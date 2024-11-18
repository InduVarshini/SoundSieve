import os
import redis
import json
import requests
from minio import Minio
import platform
import sys

# Environment variables for Redis and Minio configuration, with defaults for local development
REDIS_HOST = os.getenv("REDIS_HOST") or 'localhost'
REDIS_PORT = os.getenv("REDIS_PORT") or 6379
MINIO_HOST = os.getenv("MINIO_HOST") or 'localhost:9000'
MINIO_BUCKET_NAME = os.getenv("MINIO_BUCKET_NAME") or 'songs'

# Redis key names for the job queue and logging
QUEUE_KEY = "toWorker"  # Key for incoming job requests
LOGGING_KEY = "logging"  # Key for logging messages

# Initialize Redis and Minio clients
redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0)
minio_client = Minio(MINIO_HOST, access_key='rootuser', secret_key='rootpass123', secure=False)

# Log keys for categorizing messages based on the worker's host machine
infoKey = "{}.worker.info".format(platform.node())
debugKey = "{}.worker.debug".format(platform.node())

def log_debug(message, key=debugKey):
    """
    Log a debug message to the Redis logging queue.
    Args:
        message (str): The message to log.
        key (str): The key to categorize the log entry.
    """
    print("DEBUG:", message, file=sys.stdout)
    try:
        redis_client.lpush(LOGGING_KEY, f"{key}:{message}")
    except Exception as e:
        print(f"Error logging debug message: {e}", file=sys.stderr)

def log_info(message, key=infoKey):
    """
    Log an info message to the Redis logging queue.
    Args:
        message (str): The message to log.
        key (str): The key to categorize the log entry.
    """
    print("INFO:", message, file=sys.stdout)
    try:
        redis_client.lpush(LOGGING_KEY, f"{key}:{message}")
    except Exception as e:
        print(f"Error logging info message: {e}", file=sys.stderr)

def separate_track(songhash):
    """
    Separates the tracks of an MP3 file using DEMUCS and uploads the results to Min.io.
    Args:
        songhash (str): The unique identifier for the song being processed.
    """
    input_path = f"/tmp/{songhash}.mp3"  # Path to the input MP3 file
    output_path = f"/tmp/output/"  # Directory for DEMUCS output

    # Run DEMUCS to separate the audio tracks
    log_info(f"Running DEMUCS")
    try:
        os.system(f"python3 -m demucs.separate --out {output_path} --mp3 {input_path}")
        log_info("Track separated")
    except Exception as e:
        log_debug(f"Error running DEMUCS: {e}")

    # Upload the separated tracks to Min.io
    parts = ["vocals", "drums", "bass", "other"]
    for part in parts:
        track_path = f"/tmp/output/mdx_extra_q/{songhash}/{part}.mp3"  # Path to the separated track
        try:
            minio_client.fput_object(MINIO_BUCKET_NAME, f"{songhash}/{part}.mp3", track_path)
            log_info(f"Uploaded {part} track for {songhash} to Min.io")
        except Exception as e:
            log_debug(f"Error uploading {part} track for {songhash} to Min.io: {e}")

def worker():
    """
    Main worker loop that listens for incoming job requests, processes them, and logs results.
    """
    while True:
        # Wait for and retrieve a job request from the Redis queue
        request = redis_client.blpop(QUEUE_KEY, 0)[1]
        data = json.loads(request)  # Parse the JSON request data

        # Extract songhash and optional callback URL from the request
        songhash = data["songhash"]
        log_info(f"Request received for songhash: {songhash}")
        callback_url = data.get("callback")

        # Download the MP3 file from Min.io to a local temporary path
        try:
            minio_client.fget_object(MINIO_BUCKET_NAME, f"{songhash}/original.mp3", f"/tmp/{songhash}.mp3")
            log_info(f"Downloaded {songhash}.mp3 for processing")
        except Exception as e:
            log_debug(f"Error downloading {songhash}.mp3: {e}")
            continue

        # Process the song using DEMUCS
        separate_track(songhash)

        # Notify the optional callback URL if provided
        if callback_url:
            try:
                requests.post(callback_url, json={"hash": songhash, "status": "completed"})
                log_info(f"Callback sent to {callback_url} for {songhash}")
            except requests.RequestException as e:
                log_debug(f"Failed to send callback to {callback_url}: {e}")

if __name__ == "__main__":
    # Log the worker start message and enter the worker loop
    log_info("Worker started")
    worker()
