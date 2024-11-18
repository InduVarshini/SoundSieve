#!/usr/bin/env python3
from flask import Flask, request, jsonify, send_file
import redis
import jsonpickle
import hashlib
import base64
import os
import io
from minio import Minio
import platform
import sys

# Environment variables for Redis and Minio configurations
REDIS_HOST = os.getenv("REDIS_HOST") or 'localhost'
REDIS_PORT = os.getenv("REDIS_PORT") or 6379
MINIO_HOST = os.getenv("MINIO_HOST") or 'localhost:9000'
MINIO_BUCKET_NAME = os.getenv("MINIO_BUCKET_NAME") or 'songs'

# Redis keys for message queue and logging
QUEUE_KEY = "toWorker"  # Queue for communication with worker service
LOGGING_KEY = "logging"  # Key for logging messages in Redis

# Keys for log categorization (node-specific)
infoKey = "{}.rest.info".format(platform.node())
debugKey = "{}.rest.debug".format(platform.node())

# Initialize Flask app
app = Flask(__name__)

# Initialize Redis and Minio clients
redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0)
minio_client = Minio(MINIO_HOST, access_key='rootuser', secret_key='rootpass123', secure=False)

# Function to log debug messages to Redis
def log_debug(message, key=debugKey):
    print("DEBUG:", message, file=sys.stdout)
    try:
        redis_client.lpush(LOGGING_KEY, f"{key}:{message}")
    except Exception as e:
        print(f"Error logging debug message: {e}", file=sys.stderr)

# Function to log info messages to Redis
def log_info(message, key=infoKey):
    print("INFO:", message, file=sys.stdout)
    try:
        redis_client.lpush(LOGGING_KEY, f"{key}:{message}")
    except Exception as e:
        print(f"Error logging info message: {e}", file=sys.stderr)

# Function to generate a SHA-256 hash for unique identification
def generate_hash(data):
    return hashlib.sha256(data.encode()).hexdigest()

# Endpoint to handle song separation requests
@app.route('/apiv1/separate', methods=['POST'])
def separate():
    data = request.json
    song_name = data.get("song_name")
    log_info(f"Received request for: {song_name}")

    # Decode the base64-encoded MP3 data
    mp3_data_base64 = data.get("mp3")
    mp3_binary_data = base64.b64decode(mp3_data_base64)
    callback_url = data.get("callback")['url']

    # Generate a unique hash for the song
    songhash = generate_hash(mp3_data_base64)
    log_debug(f"Hash generated for {song_name}: {songhash}")

    task_data = {
        "songhash": songhash,
        "callback": callback_url
    }

    # Ensure the Minio bucket exists
    if not minio_client.bucket_exists(MINIO_BUCKET_NAME):
        log_info(f"Creating bucket: {MINIO_BUCKET_NAME}")
        minio_client.make_bucket(MINIO_BUCKET_NAME)
    else:
        log_info(f"Bucket {MINIO_BUCKET_NAME} already exists")

    # Upload the original song to Minio
    try:
        minio_client.put_object(
            bucket_name=MINIO_BUCKET_NAME,
            object_name=f'{songhash}/original.mp3',
            data=io.BytesIO(mp3_binary_data),
            length=len(mp3_binary_data),
            content_type='audio/mpeg'
        )
        log_info(f"File uploaded to Minio under bucket: {MINIO_BUCKET_NAME}")
    except Exception as e:
        log_debug(f"Error uploading file to Minio: {e}")

    # Push the task to the Redis queue for worker processing
    try:
        redis_client.lpush(QUEUE_KEY, jsonpickle.encode(task_data))
        log_info("Task pushed to Redis queue")
    except Exception as e:
        log_debug(f"Error pushing task to Redis: {e}")

    return jsonify({"hash": songhash, "reason": "Song enqueued for separation"}), 200

# Endpoint to get the current task queue
@app.route('/apiv1/queue', methods=['GET'])
def queue():
    queue_items = redis_client.lrange(QUEUE_KEY, 0, -1)
    task_hashes = [jsonpickle.decode(item).get("songhash") for item in queue_items]
    return jsonify({"queue": task_hashes}), 200

# Endpoint to retrieve a separated track
@app.route('/apiv1/track/<songhash>/<track>', methods=['GET'])
def get_track(songhash, track):
    try:
        data = minio_client.get_object(MINIO_BUCKET_NAME, f"{songhash}/{track}.mp3")
        log_info(f"Retrieved track {track} for {songhash}")
    except Exception as e:
        log_debug(f"Error retrieving track: {e}")
    return send_file(io.BytesIO(data), mimetype="audio/mpeg", as_attachment=True)

# Endpoint to remove a track from Minio
@app.route('/apiv1/remove/<songhash>/<track>', methods=['DELETE'])
def remove_track(songhash, track):
    try:
        minio_client.remove_object(MINIO_BUCKET_NAME, f"{songhash}/{track}.mp3")
        log_info(f"Removed track {track} for {songhash}")
    except Exception as e:
        log_debug(f"Error removing track: {e}")

# Main entry point for the Flask app
if __name__ == '__main__':
    log_info("Starting Flask app")
    app.run(host='0.0.0.0', port=5050)
