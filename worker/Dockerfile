# Use the existing DEMUCS Docker image as the base
FROM xserrat/facebook-demucs:latest

# Install dependencies for Min.io client and Redis
RUN pip install minio redis requests urllib3

# Copy worker code into the container
COPY worker.py /worker.py

# Define the command to run the worker - OVERRIDE THE Demucs IMAGE'S ENTRYPOINT
ENTRYPOINT ["python3", "/worker.py"]
