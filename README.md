# SoundSieve: Music-Separation-as-a-Service (MSaaS)  

SoundSieve harnesses AI-powered source separation through Demucs to precisely isolate vocals and instruments from audio tracks. Building on techniques used by Spotify and Apple Music, it delivers enterprise-grade audio processing through a scalable, Kubernetes architecture. This enables streaming services, music production studios, and digital platforms to offer enhanced experiences like professional-quality karaoke, remixing tools, and interactive music features. By bringing advanced audio manipulation to the cloud, SoundSieve equips businesses to meet rising demand for AI-driven audio innovation.


![Music Separation](https://tjzk.replicate.delivery/models_models_cover_image/3fc4bbf8-1d4b-45d8-bd3f-262409a73e23/source_separation_io.png)  


This repository implements **Music-Separation-as-a-Service (MSaaS)**, a Kubernetes-based system for waveform source separation. MSaaS provides a REST API for automatic music separation, enabling users to upload MP3 files, process them into separate tracks (vocals, bass, drums, etc.), and retrieve the results.  

## Overview  

The project leverages Kubernetes to deploy and manage a microservices architecture that includes:  

- **REST API service (`rest`)**: Handles API requests for music analysis and communicates with workers via a Redis queue.  
- **Worker service (`worker`)**: Processes MP3 files using [Facebook's Demucs](https://github.com/facebookresearch/demucs), a waveform source separation tool, and stores results in Min.io object storage.  
- **Redis service (`redis`)**: Provides a lightweight database for queuing work requests and logging messages.  

The system relies on **Min.io** for object storage to store uploaded MP3 files and output tracks.  


## Architecture  

The MSaaS system comprises the following components:  

1. **Redis**: Handles the queuing of tasks and logging via `lpush`/`blpop` operations.  
2. **REST API (`rest`)**: Provides endpoints for uploading MP3 files, initiating music separation, and retrieving results.  
3. **Worker**: Executes the computationally expensive music separation tasks using Demucs.  
4. **Min.io**: Stores MP3 files and separated tracks in "queue" and "output" buckets.  

Below is architecture/data flow diagram:
![MSaaS](https://github.com/InduVarshini/SoundSieve/blob/main/SoundSeive_ArchDiagram.png)  

## Prerequisites  

Before starting, ensure you have the following:  

1. **Kubernetes Cluster**: You can use a local Kubernetes installation or a cloud provider like GKE. For local development, Minikube or Docker Desktop is recommended.  
2. **Min.io**: Set up Min.io locally or as a Kubernetes service using the [Kubernetes tutorial instructions](https://github.com/cu-csci-4253-datacenter/kubernetes-tutorial/tree/master/06-minio).  
3. **Redis**: Deployed via Kubernetes as a service.  
4. **Docker**: Installed locally to build and manage container images.  
5. **Python 3.8+**: For running test scripts and interacting with the REST API.  


## Deployment  

### 1. Clone Repository  
```bash  
git clone https://github.com/InduVarshini/SoundSieve.git
cd SoundSieve  
```  

### 2. Set Up Min.io  
Deploy Min.io locally or on Kubernetes by following the [Min.io Kubernetes tutorial](https://github.com/cu-csci-4253-datacenter/kubernetes-tutorial/tree/master/06-minio). Ensure Min.io is accessible and credentials are correctly configured.  

### 3. Deploy Redis  
Run the provided script to deploy Redis:  
```bash  
bash deploy-local-dev.sh  
```  

This also sets up port-forwarding to allow local access to Redis and Min.io services.  

### 4. Build and Push Docker Images  
Build Docker images for `rest` and `worker`:  
```bash  
docker build -t your-dockerhub-user/rest:latest rest/  
docker build -t your-dockerhub-user/worker:latest worker/  
docker push your-dockerhub-user/rest:latest  
docker push your-dockerhub-user/worker:latest  
```  

### 5. Deploy Services on Kubernetes  
Deploy all services using Kubernetes manifests:  
```bash  
kubectl apply -f k8s/redis-deployment.yaml  
kubectl apply -f k8s/minio-deployment.yaml  
kubectl apply -f k8s/rest-deployment.yaml  
kubectl apply -f k8s/worker-deployment.yaml  
```  

Verify that all pods are running:  
```bash  
kubectl get pods  
```  

### 6. Port Forwarding (Optional for Local Development)  
To enable local development, forward Redis and Min.io ports to your localhost:  
```bash  
kubectl port-forward service/redis 6379:6379 &  
kubectl port-forward --namespace minio-ns svc/myminio-proj 9000:9000 &  
```  


## Testing the System  

### 1. REST API Endpoints  
The REST API accepts requests for:  
- **Uploading MP3s**  
- **Processing MP3s**  
- **Retrieving separated tracks**  

Refer to [rest/README.md](rest/README.md) for endpoint documentation.  

### 2. Sample Data  
Run the provided sample scripts to test the system:  
```bash  
python sample-requests.py  
python short-sample-requests.py  
```  

### 3. Logs  
Monitor logs using the logging service provided in the `logs/` directory. Deploy the `logs` service on Kubernetes or run it locally to view debug messages from the Redis logging queue.  


## Development Workflow  

1. **Redis Deployment**: Use `deploy-local-dev.sh` to deploy Redis with port-forwarding enabled.  
2. **REST Server**: Develop and test the REST API locally by connecting to Redis and Min.io via `localhost`.  
3. **Worker Node**: Test the worker service locally by connecting to the port-forwarded Redis queue and Min.io.  
4. **Debugging**: Use the logging pod to debug issues during development.  


## Tips for Development  

- Use **short sample MP3 files** during development to reduce processing time and memory usage.  
- Monitor Kubernetes resource usage with:  
  ```bash  
  kubectl describe node <node-name>  
  ```  
- Use **versioned Docker images** for better deployment tracking.  

## Resources  

- [Kubernetes Cheat Sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)  
- [Demucs: Waveform Source Separation](https://github.com/facebookresearch/demucs)  
- [Min.io Python API](https://min.io/docs/minio/linux/developers/python/API.html)  
- [CSCI 4253/5253 Kubernetes Tutorial](https://github.com/cu-csci-4253-datacenter/kubernetes-tutorial)  


## License  

This project is licensed under the MIT License. See the LICENSE file for details.  
