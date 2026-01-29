import os
import cv2
import numpy as np
import torch
import threading
import time
from sam2.build_sam import build_sam2
from sam2.sam2_image_predictor import SAM2ImagePredictor

# --- KONFIGURASI ---
sam2_checkpoint = "sam2.1_hiera_tiny.pt"
model_cfg = os.path.abspath("sam2.1_hiera_t.yaml")
device = "cuda" if torch.cuda.is_available() else "cpu"
INFERENCE_SIZE = (320, 240)
DISPLAY_SIZE = (640, 480)

# Load Model
try:
    print(f"Loading SAM2 model on {device}...")
    sam2_model = build_sam2(model_cfg, sam2_checkpoint, device=device)
    predictor = SAM2ImagePredictor(sam2_model)
    print("Model loaded.")
except Exception as e:
    print(f"Error loading SAM2: {e}")
    exit(1)

# Variabel Global untuk Threading
current_frame_for_ai = None
latest_mask = None
thread_lock = threading.Lock()
is_running = True

# Variabel untuk mouse interaction
click_points = []
click_labels = []
scale_factor = 1.0  # Scale factor antara display dan inference
mouse_event_lock = threading.Lock()

def mouse_callback(event, x, y, flags, param):
    """Handle mouse click untuk select area"""
    global click_points, click_labels, scale_factor, h_display, w_display
    
    if event == cv2.EVENT_LBUTTONDOWN:
        # Left click = foreground (objek yang ingin di-segment)
        with mouse_event_lock:
            # Scale dari display ke inference size
            # DISPLAY_SIZE = (640, 480), INFERENCE_SIZE = (320, 240)
            inf_x = int(x * INFERENCE_SIZE[0] / DISPLAY_SIZE[0])
            inf_y = int(y * INFERENCE_SIZE[1] / DISPLAY_SIZE[1])
            click_points.append([inf_x, inf_y])
            click_labels.append(1)
            print(f"✓ Click ({x}, {y}) -> Foreground point added (inference: {inf_x}, {inf_y})")
    
    elif event == cv2.EVENT_RBUTTONDOWN:
        # Right click = background (area yang ingin di-exclude)
        with mouse_event_lock:
            inf_x = int(x * INFERENCE_SIZE[0] / DISPLAY_SIZE[0])
            inf_y = int(y * INFERENCE_SIZE[1] / DISPLAY_SIZE[1])
            click_points.append([inf_x, inf_y])
            click_labels.append(0)
            print(f"✗ Right click ({x}, {y}) -> Background point added (inference: {inf_x}, {inf_y})")

def ai_worker_thread():
    """Thread khusus untuk menjalankan SAM2 di background"""
    global current_frame_for_ai, latest_mask, is_running, click_points, click_labels
    
    while is_running:
        frame_to_process = None
        points_to_use = []
        labels_to_use = []
        
        # Ambil frame terbaru dan points dari main thread dengan aman
        with thread_lock:
            if current_frame_for_ai is not None:
                frame_to_process = current_frame_for_ai.copy()
                current_frame_for_ai = None
        
        # Ambil click points
        with mouse_event_lock:
            if len(click_points) > 0:
                points_to_use = np.array(click_points).copy()
                labels_to_use = np.array(click_labels).copy()

        if frame_to_process is not None and len(points_to_use) > 0:
            try:
                # 1. Resize untuk kecepatan
                h_orig, w_orig = frame_to_process.shape[:2]
                frame_small = cv2.resize(frame_to_process, INFERENCE_SIZE)
                h_small, w_small = frame_small.shape[:2]
                
                # 2. Konversi ke RGB dan Set Image
                frame_rgb = cv2.cvtColor(frame_small, cv2.COLOR_BGR2RGB)
                predictor.set_image(frame_rgb)
                
                # 3. Prediksi Mask menggunakan click points
                masks, scores, _ = predictor.predict(
                    point_coords=points_to_use,
                    point_labels=labels_to_use,
                    multimask_output=False
                )
                
                # 5. Proses Mask
                generated_mask = masks[0].astype(np.uint8) * 255
                generated_mask = cv2.resize(generated_mask, (w_orig, h_orig))
                
                # Update mask global
                with thread_lock:
                    latest_mask = generated_mask
            
            except Exception as e:
                print(f"AI Error: {e}")
        else:
            # Istirahat sebentar jika tidak ada tugas untuk menghemat CPU
            time.sleep(0.01)

# --- MAIN PROGRAM ---

# Start Thread AI
worker = threading.Thread(target=ai_worker_thread)
worker.daemon = True
worker.start()

# Setup Kamera
cap = cv2.VideoCapture(1) # Ganti index kamera jika perlu
if not cap.isOpened():
    print("Error: Tidak bisa membuka kamera!")
    exit(1)

colors = [(255, 0, 0), (0, 255, 255), (0, 0, 255), (0, 255, 0)]
color_names = ["Biru", "Kuning", "Merah", "Hijau"]
current_color_idx = 0

print("=" * 60)
print("SAM2 General Object Segmentation - Interactive Mode")
print("=" * 60)
print("🖱️  MOUSE CONTROLS:")
print("   LEFT CLICK   = Add foreground point (yang ingin di-segment)")
print("   RIGHT CLICK  = Add background point (yang ingin di-exclude)")
print("🎨 KEYBOARD CONTROLS:")
print("   'r' = Ganti warna segmentasi")
print("   'c' = Clear semua points (reset)")
print("   'q' = Keluar")
print("=" * 60)
print("\n💡 TIPS PENGGUNAAN:")
print("   1. Klik di area objek yang ingin di-segment (misal: klik di rambut)")
print("   2. Bisa tambah multiple points untuk hasil lebih akurat")
print("   3. Jika salah, tekan 'c' untuk reset dan coba lagi")
print("   4. Lihat lingkaran hijau/merah di frame = points yang sudah di-klik")
print("=" * 60 + "\n")

fps_clock = cv2.getTickCount()
frame_count = 0

# Setup window callback
cv2.namedWindow("SAM2 General Object Segmentation", cv2.WINDOW_AUTOSIZE)

try:
    while True:
        ret, frame = cap.read()
        if not ret: break
        
        frame_count += 1
        frame = cv2.resize(frame, DISPLAY_SIZE)
        h_display, w_display = frame.shape[:2]
        
        # 1. Kirim frame ke AI Thread (Tanpa menunggu/Blocking)
        with thread_lock:
            if current_frame_for_ai is None: # Hanya kirim jika AI sedang nganggur
                current_frame_for_ai = frame
        
        # 2. Ambil mask terakhir yang tersedia
        mask_display = None
        with thread_lock:
            if latest_mask is not None:
                mask_display = latest_mask
        
        # 3. Terapkan pewarnaan jika mask ada
        output_frame = frame.copy()
        if mask_display is not None:
            # Smoothing mask agar lebih rapi
            mask_blur = cv2.GaussianBlur(mask_display, (5, 5), 0)
            
            # Buat layer warna
            colored_layer = np.zeros_like(frame)
            colored_layer[:] = colors[current_color_idx]
            
            # Blend area objek
            obj_region = mask_blur > 0
            
            # Cara cepat blending: Weighted Add
            output_frame[obj_region] = cv2.addWeighted(
                frame[obj_region], 0.6, 
                colored_layer[obj_region], 0.4, 
                0
            )

        # 4. Hitung FPS
        fps = cv2.getTickFrequency() / (cv2.getTickCount() - fps_clock)
        fps_clock = cv2.getTickCount()
        
        # 5. Draw click points pada frame
        with mouse_event_lock:
            for i, (pt, label) in enumerate(zip(click_points, click_labels)):
                # Scale back ke display size
                disp_x = int(pt[0] * DISPLAY_SIZE[0] / INFERENCE_SIZE[0])
                disp_y = int(pt[1] * DISPLAY_SIZE[1] / INFERENCE_SIZE[1])
                
                color = (0, 255, 0) if label == 1 else (0, 0, 255)  # Green=foreground, Red=background
                cv2.circle(output_frame, (disp_x, disp_y), 5, color, -1)
                cv2.circle(output_frame, (disp_x, disp_y), 7, (255, 255, 255), 2)
        
        # 6. Display info on result
        cv2.putText(output_frame, f"FPS: {int(fps)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(output_frame, f"Warna: {color_names[current_color_idx]}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        points_count = len(click_points)
        cv2.putText(output_frame, f"Points: {points_count}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 200, 0), 2)
        
        if points_count == 0:
            cv2.putText(output_frame, "Click objek untuk select! (r=warna, c=clear, q=exit)", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 255), 1)
        
        # 7. Display
        cv2.imshow("SAM2 General Object Segmentation", output_frame)
        cv2.setMouseCallback("SAM2 General Object Segmentation", mouse_callback)
        
        # Tangani input keyboard
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q'):
            break
        elif key == ord('r'):
            current_color_idx = (current_color_idx + 1) % len(colors)
            print(f"Warna diubah menjadi: {color_names[current_color_idx]}")
        elif key == ord('c'):
            with mouse_event_lock:
                click_points.clear()
                click_labels.clear()
            with thread_lock:
                latest_mask = None
            print("✓ Points cleared!")

finally:
    is_running = False
    worker.join(timeout=1.0)
    cap.release()
    cv2.destroyAllWindows()