FROM pytorch/torchserve:latest-gpu

# install dependencies
RUN pip install ultralytics

# copy model artifacts, custom handler and other dependencies
COPY ./handler_11.py /home/model-server/
COPY ./yolo11n.pt /home/model-server/

# create torchserve configuration file
USER root
RUN printf "\nservice_envelope=json" >> /home/model-server/config.properties
RUN printf "\ninference_address=http://0.0.0.0:8080" >> /home/model-server/config.properties
RUN printf "\nmanagement_address=http://0.0.0.0:8081" >> /home/model-server/config.properties
RUN printf "\ndisable_token_authorization=true" >> /home/model-server/config.properties
USER model-server

# expose health and prediction listener ports from the image
EXPOSE 8080
EXPOSE 8081

# create model archive file packaging model artifacts and dependencies
RUN torch-model-archiver -f \
  --model-name="yolov11" \
  --version=1.0 \
  --serialized-file=/home/model-server/yolo11n.pt \
  --handler=/home/model-server/handler_11.py \
  --export-path=/home/model-server/model-store

# run Torchserve HTTP serve to respond to prediction requests
CMD ["torchserve", \
     "--start", \
     "--ts-config=/home/model-server/config.properties", \
     "--models", \
     "yolov11=yolov11.mar", \
     "--model-store", \
     "/home/model-server/model-store"]