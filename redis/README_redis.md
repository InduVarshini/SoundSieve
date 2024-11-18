# Redis Database

This README provides details about the Redis database deployment included in the project. The deployment is designed for simplicity and supports basic functionality required for worker nodes to interact with the database.

## Overview

The Redis database is deployed as a single-pod deployment with a corresponding Kubernetes service named `redis`. This service allows worker nodes to discover the Redis instance using its DNS name (`redis`). 

The deployment utilizes the official Redis image provided by the Redis developers:  
[Redis Docker Image on Docker Hub](https://hub.docker.com/_/redis)

### Key Features

- **Automatic Table Creation**: No need to manually create tables; the database schema is automatically initialized as you start using it. Refer to the instructions in [`worker/README-worker.md`](worker/README-worker.md).
- **Simple Deployment**: Designed for ease of use and rapid prototyping.
- **Ephemeral Storage**: The deployment does not include persistent storage by default, meaning data will be lost if the Redis pod is deleted.


## Deployment Notes

1. **Single Pod Deployment**: The Redis database runs as a single pod, simplifying setup and reducing overhead.
2. **DNS-based Service Discovery**: Worker nodes can connect to the Redis database using the DNS name `redis`.


## Important Considerations

### Data Persistence

By default, this deployment does **not** use persistent storage. If the Redis pod is deleted, the database and all its data will be lost. This is intentional to keep the deployment simple and facilitate development.

If you require persistent data, consider creating a Persistent Volume (PV) and a Persistent Volume Claim (PVC) in Kubernetes. Refer to the [Kubernetes Persistent Volumes documentation](https://cloud.google.com/kubernetes-engine/docs/concepts/persistent-volumes) for guidance.

### Benefits of Ephemeral Storage During Development

Using ephemeral storage can be advantageous during development since you can easily clear all data by deleting the Redis pod. This can help reset the environment without manual intervention.


## Why Redis?

Redis is used in this project because it offers simplicity and efficiency for the intended use case. While it may not be the best choice for every scenario, it is sufficient for this project’s needs. 

If persistent data is not critical for your workflow, this lightweight Redis deployment should meet your requirements.


## Additional Resources

- [Redis Official Docker Image](https://hub.docker.com/_/redis)
- [Kubernetes Persistent Volumes Documentation](https://cloud.google.com/kubernetes-engine/docs/concepts/persistent-volumes)

