# Floci EKS Log Analyzer

A complete local cloud DevOps project that runs a Python FastAPI log analyzer on a local Floci EKS cluster.

The application reads Apache log data from Floci S3, analyzes traffic patterns, and exposes API endpoints for finding noisy IPs, most requested URLs, HTTP status code counts, and error-heavy clients.

This project is designed to practice AWS-style development locally without using a real AWS account or spending cloud credits.

---

## Project Overview

This project demonstrates a local AWS-style CI/CD workflow using Floci.

The application is containerized with Docker, pushed to Floci ECR, deployed on Floci EKS, and reads log files from Floci S3.

### What this project does

* Reads Apache logs from S3
* Parses log lines using Python regex
* Exposes FastAPI endpoints for log analysis
* Runs inside Kubernetes on Floci EKS
* Uses Floci ECR as a local container registry
* Includes automated tests with Pytest
* Includes GitHub Actions CI workflow

---

## Architecture

```text
GitHub Repository
        |
        v
GitHub Actions CI
        |
        v
Python Tests
        |
        v
Docker Image Build
        |
        v
Floci ECR
        |
        v
Floci EKS
        |
        v
FastAPI Log Analyzer
        |
        v
Floci S3 Bucket: SKM-Bucket
        |
        v
apache_logs
```

---

## Tech Stack

* Python
* FastAPI
* Pytest
* Docker
* Kubernetes
* Floci
* Local EKS
* Local S3
* Local ECR
* GitHub Actions

---

## Features

The API provides the following endpoints:

| Endpoint        | Description                                    |
| --------------- | ---------------------------------------------- |
| `/`             | Health/basic app information                   |
| `/top-ips`      | Shows the most frequently appearing client IPs |
| `/top-urls`     | Shows the most requested URLs                  |
| `/status-codes` | Shows count of HTTP status codes               |
| `/error-ips`    | Shows IPs generating 4xx/5xx responses         |
| `/summary`      | Shows overall log summary                      |

---

## Project Structure

```text
floci-eks-log-analyzer/
├── app/
│   ├── __init__.py
│   └── main.py
├── tests/
│   └── test_main.py
├── k8s/
│   ├── deployment.yaml
│   └── service.yaml
├── .github/
│   └── workflows/
│       └── ci.yaml
├── Dockerfile
├── requirements.txt
├── pytest.ini
├── .dockerignore
├── .gitignore
└── README.md
```

---

## Prerequisites

Install the following tools on your local machine:

* Docker Desktop
* Python 3.11+
* AWS CLI
* kubectl
* Floci
* Git
* GitHub CLI, optional

You should also have:

* Floci running locally
* Floci EKS cluster running
* Floci S3 bucket created
* Apache log file uploaded to S3

Current project setup:

```text
S3 Bucket: SKM-Bucket
S3 Object Key: apache_logs
ECR Repository: floci-eks-log-analyzer
Kubernetes Deployment: floci-log-analyzer
Kubernetes Service: floci-log-analyzer
```

---

## Configure Local Floci AWS Environment

```bash
export AWS_ENDPOINT_URL=http://localhost:4566
export AWS_DEFAULT_REGION=us-east-1
export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
```

Verify S3 bucket and log file:

```bash
aws s3 ls
aws s3 ls s3://SKM-Bucket
```

Expected file:

```text
apache_logs
```

---

## Run the App Locally

Create a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run tests:

```bash
python -m pytest -v
```

Start FastAPI locally:

```bash
uvicorn app.main:app --reload --port 8000
```

Test:

```bash
curl http://localhost:8000/
curl -s http://localhost:8000/summary | python3 -m json.tool
```

---

## Build Docker Image

```bash
docker build -t floci-eks-log-analyzer:local .
```

Run container locally:

```bash
docker run --rm -p 8000:8000 \
  -e S3_BUCKET=SKM-Bucket \
  -e S3_KEY=apache_logs \
  -e S3_ENDPOINT_URL=http://host.docker.internal:4566 \
  -e AWS_ACCESS_KEY_ID=test \
  -e AWS_SECRET_ACCESS_KEY=test \
  -e AWS_DEFAULT_REGION=us-east-1 \
  floci-eks-log-analyzer:local
```

Test from another terminal:

```bash
curl http://localhost:8000/
curl -s http://localhost:8000/top-ips | python3 -m json.tool
curl -s http://localhost:8000/summary | python3 -m json.tool
```

---

## Push Docker Image to Floci ECR

Create the ECR repository:

```bash
aws ecr create-repository \
  --repository-name floci-eks-log-analyzer \
  --endpoint-url $AWS_ENDPOINT_URL
```

Set repository URI:

```bash
REPO_URI=000000000000.dkr.ecr.us-east-1.localhost:5100/floci-eks-log-analyzer
```

Login to Floci ECR:

```bash
aws ecr get-login-password --endpoint-url $AWS_ENDPOINT_URL \
  | docker login --username AWS --password-stdin \
  000000000000.dkr.ecr.us-east-1.localhost:5100
```

Tag and push image:

```bash
docker tag floci-eks-log-analyzer:local $REPO_URI:v1
docker push $REPO_URI:v1
```

Verify the registry:

```bash
curl -s http://000000000000.dkr.ecr.us-east-1.localhost:5100/v2/_catalog | python3 -m json.tool
curl -s http://000000000000.dkr.ecr.us-east-1.localhost:5100/v2/floci-eks-log-analyzer/tags/list | python3 -m json.tool
```

---

## Important K3s Registry Fix

Since Floci ECR registry runs over HTTP locally, K3s/containerd must be configured to treat it as an insecure registry.

Set the node container ID:

```bash
NODE=16522a30f3c3
```

Create K3s registry config:

```bash
cat <<'EOF' | docker exec -i $NODE sh -c 'mkdir -p /etc/rancher/k3s && cat > /etc/rancher/k3s/registries.yaml'
mirrors:
  "host.docker.internal:5100":
    endpoint:
      - "http://host.docker.internal:5100"
EOF
```

Restart the K3s node container:

```bash
docker restart $NODE
```

Verify Kubernetes is back:

```bash
kubectl get nodes
kubectl get pods
```

---

## Deploy to Floci EKS

Apply Kubernetes manifests:

```bash
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

Check rollout:

```bash
kubectl rollout status deployment/floci-log-analyzer
kubectl get pods
```

Check logs:

```bash
kubectl logs deploy/floci-log-analyzer
```

---

## Test the Application on EKS

Port-forward the service:

```bash
kubectl port-forward svc/floci-log-analyzer 8000:8000
```

In another terminal:

```bash
curl http://localhost:8000/
curl -s http://localhost:8000/top-ips | python3 -m json.tool
curl -s http://localhost:8000/top-urls | python3 -m json.tool
curl -s http://localhost:8000/status-codes | python3 -m json.tool
curl -s http://localhost:8000/error-ips | python3 -m json.tool
curl -s http://localhost:8000/summary | python3 -m json.tool
```

---

## Example API Output

### `/`

```json
{
  "message": "Floci EKS Log Analyzer is running",
  "bucket": "SKM-Bucket",
  "key": "apache_logs"
}
```

### `/summary`

```json
{
  "total_parsed_requests": 10000,
  "top_5_ips": [
    ["83.149.9.216", 23],
    ["24.236.252.67", 18]
  ],
  "top_5_urls": [
    ["/index.html", 100],
    ["/images/logo.png", 80]
  ],
  "status_codes": {
    "200": 9000,
    "404": 700,
    "500": 300
  }
}
```

---

## GitHub Actions CI

This project includes a CI workflow that runs tests on every push and pull request.

Workflow file:

```text
.github/workflows/ci.yaml
```

The CI pipeline performs:

```text
Checkout code
Set up Python
Install dependencies
Run Pytest
```

---

## Useful Commands

Check all Kubernetes resources:

```bash
kubectl get all
```

Describe pod:

```bash
kubectl describe pod -l app=floci-log-analyzer
```

Restart deployment:

```bash
kubectl rollout restart deployment/floci-log-analyzer
```

Delete deployment and service:

```bash
kubectl delete -f k8s/deployment.yaml
kubectl delete -f k8s/service.yaml
```

Check S3 file:

```bash
aws s3 ls s3://SKM-Bucket
aws s3 cp s3://SKM-Bucket/apache_logs - | head -5
```

---

## Learning Outcomes

By building this project, you practice:

* Python log parsing
* Regex
* Counter and dictionary-based frequency analysis
* FastAPI development
* Unit testing with Pytest
* Docker image building
* Kubernetes Deployment and Service
* Local AWS-style S3 usage
* Local AWS-style ECR usage
* EKS-style deployment using Floci
* GitHub Actions CI
* End-to-end DevOps workflow

---

## Future Improvements

Possible next features:

* Add `/top-methods` endpoint
* Add `/largest-responses` endpoint
* Add `/filter-by-status/{status_code}` endpoint
* Add HTML dashboard
* Add Prometheus metrics
* Add Kubernetes HPA
* Add self-hosted GitHub Actions runner for full local CD
* Add automatic Docker build and deploy workflow
* Add Helm chart
* Add Ingress controller

---

## Author

Built by Sandeep Kumar as a local AWS/EKS/DevOps learning project using Floci.
"