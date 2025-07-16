import base64
import io
import torch
from ultralytics import YOLO
from ts.torch_handler.base_handler import BaseHandler
from PIL import Image

class YoloHandler(BaseHandler):
    """
    TorchServe handler for the YOLOv11 fire detection model.
    """
    def initialize(self, context):
        """
        Loads the model file and initializes the model.
        """
        properties = context.system_properties
        model_dir = properties.get("model_dir")

        # Determine the device to use (GPU if available, otherwise CPU)
        self.device = torch.device("cuda:" + str(properties.get("gpu_id")) if torch.cuda.is_available() else "cpu")
        print(f"Using device: {self.device}")

        # Load the YOLO model and move it to the determined device
        self.model = YOLO(f"{model_dir}/yolo11n.pt")
        # YOLO's predict method automatically handles device placement if CUDA is available
        if torch.cuda.is_available():
            self.model.to(self.device)

        self.initialized = True
        print("YOLOv11 model initialized successfully.")

    def preprocess(self, data):
        """
        Preprocesses the input data (a batch of requests).
        """
        images = []
        for row in data:
            # The input from the request body
            image_data = row.get("image_bytes") or row.get("data") or row.get("body")

            # The body can be bytes or a base64 encoded string in a dict
            if isinstance(image_data, dict) and "b64" in image_data:
                image_data = base64.b64decode(image_data["b64"])

            image = Image.open(io.BytesIO(image_data))
            images.append(image)

        return images

    def inference(self, data):
        """
        Runs inference on the preprocessed data.
        """
        # data is the list of PIL Images from preprocess()
        results = self.model.predict(data, conf=0.5, verbose=False)
        return results

    def postprocess(self, data):
        """
        Formats the output of inference into a JSON serializable list.
        """
        # data is the list of results from inference()
        output = []
        for result in data:
            res_json = {
                "boxes": result.boxes.xyxyn.tolist(),
                "scores": result.boxes.conf.tolist(),
                "classes": result.boxes.cls.tolist(),
            }
            output.append(res_json)

        return output