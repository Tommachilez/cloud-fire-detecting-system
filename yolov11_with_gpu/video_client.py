# video_client_vertexai.py
import os
import cv2
import base64
import time
from google.cloud import aiplatform
from google.protobuf import json_format
from google.protobuf.struct_pb2 import Value
from dotenv import load_dotenv

load_dotenv()

# --- Configuration ---
PROJECT_ID = os.getenv('PROJECT_ID')
LOCATION = "us-central1"
ENDPOINT_ID = os.getenv('VERTEX_AI_ENDPOINT_ID')

# Confidence threshold for drawing boxes
CONFIDENCE_THRESHOLD = 0.5
# ---------------------

# --- Choose ONE of the following video sources ---
# 1. To use a webcam
VIDEO_SOURCE = 0  # Use 0 for the default webcam

# 2. To use a video file
# VIDEO_SOURCE = "path/to/your/video.mp4"
# ---------------------

def predict_video_stream(video_source, project_id, location, endpoint_id):
    """
    Captures video from a source, sends frames to a Vertex AI endpoint,
    and displays the results.
    """
    # 1. Initialize Vertex AI Client
    # This client can be reused for multiple requests.
    api_endpoint = f"{location}-aiplatform.googleapis.com"
    client_options = {"api_endpoint": api_endpoint}
    client = aiplatform.gapic.PredictionServiceClient(client_options=client_options)
    endpoint_path = client.endpoint_path(
        project=project_id, location=location, endpoint=endpoint_id
    )

    # 2. Open Video Source
    cap = cv2.VideoCapture(video_source)
    if not cap.isOpened():
        print(f"Error: Could not open video source '{video_source}'")
        return

    print("Video source opened successfully. Starting stream...")

    while True:
        # 3. Read a frame
        ret, frame = cap.read()
        if not ret:
            print("End of video stream or cannot read frame.")
            break

        # 4. Prepare the frame for prediction
        # Encode the frame as JPEG and then to a base64 string
        _, buffer = cv2.imencode('.jpg', frame)
        encoded_content = base64.b64encode(buffer).decode("utf-8")

        # 5. Build the Vertex AI request payload
        # The format of each instance should conform to the deployed model's prediction input schema.
        instance = json_format.ParseDict({
                    "image_bytes":  {
                        "b64": encoded_content
                    }
                }, Value())
        instances = [instance]
        # You can also send parameters to the model.
        parameters = json_format.ParseDict(
            {
                "confidenceThreshold": CONFIDENCE_THRESHOLD,
                "maxPredictions": 5, # Limit the number of predictions
            },
            Value(),
        )

        try:
            # 6. Send the prediction request
            start_time = time.time()
            response = client.predict(
                endpoint=endpoint_path, instances=instances, parameters=parameters
            )
            end_time = time.time()
            print(f"Inference took: {end_time - start_time:.4f} seconds")

            # 7. Process and display the response
            frame = draw_boxes(frame, response.predictions)

        except Exception as e:
            print(f"Error sending request to Vertex AI: {e}")

        # 8. Display the resulting frame
        cv2.imshow('YOLOv8 Live Detection (Vertex AI)', frame)
        
        # ADD THIS LINE to prevent overwhelming the endpoint
        time.sleep(0.1) # Introduce a 100ms delay

        # Press 'q' to exit the loop
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release resources
    cap.release()
    cv2.destroyAllWindows()
    print("Stream finished and resources released.")


def draw_boxes(image, predictions):
    """
    Draws bounding boxes on an image based on the Vertex AI model's output.
    """
    h, w, _ = image.shape

    # The 'predictions' object is a list of protobuf Structs
    for prediction in predictions:
        prediction_dict = dict(prediction)
        
        # Extract bounding boxes, scores, and class names
        confidences = prediction.get('scores', [])
        bboxes = prediction.get('boxes', [])
        display_names = prediction.get('classes', [])

        for i, box in enumerate(bboxes):
            if confidences[i] >= CONFIDENCE_THRESHOLD:
                # Vertex AI bboxes are often in [xMin, xMax, yMin, yMax] format
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
    predict_video_stream(VIDEO_SOURCE, PROJECT_ID, LOCATION, ENDPOINT_ID)