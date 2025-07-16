PROJECT_ID=$(gcloud config list project --format "value(core.project)")
REPO_NAME="fire-detection-docker-repo"
IMAGE_NAME="fire-detection-yolov11-image"
IMAGE_TAG="demo"
IMAGE_URI=us-central1-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/${IMAGE_NAME}:${IMAGE_TAG}

docker build -f Dockerfile -t ${IMAGE_URI} ./