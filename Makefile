AWS_REGION    := us-east-1
AWS_ACCOUNT   := 573979277529
ECR_REPO      := modelship
IMAGE_TAG     := $(shell git rev-parse --short HEAD)
ECR_URI       := $(AWS_ACCOUNT).dkr.ecr.$(AWS_REGION).amazonaws.com/$(ECR_REPO)

.PHONY: help lint test build run push deploy

help:
	@echo "Usage: make <target>"
	@echo ""
	@echo "  lint    Run ruff linter"
	@echo "  test    Run pytest"
	@echo "  build   Build Docker image (tag: git SHA)"
	@echo "  run     Start full stack via docker-compose"
	@echo "  push    Build and push image to ECR"
	@echo "  deploy  Rolling update on EKS (requires kubectl context)"

lint:
	ruff check src/ tests/

test:
	pytest tests/ -v

build:
	docker build -t $(ECR_URI):$(IMAGE_TAG) -t $(ECR_URI):latest -f docker/Dockerfile .

run:
	docker-compose up

push: build
	aws ecr get-login-password --region $(AWS_REGION) | \
		docker login --username AWS --password-stdin $(AWS_ACCOUNT).dkr.ecr.$(AWS_REGION).amazonaws.com
	docker push $(ECR_URI):$(IMAGE_TAG)
	docker push $(ECR_URI):latest
	@echo "Pushed → $(ECR_URI):$(IMAGE_TAG)"

deploy:
	kubectl set image deployment/modelship-deployment \
		modelship-api=$(ECR_URI):$(IMAGE_TAG)
	kubectl rollout status deployment/modelship-deployment
