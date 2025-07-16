# video_client_local.py
import cv2
import base64
import time
import requests # Use requests library for HTTP calls
import json

# --- Configuration ---
# URL for the local Docker container's prediction endpoint
ENDPOINT_URL = "http://localhost:8080/predictions/yolov11"

# Confidence threshold for drawing boxes
CONFIDENCE_THRESHOLD = 0.5
# ---------------------

# --- Choose ONE of the following video sources ---
# 1. To use a webcam
VIDEO_SOURCE = 0  # Use 0 for the default webcam

# 2. To use a video file
# VIDEO_SOURCE = "path/to/your/video.mp4"
# ---------------------

def predict_video_stream(video_source, endpoint_url):
    """
    Captures video from a source, sends frames to a local prediction server,
    and displays the results.
    """
    # 1. Open Video Source
    cap = cv2.VideoCapture(video_source)
    if not cap.isOpened():
        print(f"Error: Could not open video source '{video_source}'")
        return

    print("Video source opened successfully. Starting stream...")

    while True:
        # 2. Read a frame
        ret, frame = cap.read()
        if not ret:
            print("End of video stream or cannot read frame.")
            break

        # 3. Prepare the frame for prediction
        # Encode the frame as JPEG and then to a base64 string
        _, buffer = cv2.imencode('.jpg', frame)
        encoded_content = base64.b64encode(buffer).decode("utf-8")

        # 4. Build the request payload
        # This structure matches the one used in your curl command.
        payload = {
            "instances": [
                {
                    "image_bytes":  {
                        "b64": encoded_content
                    }
                }
            ],
            "parameters": {
                "confidenceThreshold": CONFIDENCE_THRESHOLD,
                "maxPredictions": 5,
            }
        }
        headers = {"Content-Type": "application/json"}


        try:
            # 5. Send the prediction request to the local server
            start_time = time.time()
            response = requests.post(endpoint_url, data=json.dumps(payload), headers=headers)
            response.raise_for_status() # Raise an exception for bad status codes
            end_time = time.time()
            print(f"Inference took: {end_time - start_time:.4f} seconds")

            # 6. Process and display the response
            predictions = response.json().get('predictions', [])
            frame = draw_boxes(frame, predictions)

        except requests.exceptions.RequestException as e:
            print(f"Error sending request to local server: {e}")

        # 7. Display the resulting frame
        cv2.imshow('YOLOv8 Live Detection (Local Docker)', frame)
        
        # Press 'q' to exit the loop
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release resources
    cap.release()
    cv2.destroyAllWindows()
    print("Stream finished and resources released.")


def draw_boxes(image, predictions):
    """
    Draws bounding boxes on an image based on the local model's output.
    """
    h, w, _ = image.shape

    for prediction in predictions:
        # The exact keys depend on your model's output signature.
        # Adjust these if your local model's output schema is different.
        confidences = prediction.get('scores', [])
        bboxes = prediction.get('boxes', [])
        display_names = prediction.get('classes', [])

        for i, box in enumerate(bboxes):
            if confidences[i] >= CONFIDENCE_THRESHOLD:
                # Assuming bboxes are in [xMin, xMax, yMin, yMax] format
                # and normalized to [0, 1].
                x1, x2, y1, y2 = box
                start_point = (int(x1 * w), int(y1 * h))
                end_point = (int(x2 * w), int(y2 * h))
                
                # Draw rectangle and label
                cv2.rectangle(image, start_point, end_point, (0, 255, 0), 2)
                label = f"{display_names[i]}: {confidences[i]:.2f}"
                cv2.putText(image, label, (start_point[0], start_point[1] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    return image


if __name__ == "__main__":
    predict_video_stream(VIDEO_SOURCE, ENDPOINT_URL)