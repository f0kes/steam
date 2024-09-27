IMAGE_NAME="steam-collector:latest"
CONTAINER_NAME="steam-collector"



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
sudo docker run -d -e DB_HOST=172.17.0.3 -e TZ=Europe/Sofia --name $CONTAINER_NAME $IMAGE_NAME

# if exists, echo success message
if [ "$(sudo docker ps -q -f name=$CONTAINER_NAME)" ]; then
    echo "Docker container started successfully!"
fi