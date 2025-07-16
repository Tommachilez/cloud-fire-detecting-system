export PROJECT_ID=$(gcloud config list project --format "value(core.project)")
export REPO_NAME="fire-detection-docker-repo"
export IMAGE_NAME="fire-detection-yolov8-image"
export IMAGE_TAG="demo"
export IMAGE_URI=us-central1-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/${IMAGE_NAME}:${IMAGE_TAG}

docker push ${IMAGE_URI}