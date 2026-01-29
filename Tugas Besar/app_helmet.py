import streamlit as st
import cv2
import numpy as np
from pathlib import Path
from PIL import Image
import tempfile
import os
from ultralytics import YOLO
import pandas as pd

# Set page config
st.set_page_config(
    page_title="🏍️ Helmet Detection System",
    page_icon="🏍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .header {
        text-align: center;
        color: #1f77b4;
        margin-bottom: 30px;
    }
    .metric-box {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .safe {
        background-color: #d4edda;
        color: #155724;
        padding: 15px;
        border-radius: 5px;
        border-left: 5px solid #28a745;
    }
    .unsafe {
        background-color: #f8d7da;
        color: #721c24;
        padding: 15px;
        border-radius: 5px;
        border-left: 5px solid #dc3545;
    }
    .warning {
        background-color: #fff3cd;
        color: #856404;
        padding: 15px;
        border-radius: 5px;
        border-left: 5px solid #ffc107;
    }
    </style>
""", unsafe_allow_html=True)

# Load model
@st.cache_resource
def load_model():
    model_path = Path("results/helmet_balanced/weights/best.pt")
    if not model_path.exists():
        st.error(f"❌ Model tidak ditemukan di: {model_path}")
        return None
    model = YOLO(str(model_path))
    return model

# Class colors for visualization
CLASS_COLORS = {
    0: (0, 255, 0),      # with_helmet - Green
    1: (0, 0, 255),      # no_helmet - Red
    2: (255, 165, 0)     # motorcycle - Orange
}

CLASS_NAMES = {
    0: "With Helmet",
    1: "No Helmet",
    2: "Motorcycle"
}

def detect_in_image(image, model, confidence_threshold=0.5):
    """Deteksi helmet dalam gambar"""
    results = model.predict(image, conf=confidence_threshold, verbose=False)
    
    detections = {
        'with_helmet': 0,
        'no_helmet': 0,
        'motorcycle': 0,
        'total_riders': 0,
        'details': []
    }
    
    # Process detections
    for result in results:
        boxes = result.boxes
        for box in boxes:
            cls_id = int(box.cls[0].item())
            conf = box.conf[0].item()
            
            if cls_id == 0:
                detections['with_helmet'] += 1
                detections['total_riders'] += 1
            elif cls_id == 1:
                detections['no_helmet'] += 1
                detections['total_riders'] += 1
            elif cls_id == 2:
                detections['motorcycle'] += 1
            
            detections['details'].append({
                'class': CLASS_NAMES[cls_id],
                'confidence': f"{conf:.2%}"
            })
    
    return detections, results

def draw_detections(image, results):
    """Gambarkan bounding box dan label pada gambar"""
    annotated_frame = image.copy()
    
    for result in results:
        boxes = result.boxes
        for box in boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cls_id = int(box.cls[0].item())
            conf = box.conf[0].item()
            
            color = CLASS_COLORS.get(cls_id, (255, 255, 255))
            
            # Draw bounding box
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
            
            # Draw label
            label = f"{CLASS_NAMES[cls_id]} {conf:.2%}"
            text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
            cv2.rectangle(annotated_frame, (x1, y1 - 25), (x1 + text_size[0], y1), color, -1)
            cv2.putText(annotated_frame, label, (x1, y1 - 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    return annotated_frame

def draw_tracked_detections(image, results):
    """Gambarkan bounding box dengan tracking ID untuk stabilitas"""
    annotated_frame = image.copy()
    
    for result in results:
        boxes = result.boxes
        for box in boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cls_id = int(box.cls[0].item())
            conf = box.conf[0].item()
            track_id = int(box.id[0].item()) if box.id is not None else -1
            
            color = CLASS_COLORS.get(cls_id, (255, 255, 255))
            
            # Draw bounding box dengan lebih tebal untuk visibilitas tracking
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 3)
            
            # Draw label dengan tracking ID
            if track_id >= 0:
                label = f"ID:{track_id} {CLASS_NAMES[cls_id]} {conf:.2%}"
            else:
                label = f"{CLASS_NAMES[cls_id]} {conf:.2%}"
            
            text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
            cv2.rectangle(annotated_frame, (x1, y1 - 30), (x1 + text_size[0], y1), color, -1)
            cv2.putText(annotated_frame, label, (x1, y1 - 8), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    return annotated_frame

def analyze_safety_compliance(with_helmet, no_helmet, total_riders):
    """Analisis compliance keselamatan"""
    if total_riders == 0:
        return "⚠️ Tidak ada pengendara terdeteksi", "warning"
    
    compliance_rate = (with_helmet / total_riders) * 100
    
    if compliance_rate == 100:
        status = "✅ AMAN - Semua pengendara menerapkan safety dengan menggunakan helm"
        color = "safe"
    elif compliance_rate >= 80:
        status = "✅ CUKUP AMAN - Sebagian besar pengendara menggunakan helm"
        color = "safe"
    elif compliance_rate >= 50:
        status = "⚠️ RAWAN - Banyak pengendara yang tidak menggunakan helm"
        color = "warning"
    else:
        status = "❌ BAHAYA - Mayoritas pengendara tidak menggunakan helm, melanggar regulasi keselamatan"
        color = "unsafe"
    
    return status, color, compliance_rate

def process_video(video_path, model, confidence_threshold=0.5, sample_rate=5):
    """Proses video dan deteksi helmet dengan tracking untuk menghindari flicker"""
    cap = cv2.VideoCapture(video_path)
    
    frame_count = 0
    detected_frames = 0
    total_detections = {
        'with_helmet': 0,
        'no_helmet': 0,
        'motorcycle': 0,
    }
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # Create video writer
    output_path = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4').name
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Track object IDs untuk menghindari flicker
    tracked_objects = {}
    frame_with_tracking = None
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        
        # Run tracking on every frame untuk stabilitas, tapi hanya deteksi setiap sample_rate
        if frame_count % sample_rate == 0 or frame_count == 1:
            # Gunakan track() instead of predict() untuk mendapatkan tracking IDs
            results = model.track(frame, conf=confidence_threshold, persist=True, verbose=False)
            
            detections, _ = detect_in_image(frame, model, confidence_threshold)
            annotated_frame = draw_tracked_detections(frame, results)
            
            total_detections['with_helmet'] += detections['with_helmet']
            total_detections['no_helmet'] += detections['no_helmet']
            total_detections['motorcycle'] += detections['motorcycle']
            
            if detections['total_riders'] > 0:
                detected_frames += 1
            
            frame_with_tracking = annotated_frame
        else:
            # Gunakan frame yang sudah di-track dari sebelumnya untuk mencegah flicker
            if frame_with_tracking is not None:
                # Lakukan lightweight tracking untuk stabilitas
                results = model.track(frame, conf=confidence_threshold, persist=True, verbose=False)
                annotated_frame = draw_tracked_detections(frame, results)
            else:
                annotated_frame = frame.copy()
        
        out.write(annotated_frame)
        progress = min(int((frame_count / total_frames) * 100), 100)
        progress_bar.progress(progress)
        status_text.text(f"Processing frame {frame_count}/{total_frames}...")
    
    cap.release()
    out.release()
    
    progress_bar.progress(100)
    status_text.text("✅ Video processing selesai!")
    
    return output_path, total_detections, detected_frames

# Main app
st.markdown("<h1 class='header'>🏍️ Helmet Detection System</h1>", unsafe_allow_html=True)
st.markdown("Sistem deteksi helm untuk menganalisis kepatuhan keselamatan berkendara", 
           help="Aplikasi ini menggunakan YOLOv11 untuk mendeteksi helm pada pengendara motor")

# Load model
model = load_model()
if model is None:
    st.stop()

# Sidebar settings
st.sidebar.header("⚙️ Settings")
confidence_threshold = st.sidebar.slider("Confidence Threshold", 0.0, 1.0, 0.5, 0.05)

# Main content
tab1, tab2, tab3 = st.tabs(["📷 Image Detection", "🎬 Video Detection", "📊 About"])

with tab1:
    st.header("Image Detection")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Upload Gambar")
        uploaded_image = st.file_uploader("Pilih gambar...", type=["jpg", "jpeg", "png", "bmp"])
        
        if uploaded_image is not None:
            image = Image.open(uploaded_image)
            image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Run detection
            with st.spinner("🔍 Mendeteksi helm..."):
                detections, results = detect_in_image(image_cv, model, confidence_threshold)
                annotated_image = draw_detections(image_cv, results)
            
            # Display results
            st.image(cv2.cvtColor(annotated_image, cv2.COLOR_BGR2RGB), 
                    use_column_width=True, caption="Hasil Deteksi")
    
    with col2:
        if uploaded_image is not None:
            st.subheader("📊 Hasil Analisis")
            
            # Statistics
            col_stats1, col_stats2, col_stats3 = st.columns(3)
            
            with col_stats1:
                st.metric("👤 With Helmet", detections['with_helmet'], 
                         delta="✅" if detections['with_helmet'] > 0 else "")
            
            with col_stats2:
                st.metric("❌ No Helmet", detections['no_helmet'],
                         delta="⚠️" if detections['no_helmet'] > 0 else "")
            
            with col_stats3:
                st.metric("🏍️ Motorcycle", detections['motorcycle'])
            
            st.divider()
            
            # Compliance analysis
            if detections['total_riders'] > 0:
                status, color, compliance_rate = analyze_safety_compliance(
                    detections['with_helmet'],
                    detections['no_helmet'],
                    detections['total_riders']
                )
                
                st.markdown(f"<div class='{color}'><b>{status}</b></div>", 
                           unsafe_allow_html=True)
                
                st.subheader("📈 Compliance Rate")
                st.progress(compliance_rate / 100)
                st.write(f"**{compliance_rate:.1f}%** pengendara menggunakan helm")
            else:
                st.info("ℹ️ Tidak ada pengendara yang terdeteksi dalam gambar")
            
            # Details
            st.subheader("🔍 Detail Deteksi")
            if detections['details']:
                df_details = pd.DataFrame(detections['details'])
                st.dataframe(df_details, use_container_width=True, hide_index=True)

with tab2:
    st.header("Video Detection")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Upload Video")
        uploaded_video = st.file_uploader("Pilih video...", type=["mp4", "avi", "mov", "mkv"])
        
        if uploaded_video is not None:
            # Save uploaded video
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
                tmp_file.write(uploaded_video.read())
                tmp_video_path = tmp_file.name
            
            sample_rate = st.slider("Sample Rate (process every N frames)", 1, 10, 5)
            
            if st.button("🎬 Start Video Detection", type="primary"):
                with st.spinner("🔄 Processing video... (ini mungkin butuh waktu)"):
                    output_video_path, total_detections, detected_frames = process_video(
                        tmp_video_path, model, confidence_threshold, sample_rate
                    )
                
                st.success("✅ Video processing selesai!")
                
                # Display results
                st.subheader("📊 Video Analysis Results")
                
                col_v1, col_v2, col_v3 = st.columns(3)
                
                with col_v1:
                    st.metric("👤 With Helmet (Total)", total_detections['with_helmet'])
                
                with col_v2:
                    st.metric("❌ No Helmet (Total)", total_detections['no_helmet'])
                
                with col_v3:
                    st.metric("🏍️ Motorcycle (Total)", total_detections['motorcycle'])
                
                st.divider()
                
                # Overall compliance
                total_riders = total_detections['with_helmet'] + total_detections['no_helmet']
                if total_riders > 0:
                    status, color, compliance_rate = analyze_safety_compliance(
                        total_detections['with_helmet'],
                        total_detections['no_helmet'],
                        total_riders
                    )
                    
                    st.markdown(f"<div class='{color}'><b>{status}</b></div>", 
                               unsafe_allow_html=True)
                    
                    st.subheader("📈 Overall Compliance Rate")
                    st.progress(compliance_rate / 100)
                    st.write(f"**{compliance_rate:.1f}%** pengendara menggunakan helm")
                    st.write(f"Frames dengan deteksi: {detected_frames}")
                else:
                    st.info("ℹ️ Tidak ada pengendara yang terdeteksi dalam video")
                
                # Download processed video
                with open(output_video_path, 'rb') as f:
                    st.download_button(
                        label="📥 Download Video dengan Deteksi",
                        data=f.read(),
                        file_name="helmet_detection_result.mp4",
                        mime="video/mp4"
                    )
                
                # Cleanup
                os.unlink(tmp_video_path)
                os.unlink(output_video_path)

with tab3:
    st.header("ℹ️ About This Application")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Fitur Utama")
        st.markdown("""
        - ✅ Deteksi helm pada pengendara motor
        - 📊 Analisis kepatuhan keselamatan
        - 📷 Kompatibel dengan gambar
        - 🎬 Kompatibel dengan video
        - 📈 Real-time statistics
        """)
    
    with col2:
        st.subheader("📋 Kelas Deteksi")
        st.markdown("""
        - **🟢 With Helmet**: Pengendara yang menggunakan helm
        - **🔴 No Helmet**: Pengendara tanpa helm
        - **🟠 Motorcycle**: Motor/kendaraan roda dua
        """)
    
    st.divider()
    
    st.subheader("🏆 Safety Compliance Levels")
    col_safe1, col_safe2, col_safe3, col_safe4 = st.columns(4)
    
    with col_safe1:
        st.markdown("""
        <div class='safe'>
        <b>✅ 100% Safe</b><br>
        Semua pakai helm
        </div>
        """, unsafe_allow_html=True)
    
    with col_safe2:
        st.markdown("""
        <div class='safe'>
        <b>✅ 80-99% Safe</b><br>
        Sebagian besar aman
        </div>
        """, unsafe_allow_html=True)
    
    with col_safe3:
        st.markdown("""
        <div class='warning'>
        <b>⚠️ 50-79% Safe</b><br>
        Cukup rawan
        </div>
        """, unsafe_allow_html=True)
    
    with col_safe4:
        st.markdown("""
        <div class='unsafe'>
        <b>❌ <50% Safe</b><br>
        Sangat berbahaya
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    st.subheader("📌 Informasi Model")
    st.info("""
    - **Model**: YOLOv11 (Pretrained & Fine-tuned)
    - **Dataset**: Helmet Detection Dataset (14 sources)
    - **Total Training Data**: 18,731 images
    - **Classes**: 3 (with_helmet, no_helmet, motorcycle)
    - **Framework**: Ultralytics YOLO
    """)

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: gray; margin-top: 20px;'>
    <small>🏍️ Helmet Detection System v1.0 | Untuk keselamatan berkendara</small>
</div>
""", unsafe_allow_html=True)
