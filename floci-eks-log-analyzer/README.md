# Floci EKS Log Analyzer

This project runs a Python FastAPI log analyzer on a local Floci EKS cluster.

The app reads Apache logs from Floci S3 and exposes APIs to analyze traffic.

## Stack

- Python
- FastAPI
- Docker
- Kubernetes / EKS
- Floci
- S3
- ECR
- GitHub Actions

## Current Floci Resources

- S3 Bucket: `SKM-Bucket`
- S3 Object: `apache_logs`
- ECR Image: `host.docker.internal:5100/floci-eks-log-analyzer:v1`
- Kubernetes Deployment: `floci-log-analyzer`

## API Endpoints

```text
/
 /top-ips
 /top-urls
 /status-codes
 /error-ips
 /summary
'''

 ## Run Test
'''bash
