# Min.io Deployment README

This README provides instructions for setting up and using a local deployment of [Min.io](http://min.io) for object storage. Min.io provides a lightweight alternative to Google Cloud Storage or Amazon S3, making it ideal for standalone environments.

## Overview

Min.io is deployed locally using the steps provided in the [Kubernetes tutorial](https://github.com/cu-csci-4253-datacenter/kubernetes-tutorial/tree/master/06-minio). This setup enables standalone object storage accessible via an `ExternalName` service, allowing applications to reference Min.io using the hostname `minio`.


## Deployment Instructions

To deploy Min.io locally:

1. Follow the [Kubernetes tutorial for Min.io setup](https://github.com/cu-csci-4253-datacenter/kubernetes-tutorial/tree/master/06-minio).
2. Configure an `ExternalName` service to simplify service discovery. This allows your applications to use the hostname `minio` when interacting with the object store.


## Provided Resources

This deployment includes:

- **Min.io Specification**: A predefined configuration copied from the [Kubernetes tutorial](https://github.com/cu-csci-4253-datacenter/kubernetes-tutorial/tree/master/06-minio).
- **Helm Configuration File**: Used to deploy and manage the Min.io instance.

If you make modifications to these configurations, ensure they are documented here to keep the setup reproducible and transparent.


## Benefits of Local Min.io Deployment

- **Standalone Environment**: Avoids the need for access to Google Cloud Storage or S3, making it suitable for local testing and development.
- **Service Discovery**: The `ExternalName` service ensures seamless application connectivity using the hostname `minio`.


## Additional Resources

- [Min.io Documentation](https://docs.min.io/)
- [Kubernetes Min.io Tutorial](https://github.com/cu-csci-4253-datacenter/kubernetes-tutorial/tree/master/06-minio)

