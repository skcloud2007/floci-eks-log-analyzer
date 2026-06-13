APP_NAME=floci-log-analyzer
IMAGE_NAME=floci-eks-log-analyzer
IMAGE_TAG?=v2

AWS_ENDPOINT_URL=http://localhost:4566
ECR_REGISTRY=000000000000.dkr.ecr.us-east-1.localhost:5100
ECR_URI=$(ECR_REGISTRY)/$(IMAGE_NAME)
K8S_IMAGE=host.docker.internal:5100/$(IMAGE_NAME):$(IMAGE_TAG)

.PHONY: help test build run-local ecr-login push deploy restart pods logs port-forward clean

help:
	@echo "Available commands:"
	@echo "  make test          - Run Python tests"
	@echo "  make build         - Build Docker image"
	@echo "  make run-local     - Run app locally using Docker"
	@echo "  make ecr-login     - Login to Floci ECR"
	@echo "  make push          - Push Docker image to Floci ECR"
	@echo "  make deploy        - Deploy app to Floci EKS"
	@echo "  make restart       - Restart Kubernetes deployment"
	@echo "  make pods          - Show Kubernetes pods"
	@echo "  make logs          - Show app logs"
	@echo "  make port-forward  - Port-forward app to localhost:8000"
	@echo "  make clean         - Delete Kubernetes deployment and service"

test:
	python -m pytest -v

build:
	docker build -t $(IMAGE_NAME):local .

run-local:
	docker run --rm -p 8000:8000 \
		-e S3_BUCKET=SKM-Bucket \
		-e S3_KEY=apache_logs \
		-e S3_ENDPOINT_URL=http://host.docker.internal:4566 \
		-e AWS_ACCESS_KEY_ID=test \
		-e AWS_SECRET_ACCESS_KEY=test \
		-e AWS_DEFAULT_REGION=us-east-1 \
		$(IMAGE_NAME):local

ecr-login:
	aws ecr get-login-password --endpoint-url $(AWS_ENDPOINT_URL) | docker login --username AWS --password-stdin $(ECR_REGISTRY)

push: ecr-login
	docker tag $(IMAGE_NAME):local $(ECR_URI):$(IMAGE_TAG)
	docker push $(ECR_URI):$(IMAGE_TAG)

deploy:
	kubectl apply -f k8s/configmap.yaml
	kubectl apply -f k8s/service.yaml
	kubectl apply -f k8s/deployment.yaml
	kubectl set image deployment/$(APP_NAME) $(APP_NAME)=$(K8S_IMAGE)
	kubectl rollout status deployment/$(APP_NAME)

restart:
	kubectl rollout restart deployment/$(APP_NAME)
	kubectl rollout status deployment/$(APP_NAME)

pods:
	kubectl get pods
	kubectl get svc

logs:
	kubectl logs deploy/$(APP_NAME)

port-forward:
	kubectl port-forward svc/$(APP_NAME) 8000:8000

clean:
	kubectl delete -f k8s/deployment.yaml --ignore-not-found=true
	kubectl delete -f k8s/service.yaml --ignore-not-found=true
