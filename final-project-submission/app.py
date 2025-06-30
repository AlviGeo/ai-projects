import streamlit as st
import cv2
import numpy as np
import matplotlib.pyplot as plt
from ultralytics import YOLO
from PIL import Image
from io import BytesIO
import tempfile
import torch
from ultralytics.engine.results import Boxes

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
            x1, y1, x2, y2 = map(int,  box.xyxy[0])
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

def generate_bar_chart(boxes, class_names):
    if boxes.shape[0] == 0:
        return None
    classes = boxes.cls.int().tolist()
    counts = {}
    for cls in classes:
        label = class_names.get(cls, 'Unknown')
        counts[label] = counts.get(label, 0) + 1
    labels = list(counts.keys())
    values = list(counts.values())

    fig, ax = plt.subplots(figsize=(12, 3))
    ax.bar(labels, values, color='skyblue')
    ax.set_title("Detected Objects Count")
    ax.set_ylabel("Count")
    ax.set_xlabel("Object Class")
    plt.xticks(rotation=45)
    st.pyplot(fig)

# ---- Sidebar Controls ----
with st.sidebar:
    st.header("Settings")
    model_name = st.selectbox("Choose YOLOv8 model", ["yolov8n.pt", "yolov8s.pt", "yolov8m.pt", "yolov8l.pt", "yolov8x.pt"])
    source_type = st.selectbox("Source Type", ["Image", "Video"])

    if source_type == "Image":
        image_resize = st.sidebar.slider("Resize image width", 300, 800, 600, step=50)
        uploaded_file = st.file_uploader("Upload an Image", type=['png', 'jpg', 'jpeg'])
    else:
        uploaded_file = st.file_uploader("Upload a Video", type=['mp4', 'mov', 'avi'])

    confidence = st.slider("Model Confidence", 0.0, 1.0, 0.3, 0.05)
    detect_btn = st.button("Run Detection")

# ---- Main UI ----
if detect_btn and uploaded_file:
    detector = YOLODetector(model_name)

    if source_type == 'Image':
        image = load_image(uploaded_file)
        image = cv2.resize(image, (image_resize, int(image.shape[0] * image_resize / image.shape[1])))
        
        result = detector.detect(image, confidence=confidence)
        annotated_image, class_names, boxes = detector.draw_boxes(image, result)

        col = st.columns([1, 4, 4, 1])
        with col[1]:
            st.subheader("Original Image")
            st.image(image)
        with col[2]:
            st.subheader("Detected Objects")
            st.image(annotated_image)
            
            # Convert image to PIL for download
            pil_img = Image.fromarray(cv2.cvtColor(annotated_image, cv2.COLOR_BGR2RGB))
            img_buffer = BytesIO()
            pil_img.save(img_buffer, format="PNG")
            img_bytes = img_buffer.getvalue()

            st.download_button(
                label="📥 Download Detected Image",
                data=img_bytes,
                file_name="detected_output.png",
                mime="image/png",
                use_container_width=True,
            )

        # Description below images
        description = describe_objects(boxes, class_names)
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align:center;font-size:18px;font-weight:600;'>{description}</p>", unsafe_allow_html=True)
        generate_bar_chart(boxes, class_names)
    
    elif source_type == 'Video':
        tfile = tempfile.NamedTemporaryFile(delete=False)
        tfile.write(uploaded_file.read())
        
        cap = cv2.VideoCapture(tfile.name)
        
        all_boxes = []
        class_names = detector.model.names
        
        sample_frame_orig = None
        sample_frame_annotated = None

        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        output_width = 600
        output_height = int(frame_height * output_width / frame_width) if frame_width > 0 else 0
        
        st.subheader("Processing Video...")
        progress_bar = st.progress(0)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        frame_count = 0
        while cap.isOpened() and output_height > 0:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            resized_frame = cv2.resize(frame, (output_width, output_height))
            
            result = detector.detect(resized_frame, confidence=confidence)
            
            if len(result.boxes) > 0:
                all_boxes.append(result.boxes)
            
            if sample_frame_annotated is None and len(result.boxes) > 0:
                sample_frame_orig = resized_frame
                sample_frame_annotated, _, _ = detector.draw_boxes(resized_frame, result)
            
            if total_frames > 0:
                progress_bar.progress(frame_count / total_frames)

        cap.release()
        progress_bar.empty()

        if not all_boxes:
            st.warning("No objects were detected in the video.")
        else:
            all_xyxy = torch.cat([b.xyxy for b in all_boxes])
            all_conf = torch.cat([b.conf for b in all_boxes])
            all_cls = torch.cat([b.cls for b in all_boxes])
            
            combined_tensor = torch.cat([
                all_xyxy, 
                all_conf.unsqueeze(1), 
                all_cls.unsqueeze(1)
            ], dim=1)
            
            combined_boxes = Boxes(
                combined_tensor, 
                sample_frame_orig.shape[:2]
            )
            
            st.subheader("Video Processing Complete")
            
            col = st.columns(2)
            with col[0]:
                st.subheader("Sample Frame")
                st.image(sample_frame_orig, channels="BGR", use_container_width=True)
            with col[1]:
                st.subheader("Annotated Sample")
                st.image(sample_frame_annotated, channels="BGR", use_container_width=True)

            description = describe_objects(combined_boxes, class_names)
            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center;font-size:18px;font-weight:600;'>{description}</p>", unsafe_allow_html=True)
            generate_bar_chart(combined_boxes, class_names)

elif uploaded_file and not detect_btn:
    st.info(f"Click the 'Run Detection' button from the sidebar to process the uploaded {source_type.lower()}.")
else:
    st.warning("Please upload an image or a video from the sidebar to start.")