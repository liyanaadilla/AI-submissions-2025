"""
PlantWatch - Banana Ripeness Detection System
Authors: Wan Zafirzan Bin Wan Tarmizan (A22MJ8003) & Safuan Hakim Bin Shani (A22MJ8014)
Group 2 - PlantWatch

This application uses YOLOv8 deep learning to detect banana ripeness levels
in real-time and provides harvestability recommendations.
"""

from flask import Flask, render_template, request, Response, jsonify
import cv2
from ultralytics import YOLO
import numpy as np
from PIL import Image
import base64
import os
import urllib.request

app = Flask(__name__)

# Model weights URL (hosted on GitHub)
MODEL_URL = "https://github.com/Zaphyrzan/PlantWatch-AI-Fruit-Detection/raw/main/weights_3/best.pt"
MODEL_PATH = "weights_3/best.pt"


def download_model():
    """Download the model weights if not present."""
    if not os.path.exists(MODEL_PATH):
        print("Downloading model weights...")
        os.makedirs("weights_3", exist_ok=True)
        try:
            urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
            print("Model downloaded successfully!")
        except Exception as e:
            print(f"Error downloading model: {e}")
            print("Please download the model manually from:")
            print("https://github.com/Zaphyrzan/PlantWatch-AI-Fruit-Detection/tree/main/weights_3")
            raise


# Download model if not present, then load it
download_model()
banana_detection_model = YOLO(MODEL_PATH)


def get_harvestability_info(ripeness_status):
    """
    Returns harvestability information based on the ripeness status of the banana.
    """
    ripeness_lower = ripeness_status.lower()
    
    if ripeness_lower in ['ripe', 'ripen', 'yellow']:
        return {
            'status': 'Harvestable and Consumable',
            'recommendation': 'This banana is at its peak ripeness. Perfect for immediate consumption or sale.',
            'color': '#28a745'  # Green
        }
    elif ripeness_lower in ['unripe', 'raw', 'green', 'underripe']:
        return {
            'status': 'Not Ready for Harvest',
            'recommendation': 'This banana needs more time to ripen. Estimated time to ripeness: 3-5 days depending on storage conditions. Store at room temperature (20-25°C) to accelerate ripening.',
            'color': '#ffc107'  # Yellow/Warning
        }
    elif ripeness_lower in ['overripe', 'over-ripe', 'spoiled', 'rotten']:
        return {
            'status': 'Past Optimal Harvest Time',
            'recommendation': 'This banana is overripe. Not ideal for fresh consumption but can still be used for baking, smoothies, or compost. Consume within 1-2 days if still edible.',
            'color': '#dc3545'  # Red
        }
    else:
        return {
            'status': 'Unknown Ripeness',
            'recommendation': 'Unable to determine ripeness status. Please inspect manually.',
            'color': '#6c757d'  # Gray
        }


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/fruit_detection')
def fruit_detection():
    return render_template('fruit_detection.html')


@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/detect_objects', methods=['POST'])
def detect_objects():
    # Receive image data from the client
    image_data = request.json['image_data'].split(',')[1]  # Remove the data URL prefix

    # Decode base64 image data
    image_bytes = base64.b64decode(image_data)

    # Convert image bytes to numpy array
    image_array = np.frombuffer(image_bytes, dtype=np.uint8)

    # Decode the image
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

    # Perform object detection using YOLO
    results = banana_detection_model(image)

    # Extract detection results
    detected_objects = []
    for result in results:
        boxes = result.boxes.xywh.cpu()  # xywh bbox list
        clss = result.boxes.cls.cpu().tolist()  # classes Id list
        names = result.names  # classes names list
        confs = result.boxes.conf.float().cpu().tolist()  # probabilities of classes

        for box, cls, conf in zip(boxes, clss, confs):
            class_name = names[cls]
            # Extract ripeness status (first word) from class name
            ripeness_status = class_name.split(' ')[0] if ' ' in class_name else class_name
            harvestability = get_harvestability_info(ripeness_status)
            
            detected_objects.append({
                'class': class_name, 
                'bbox': box.tolist(), 
                'confidence': conf,
                'harvestability': harvestability
            })

    return jsonify(detected_objects)


def generate_frames():
    camera = cv2.VideoCapture(0)
    while True:
        success, frame = camera.read()  # Read frame from camera
        if not success:
            break
        else:
            fruit_results = banana_detection_model(frame)
            for result in fruit_results:
                im_array = result.plot()
                im = Image.fromarray(im_array[..., ::-1])
                image = cv2.cvtColor(np.array(im), cv2.COLOR_RGB2BGR)

            ret, buffer = cv2.imencode('.jpg', image, [cv2.IMWRITE_JPEG_QUALITY, 50])
            frame_bytes = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')


if __name__ == '__main__':
    print("=" * 60)
    print("PlantWatch - Banana Ripeness Detection System")
    print("Authors: A22MJ8003 & A22MJ8014 | Group 2 - PlantWatch")
    print("=" * 60)
    print("\nStarting server...")
    print("Open http://127.0.0.1:5000 in your browser")
    print("Navigate to 'Fruit Detection' to use the camera\n")
    app.run(host="0.0.0.0", debug=True)
