PROJECT_ID=$(gcloud config list project --format "value(core.project)")
REPO_NAME="fire-detection-docker-repo"
IMAGE_NAME="fire-detection-yolov11-image"
IMAGE_TAG="demo"
IMAGE_URI=us-central1-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/${IMAGE_NAME}:${IMAGE_TAG}

# run docker container to start local TorchServe deployment
docker run -t -d --rm -p 8080:8080 --name=local_fire_detection_yolov11 $IMAGE_URI
# delay to allow the model to be loaded in torchserve (takes a few seconds)
sleep 20