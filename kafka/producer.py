#!../.venv/Scripts/python

# import os
# from random import choice
# from dotenv import load_dotenv
# from confluent_kafka import Producer

import os
import sys
import cv2
import base64
from dotenv import load_dotenv
from confluent_kafka import Producer
import time

if __name__ == '__main__':
    
    load_dotenv()

    config = {
        # User-specific properties that you must set
        'bootstrap.servers': os.getenv('BOOTSTRAP_SERVERS'),
        'sasl.username':     os.getenv('CLUSTER_API_KEY'),
        'sasl.password':     os.getenv('CLUSTER_API_SECRET'),

        # Fixed properties
        'security.protocol': 'SASL_SSL',
        'sasl.mechanisms':   'PLAIN',
        'acks':              '1',  # Wait for leader to acknowledge
        'linger.ms':         0
    }

    # Create Producer instance
    producer = Producer(config)

    # Optional per-message delivery callback
    def delivery_callback(err, msg):
        if err:
            print(f'ERROR: Message failed delivery: {err}')
        else:
            print(f"Produced event to topic {msg.topic()}")

    # Produce data by selecting random values from these lists.
    topic = "test"

    # Open a connection to the default camera (usually 0)
    cap = cv2.VideoCapture(0)
    # Set a smaller resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 640)

    if not cap.isOpened():
        print("Error: Could not open video stream.")
        sys.exit()

    try:
        while True:
            # Capture frame-by-frame
            ret, frame = cap.read()
            if not ret:
                print("Error: Can't receive frame (stream end?). Exiting ...")
                break

            # Encode frame as JPEG
            _, buffer = cv2.imencode('.jpg', frame)
            
            # Encode buffer to base64
            b64_encoded_frame = base64.b64encode(buffer)

            # Send the base64 encoded frame
            producer.produce(
                topic,
                value=b64_encoded_frame,
                callback=delivery_callback
            )
            producer.poll(0)
            # time.sleep(0.05) # Control frame rate

    except KeyboardInterrupt:
        print("Interrupted by user")
        pass
    finally:
        # Block until the messages are sent.
        print("Flushing messages...")
        producer.flush()
        # Release the camera and close all OpenCV windows
        cap.release()