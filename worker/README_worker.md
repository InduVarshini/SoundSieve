# Waveform Separation Worker

This worker handles the task of separating audio tracks (e.g., vocals, bass, drums, etc.) from MP3 songs using the [Facebook DEMUCS](https://github.com/facebookresearch/demucs/blob/main/demucs/separate.py) waveform separation software. The workflow involves receiving requests, processing songs, and storing the results in a Min.io object storage system.

## Overview of Worker Responsibilities

1. **Listening for Job Requests**  
   The worker listens to a Redis queue (`toWorkers` key) for incoming requests. Each request contains the necessary details to retrieve and process an MP3 song.

2. **Downloading MP3 Songs**  
   Rather than passing large MP3 files through Redis, the worker retrieves song files from a Min.io object storage system. 

3. **Waveform Separation**  
   The worker uses the DEMUCS software to perform music source separation. This splits the audio into individual components, such as vocals, bass, drums, and others.

4. **Storing Results**  
   Once the separation is complete, the resulting audio files are uploaded back to the Min.io object storage system.

5. **Webhook Callbacks (Optional)**  
   If specified in the request, the worker sends an HTTP POST request to a webhook callback URL with a payload indicating the status or results of the process. Failures in the callback do not require retry logic but should be logged.

## File Structure

worker/

├── Dockerfile       # Dockerfile for building the worker server image.
├── Makefile         # Automates build, test, and deploy processes.
├── worker.py   # Main WORKER server application code.
├── worker-deployment.yaml # Kubernetes deployment configuration.


## Setting Up the Worker Environment

To implement the worker:

1. **Redis for Communication**  
   - Use Redis to handle the queue for job requests (`toWorkers`) and for logging (`logging`).  
   - The worker reads requests in JSON format from the Redis queue.

2. **Min.io for Storage**  
   - Store the original MP3 files and the separated output tracks in Min.io.  
   - Use the `fput_object` interface to upload files to the appropriate bucket after processing.

3. **DEMUCS for Separation**  
   - Install and use the [DEMUCS Docker image](https://github.com/xserrat/docker-facebook-demucs).  
   - Run DEMUCS as a separate program using `os.system(...)` in Python, ensuring the outputs are correctly saved in the specified directories.

## Workflow Example

1. **Receive Job**  
   The worker receives a job request from the `toWorkers` Redis key. The request includes:  
   - A reference to the MP3 file stored in Min.io.  
   - Optional webhook details for callback after processing.

2. **Process Song**  
   - Retrieve the MP3 file from Min.io using its reference.  
   - Run DEMUCS to separate the audio into components.  
   - Store the separated audio tracks back in Min.io, using a unique identifier for organization.

3. **Callback and Logging**  
   - If a webhook is provided, send an HTTP POST request with the results payload.  
   - Log the process status in the `logging` Redis key.

## Development and Deployment Instructions

### Local Development

1. **Install DEMUCS Docker Image**  
   Use the [pre-existing Docker image](https://github.com/xserrat/docker-facebook-demucs) as the base.

2. **Deploy Redis and Min.io**  
   - Use the provided `deploy-local-dev.sh` script to deploy Redis and Min.io locally.  
   - Use `kubectl port-forward` to expose these services on your localhost.

3. **Run the Worker Locally**  
   With services running locally, execute `worker.py` to process requests.

4. **Sample Request**  
   Create a program to send a sample request to the worker for testing purposes. The request should include:
   - The MP3 file reference in Min.io.
   - Optional webhook details.

### Deployment in Kubernetes

1. **Update Worker Configuration**  
   - Configure the worker to use environment variables for Redis and Min.io host details during deployment.

2. **Build and Deploy Docker Image**  
   - Extend the [DEMUCS Docker image](https://github.com/xserrat/docker-facebook-demucs) with your server code.
   - Deploy the updated image in your Kubernetes cluster.

## Output Handling

The DEMUCS software outputs separated tracks into a directory with the structure:  
`/tmp/output/mdx_extra_q/{songhash}/{part}.mp3`  
Where `{songhash}` is a unique identifier for the song and `{part}` is one of `bass`, `drums`, `vocals`, or `other`.  

The worker uploads these files to Min.io for access by downstream systems or clients.
