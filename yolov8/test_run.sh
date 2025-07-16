curl -s -X POST \
  -H "Content-Type: application/json; charset=utf-8" \
  -d @./payload.json \
  http://localhost:8080/predictions/yolov8/