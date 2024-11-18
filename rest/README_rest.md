# REST Server for Song Separation API

This REST server facilitates the separation of audio tracks (e.g., vocals, bass, drums, etc.) from MP3 songs through a distributed system. The server handles API requests, queues tasks for processing, and interfaces with storage and logging systems to manage the workflow.

## Overview of Server Responsibilities

1. **Handling Client Requests**  
   The REST server exposes several API endpoints to:
   - Upload songs for separation.
   - Retrieve processing queue status.
   - Access separated tracks.
   - Remove tracks from the storage.

2. **Task Queuing with Redis**  
   - Tasks for song separation are added to a Redis queue (`toWorker` key) for processing by downstream workers.
   - Logging messages are pushed to a Redis logging queue (`logging` key).

3. **Storing Songs and Tracks in Min.io**  
   - Original songs and separated tracks are stored in a Min.io object storage system under a bucket (`songs`).
   - Each file is organized by a unique hash identifier.

4. **Logging and Debugging**  
   - Logs important events and errors into a Redis logging key, providing visibility into the system's status.

## File Structure

rest/
├── Dockerfile       # Dockerfile for building the REST server image.
├── Makefile         # Automates build, test, and deploy processes.
├── rest-server.py   # Main REST server application code.
├── rest-ingress.yaml     # Kubernetes ingress configuration.
├── rest-service.yaml     # Kubernetes service configuration.
├── rest-deployment.yaml # Kubernetes deployment configuration.


## API Endpoints

### 1. **POST `/apiv1/separate`**
   - **Description**: Accepts a song file for processing and queues it for separation.
   - **Request Body** (JSON):
     ```json
     {
       "song_name": "example.mp3",
       "mp3": "Base64-encoded-MP3-data",
       "callback": {
         "url": "http://example.com/callback"
       }
     }
     ```
   - **Response** (JSON):
     ```json
     {
       "hash": "unique-song-hash",
       "reason": "Song enqueued for separation"
     }
     ```
   - **Processing Steps**:
     - Decode and store the MP3 file in Min.io under the unique hash.
     - Queue the song details in Redis for processing by workers.

### 2. **GET `/apiv1/queue`**
   - **Description**: Retrieves the list of song hashes currently in the processing queue.
   - **Response** (JSON):
     ```json
     {
       "queue": ["hash1", "hash2", "hash3"]
     }
     ```

### 3. **GET `/apiv1/track/<songhash>/<track>`**
   - **Description**: Retrieves a specific separated track from storage.
   - **Parameters**:
     - `songhash`: Unique identifier for the song.
     - `track`: Name of the track (e.g., `vocals`, `bass`, `drums`, `other`).
   - **Response**: Returns the track as an MP3 file.

### 4. **DELETE `/apiv1/remove/<songhash>/<track>`**
   - **Description**: Deletes a specific separated track from storage.
   - **Parameters**:
     - `songhash`: Unique identifier for the song.
     - `track`: Name of the track to be deleted.
   - **Response**: Confirmation of deletion.


## Workflow Example

1. **Client Upload**: A client sends a POST request to `/apiv1/separate` with the MP3 file and callback URL.
2. **Task Queueing**: The REST server:
   - Stores the MP3 file in Min.io.
   - Queues the task in Redis with a unique hash.
3. **Track Retrieval**: Once processed, separated tracks can be retrieved via the `/apiv1/track/<songhash>/<track>` endpoint.

## Future Enhancements

- Add authentication for API endpoints.
- Implement retry logic for failed webhook callbacks.
- Support additional audio formats beyond MP3.