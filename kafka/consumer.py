#!../.venv/Scripts/python

import os
import cv2
import base64
import numpy as np
from dotenv import load_dotenv
from confluent_kafka import Consumer

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
        'group.id':          'kafka-python-getting-started',
        'auto.offset.reset': 'earliest'
    }

    # Create Consumer instance
    consumer = Consumer(config)

    # Subscribe to topic
    topic = "test"
    consumer.subscribe([topic])
    
    # --- Message Polling and Display Loop ---
    try:
        latest_msg = None
        while True:
            # Inner loop to consume all messages in the buffer and get the latest one
            while True:
                msg = consumer.poll(0) # Non-blocking poll
                if msg is None:
                    # No more messages in the buffer, break the inner loop
                    break
                if msg.error():
                    print(f"ERROR: {msg.error()}")
                    continue
                # We have a message, so store it
                latest_msg = msg

            # If we have a message from the consumption loop, process it
            if latest_msg:
                # Decode the base64 message
                b64_decoded_frame = base64.b64decode(latest_msg.value())
                
                # Convert the bytes back to a numpy array for opencv
                frame_buffer = np.frombuffer(b64_decoded_frame, np.uint8)

                # Decode the JPEG image
                frame = cv2.imdecode(frame_buffer, cv2.IMREAD_COLOR)

                # Display the resulting frame
                cv2.imshow('Live Camera Feed (Raw)', frame)

                # Reset for the next iteration
                latest_msg = None

            # Allow the GUI to update and check for the 'q' key
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()
        cv2.destroyAllWindows()