import streamlit as st
import cv2
import numpy as np
import matplotlib.pyplot as plt
from ultralytics import YOLO
from PIL import Image
from io import BytesIO
import tempfile

# Set page config
st.set_page_config(page_title="YOLOv8 Object Detection", layout="wide")

# ---- OOP Implementation ----
class YOLODetector:
    def __init__(self, model_name):
        self.model = YOLO(model_name)

    def detect(self, image, confidence=0.3):
        results = self.model(image, conf=confidence) 
        return results[0]

    def draw_boxes(self, image, results):
        img_copy = image.copy()
        boxes = results.boxes
        class_names = self.model.names
        for box in boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cls_id = int(box.cls[0])
            label = f"{class_names[cls_id]}"
            conf = float(box.conf[0])
            cv2.rectangle(img_copy, (x1, y1), (x2, y2), (255, 0, 0), 2)
            cv2.putText(img_copy, f"{label} {conf:.2f}", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
        return img_copy, class_names, boxes

# ---- Utility Functions ----
def load_image(uploaded_file):
    image = Image.open(uploaded_file).convert('RGB')
    return np.array(image)

def display_gradient_title(text):
    html = f"""
    <style>
        .gradient-title {{
            background: linear-gradient(to right, red, orange, yellow, green, blue, purple);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .gradient-wrapper {{
            display: flex;
            justify-content: center;
        }}
    </style>
    <div class="gradient-wrapper">
        <h1 class="gradient-title">{text}</h1>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

display_gradient_title("YOLOv8 Object Detection")

def describe_objects(boxes, class_names):
    if boxes.shape[0] == 0:
        return "No objects were detected."
    classes = boxes.cls.int().tolist()
    counts = {}
    for cls in classes:
        label = class_names.get(cls, 'Unknown')
        counts[label] = counts.get(label, 0) + 1
    description = ", ".join([f"{v} {k}" for k, v in counts.items()])
    return f"This image contains: {description}."

# ---- Sidebar Controls ----
with st.sidebar:
    st.header("Settings")
    model_name = st.selectbox("Choose YOLOv8 model", ["yolov8n.pt", "yolov8s.pt", "yolov8m.pt", "yolov8l.pt", "yolov8x.pt"])
    source_type = st.selectbox("Source Type", ["Image", "Video", "Webcam"])
    image_resize = st.sidebar.slider("Resize image width", 300, 800, 600, step=50)
    confidence = st.slider("Model Confidence", 0.0, 1.0, 0.3, 0.05)
    uploaded_file = st.file_uploader("Upload an Image", type=['png', 'jpg', 'jpeg'])
    detect_btn = st.button("Run Detection")

# ---- Main UI ----
if detect_btn and uploaded_file:
    image = load_image(uploaded_file)
    image = cv2.resize(image, (image_resize, int(image.shape[0] * image_resize / image.shape[1])))
    
    detector = YOLODetector(model_name)
    result = detector.detect(image, confidence=confidence)
    annotated_image, class_names, boxes = detector.draw_boxes(image, result)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Original Image")
        st.image(image)
    with col2:
        st.subheader("Detected Objects")
        st.image(annotated_image)

    # Description below images
    description = describe_objects(boxes, class_names)
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center;font-size:18px;font-weight:600;'>{description}</p>", unsafe_allow_html=True)

elif uploaded_file and not detect_btn:
    st.info("Click the 'Run Detection' button from the sidebar to process the uploaded image.")
else:
    st.warning("Please upload an image from the sidebar to start.")