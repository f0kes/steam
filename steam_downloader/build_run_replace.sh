#!/bin/bash

# Define variables
IMAGE_NAME="steam-collector:latest"
CONTAINER_NAME="steam-collector"


# Build Docker image
echo "Building Docker image..."
sudo docker build -t $IMAGE_NAME .

# Check if container with the same name is already running
if [ "$(sudo docker ps -q -f name=$CONTAINER_NAME)" ]; then
    echo "Stopping existing container..."
    sudo docker stop $CONTAINER_NAME
fi

# Remove existing container if it exists
if [ "$(sudo docker ps -a -q -f name=$CONTAINER_NAME)" ]; then
    echo "Removing existing container..."
    sudo docker rm $CONTAINER_NAME
fi

# Run Docker container
echo "Starting Docker container..."
echo "Starting Docker container..." && sudo docker run -d -e POSTGRES_HOST=172.17.0.5 -e REDIS_HOST=172.17.0.4 -e TZ=Europe/Sofia -e MODE=time --name $CONTAINER_NAME $IMAGE_NAME


# if exists, echo success message
if [ "$(sudo docker ps -q -f name=$CONTAINER_NAME)" ]; then
    echo "Docker container started successfully!"
fi
