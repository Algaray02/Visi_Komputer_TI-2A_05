"""
Helmet Detection API Backend
Flask server dengan FFmpeg untuk video encoding yang browser-compatible
"""

from flask import Flask, request, jsonify, send_file, Response
from flask_cors import CORS
import cv2
import numpy as np
import base64
from pathlib import Path
from ultralytics import YOLO
import tempfile
import os
import uuid
import subprocess
import shutil

# Create temp video directory if not exists
TEMP_VIDEO_DIR = Path("temp_videos")
TEMP_VIDEO_DIR.mkdir(exist_ok=True)
import logging
import torch
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Monkey patch torch.load for PyTorch 2.6+ compatibility
_original_torch_load = torch.load
def patched_torch_load(f, *args, **kwargs):
    kwargs.setdefault('weights_only', False)
    return _original_torch_load(f, *args, **kwargs)
torch.load = patched_torch_load

# Check if FFmpeg is available
def check_ffmpeg():
    """Check if FFmpeg is installed"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, 
                              text=True, 
                              timeout=5)
        if result.returncode == 0:
            logger.info("✅ FFmpeg is available")
            return True
    except Exception as e:
        logger.warning(f"⚠️ FFmpeg not found: {e}")
        logger.warning("Install FFmpeg: apt-get install ffmpeg (Linux) or download from ffmpeg.org (Windows)")
    return False

FFMPEG_AVAILABLE = check_ffmpeg()

# Load model with fallback
def load_detection_model():
    """Load model with automatic fallback to yolov11n if custom model fails"""
    MODEL_PATH = Path("results/helmet_balanced/weights/best.pt")
    
    # Try loading custom model first
    if MODEL_PATH.exists():
        try:
            logger.info(f"Loading custom model from {MODEL_PATH}...")
            model = YOLO(str(MODEL_PATH))
            logger.info("✅ Custom helmet detection model loaded successfully")
            return model
        except Exception as e:
            logger.warning(f"⚠️ Custom model loading failed: {e}")
    
    # Fallback to default YOLOv11 nano
    try:
        logger.info("Loading YOLOv11 nano model (auto-downloading)...")
        model = YOLO('yolov11n')
        logger.info("✅ YOLOv11 nano model loaded successfully")
        return model
    except Exception as e:
        logger.error(f"❌ Failed to load any model: {e}")
        return None

model = load_detection_model()

# Class mapping
CLASS_NAMES = {
    0: "with_helmet",
    1: "no_helmet",
    2: "motorcycle"
}

CLASS_COLORS = {
    0: (0, 255, 0),      # with_helmet - Green
    1: (0, 0, 255),      # no_helmet - Red
    2: (255, 165, 0)     # motorcycle - Orange
}

def decode_base64_image(image_string):
    """Decode base64 image string to numpy array"""
    try:
        if ',' in image_string:
            image_string = image_string.split(',')[1]
        
        image_data = base64.b64decode(image_string)
        image_array = np.frombuffer(image_data, dtype=np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        return image
    except Exception as e:
        logger.error(f"Error decoding image: {e}")
        return None

def annotate_frame(image, result):
    """Draw bounding boxes on image"""
    annotated_frame = image.copy()
    
    boxes = result.boxes
    for box in boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        cls_id = int(box.cls[0].item())
        conf = box.conf[0].item()
        
        color = CLASS_COLORS.get(cls_id, (255, 255, 255))
        
        # Draw bounding box
        cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
        
        # Draw label
        label = f"{CLASS_NAMES.get(cls_id, 'unknown')} {conf:.2%}"
        text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
        cv2.rectangle(annotated_frame, (x1, y1 - 25), (x1 + text_size[0], y1), color, -1)
        cv2.putText(annotated_frame, label, (x1, y1 - 5), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    return annotated_frame

def draw_detections(image, results):
    """Draw bounding boxes on image"""
    annotated_frame = image.copy()
    
    for result in results:
        annotated_frame = annotate_frame(annotated_frame, result)
    
    return annotated_frame

def convert_to_web_compatible_mp4(input_path, output_path):
    """
    Convert video to browser-compatible MP4 using FFmpeg
    Uses H.264 codec with proper settings for web playback
    """
    try:
        # FFmpeg command untuk web-compatible MP4
        # -c:v libx264: H.264 video codec
        # -preset fast: encoding speed
        # -crf 23: quality (lower = better, 18-28 recommended)
        # -pix_fmt yuv420p: pixel format compatible dengan semua browser
        # -movflags +faststart: moov atom di awal file untuk web streaming
        cmd = [
            'ffmpeg',
            '-i', str(input_path),
            '-c:v', 'libx264',
            '-preset', 'fast',
            '-crf', '23',
            '-pix_fmt', 'yuv420p',
            '-movflags', '+faststart',
            '-y',  # overwrite output file
            str(output_path)
        ]
        
        logger.info(f"Converting video with FFmpeg...")
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes timeout
        )
        
        if result.returncode == 0:
            logger.info("✅ Video converted successfully")
            return True
        else:
            logger.error(f"FFmpeg error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error("FFmpeg conversion timeout")
        return False
    except Exception as e:
        logger.error(f"FFmpeg conversion failed: {e}")
        return False

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    MODEL_PATH = Path("results/helmet_balanced/weights/best.pt")
    return jsonify({
        'status': 'ok',
        'model_loaded': model is not None,
        'ffmpeg_available': FFMPEG_AVAILABLE,
        'model_path': str(MODEL_PATH)
    })

@app.route('/api/detect-image', methods=['POST'])
def detect_image():
    """Detect helmet in image"""
    if model is None:
        return jsonify({'error': 'Model not loaded'}), 500
    
    try:
        data = request.json
        image_base64 = data.get('image')
        confidence_threshold = float(data.get('confidence_threshold', 0.5))
        
        if not image_base64:
            return jsonify({'error': 'No image provided'}), 400
        
        # Decode image
        image = decode_base64_image(image_base64)
        if image is None:
            return jsonify({'error': 'Failed to decode image'}), 400
        
        # Run detection
        results = model.predict(image, conf=confidence_threshold, verbose=False)
        
        # Annotate image with detections
        annotated_image = image.copy()
        
        # Process detections
        detections = {
            'with_helmet': 0,
            'no_helmet': 0,
            'motorcycle': 0,
            'details': [],
            'processed_image': None
        }
        
        for result in results:
            boxes = result.boxes
            annotated_image = annotate_frame(annotated_image, result)
            
            for box in boxes:
                cls_id = int(box.cls[0].item())
                conf = box.conf[0].item()
                
                if cls_id == 0:
                    detections['with_helmet'] += 1
                elif cls_id == 1:
                    detections['no_helmet'] += 1
                elif cls_id == 2:
                    detections['motorcycle'] += 1
                
                detections['details'].append({
                    'class': CLASS_NAMES.get(cls_id, 'unknown'),
                    'confidence': f"{conf:.2%}"
                })
        
        # Convert annotated image to base64
        _, buffer = cv2.imencode('.jpg', annotated_image)
        processed_image_base64 = base64.b64encode(buffer).decode('utf-8')
        detections['processed_image'] = f"data:image/jpeg;base64,{processed_image_base64}"
        
        return jsonify(detections)
    
    except Exception as e:
        logger.error(f"Error in detect_image: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/detect-video', methods=['POST'])
def detect_video():
    """Detect helmet in video"""
    if model is None:
        return jsonify({'error': 'Model not loaded'}), 500
    
    temp_input = None
    temp_output_raw = None
    cap = None
    out = None
    
    try:
        video_file = request.files.get('video')
        confidence_threshold = float(request.form.get('confidence_threshold', 0.5))
        sample_rate = int(request.form.get('sample_rate', 5))
        
        if not video_file:
            return jsonify({'error': 'No video provided'}), 400
        
        # Save temp input video
        temp_input = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        video_file.save(temp_input.name)
        temp_input.close()
        
        # Process video
        cap = cv2.VideoCapture(temp_input.name)
        
        frame_count = 0
        detected_frames = 0
        total_detections = {
            'with_helmet': 0,
            'no_helmet': 0,
            'motorcycle': 0,
        }
        details = []
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Create temporary output video (raw, before FFmpeg conversion)
        temp_output_raw = tempfile.NamedTemporaryFile(delete=False, suffix='_raw.avi')
        temp_output_raw.close()
        
        # Use XVID codec untuk temporary file (reliable)
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(temp_output_raw.name, fourcc, fps, (width, height))
        
        last_frame = None
        preview_frame = None
        
        logger.info(f"Processing {total_frames} frames...")
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            # Run detection every sample_rate frames
            if frame_count % sample_rate == 0 or frame_count == 1:
                results = model.predict(frame, conf=confidence_threshold, verbose=False)
                annotated_frame = draw_detections(frame, results)
                
                # Count detections and collect details
                for result in results:
                    boxes = result.boxes
                    for box in boxes:
                        cls_id = int(box.cls[0].item())
                        conf = box.conf[0].item()
                        
                        if cls_id == 0:
                            total_detections['with_helmet'] += 1
                        elif cls_id == 1:
                            total_detections['no_helmet'] += 1
                        elif cls_id == 2:
                            total_detections['motorcycle'] += 1
                        
                        details.append({
                            'class': CLASS_NAMES.get(cls_id, 'unknown'),
                            'confidence': f"{conf:.2%}",
                            'frame': frame_count
                        })
                
                detected_frames += 1
                last_frame = annotated_frame
                if preview_frame is None:
                    preview_frame = annotated_frame
            else:
                # Reuse last annotated frame
                if last_frame is not None:
                    annotated_frame = last_frame
                else:
                    annotated_frame = frame
            
            out.write(annotated_frame)
        
        if cap is not None:
            cap.release()
        if out is not None:
            out.release()
        
        # Cleanup input temp file
        try:
            os.unlink(temp_input.name)
        except:
            pass
        
        # Convert to web-compatible MP4 using FFmpeg
        unique_filename = f"video_{uuid.uuid4().hex}.mp4"
        final_output_path = TEMP_VIDEO_DIR / unique_filename
        
        if FFMPEG_AVAILABLE:
            logger.info("Converting to web-compatible MP4...")
            success = convert_to_web_compatible_mp4(temp_output_raw.name, final_output_path)
            
            if not success:
                logger.warning("FFmpeg conversion failed, using raw video")
                shutil.move(temp_output_raw.name, final_output_path)
            else:
                # Cleanup raw temp file
                try:
                    os.unlink(temp_output_raw.name)
                except:
                    pass
        else:
            logger.warning("FFmpeg not available, using raw video (may not play in browser)")
            shutil.move(temp_output_raw.name, final_output_path)
        
        # Convert preview frame to base64
        preview_image_base64 = None
        if preview_frame is not None:
            _, buffer = cv2.imencode('.jpg', preview_frame)
            preview_image_base64 = f"data:image/jpeg;base64,{base64.b64encode(buffer).decode('utf-8')}"
        
        # Return response
        response_data = {
            'with_helmet': total_detections['with_helmet'],
            'no_helmet': total_detections['no_helmet'],
            'motorcycle': total_detections['motorcycle'],
            'details': details,
            'preview_image': preview_image_base64,
            'video_path': f"/api/video/{unique_filename}",
            'total_frames': total_frames,
            'processed_frames': detected_frames,
            'ffmpeg_converted': FFMPEG_AVAILABLE
        }
        
        return jsonify(response_data)
    
    except Exception as e:
        logger.error(f"Error in detect_video: {e}")
        # Cleanup on error
        if cap is not None:
            cap.release()
        if out is not None:
            out.release()
        if temp_input is not None:
            try:
                os.unlink(temp_input.name)
            except:
                pass
        if temp_output_raw is not None:
            try:
                os.unlink(temp_output_raw.name)
            except:
                pass
        return jsonify({'error': str(e)}), 500

@app.route('/api/models', methods=['GET'])
def get_models():
    """Get information about available models"""
    return jsonify({
        'models': [
            {
                'name': 'helmet_balanced',
                'path': 'results/helmet_balanced/weights/best.pt',
                'status': 'loaded' if model is not None else 'not_loaded'
            }
        ]
    })

@app.route('/api/video/<filename>', methods=['GET'])
def serve_video(filename):
    """Serve processed video file with proper headers for streaming"""
    try:
        file_path = TEMP_VIDEO_DIR / filename
        if not file_path.exists():
            return jsonify({'error': 'Video not found'}), 404
        
        # Get file size for range requests
        file_size = os.path.getsize(file_path)
        
        # Handle range requests for video seeking
        range_header = request.headers.get('Range', None)
        
        if range_header:
            # Parse range header
            byte_range = range_header.replace('bytes=', '').split('-')
            start = int(byte_range[0]) if byte_range[0] else 0
            end = int(byte_range[1]) if len(byte_range) > 1 and byte_range[1] else file_size - 1
            
            # Read the requested range
            with open(file_path, 'rb') as f:
                f.seek(start)
                data = f.read(end - start + 1)
            
            # Create response with partial content
            response = Response(
                data,
                206,  # Partial Content
                mimetype='video/mp4',
                direct_passthrough=True
            )
            response.headers.add('Content-Range', f'bytes {start}-{end}/{file_size}')
            response.headers.add('Accept-Ranges', 'bytes')
            response.headers.add('Content-Length', str(len(data)))
            response.headers.add('Cache-Control', 'no-cache')
            return response
        else:
            # Serve entire file
            response = send_file(
                str(file_path),
                mimetype='video/mp4',
                as_attachment=False,
                download_name=filename
            )
            response.headers.add('Accept-Ranges', 'bytes')
            response.headers.add('Content-Length', str(file_size))
            response.headers.add('Cache-Control', 'no-cache')
            return response
            
    except Exception as e:
        logger.error(f"Error serving video: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)