import numpy as np
import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# Define natural hair colors (BGR format for OpenCV)
HAIR_COLORS = [
    (255, 255, 0),    # Cyan (Natural light)
    (0, 165, 255),    # Orange (Natural warm)
    (51, 102, 153),   # Brown
    (255, 0, 0),      # Red
    (0, 0, 255),      # Yellow
]

BG_COLOR = (192, 192, 192)  # gray

# Path to the hair segmenter model
MODEL_PATH = 'hair_segmenter.tflite'

def resize_and_show(image, window_name='Image'):
    """Display image with resizing if needed"""
    h, w = image.shape[:2]
    if h > 800 or w > 800:
        scale = min(800/h, 800/w)
        image = cv2.resize(image, (int(w*scale), int(h*scale)))
    return image

# Create segmenter options
base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
options = vision.ImageSegmenterOptions(
    base_options=base_options,
    output_category_mask=True
)

# Open webcam
cap = cv2.VideoCapture(1)

# Color index tracker
color_index = 0

# Create the image segmenter
with vision.ImageSegmenter.create_from_options(options) as segmenter:
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            break
        
        # Convert BGR to RGB for MediaPipe
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Create MediaPipe image from frame
        image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
        
        # Perform segmentation
        segmentation_result = segmenter.segment(image)
        category_mask = segmentation_result.category_mask
        
        # Get current hair color
        current_color = HAIR_COLORS[color_index]
        
        # Create hair color overlay
        hair_overlay = np.zeros(frame_rgb.shape, dtype=np.uint8)
        hair_overlay[:] = current_color
        
        # Apply hair color only to detected hair area, keep original frame elsewhere
        condition = np.stack((category_mask.numpy_view(),) * 3, axis=-1) > 0.2
        output_image = np.where(condition, hair_overlay, frame_rgb)
        
        # Resize for display
        output_image = resize_and_show(output_image)
        
        # Convert back to BGR for OpenCV display
        output_bgr = cv2.cvtColor(output_image, cv2.COLOR_RGB2BGR)
        
        # Display result
        cv2.imshow('Hair Detection', output_bgr)
        
        # Handle key press
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('r'):
            color_index = (color_index + 1) % len(HAIR_COLORS)
            print(f'Hair color changed to: {HAIR_COLORS[color_index]}')

cap.release()
cv2.destroyAllWindows()
