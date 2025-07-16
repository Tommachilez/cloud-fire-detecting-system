export PROJECT_ID=$(gcloud config list project --format "value(core.project)")
export REPO_NAME="fire-detection-docker-repo"
export IMAGE_NAME="fire-detection-yolov8-image"
export IMAGE_TAG="demo"
export IMAGE_URI=us-central1-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/${IMAGE_NAME}:${IMAGE_TAG}

# run docker container to start local TorchServe deployment
docker run -t -d --rm -p 8080:8080 --name=local_fire_detection_yolov8 $IMAGE_URI
# delay to allow the model to be loaded in torchserve (takes a few seconds)
sleep 20