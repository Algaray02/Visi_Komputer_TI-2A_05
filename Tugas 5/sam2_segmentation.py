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

def ai_worker_thread():
    """Thread khusus untuk menjalankan SAM2 di background"""
    global current_frame_for_ai, latest_mask, is_running
    
    while is_running:
        frame_to_process = None
        
        # Ambil frame terbaru dari main thread dengan aman
        with thread_lock:
            if current_frame_for_ai is not None:
                frame_to_process = current_frame_for_ai.copy()
                current_frame_for_ai = None # Reset agar tidak memproses ulang frame yang sama

        if frame_to_process is not None:
            try:
                # 1. Resize untuk kecepatan
                h_orig, w_orig = frame_to_process.shape[:2]
                frame_small = cv2.resize(frame_to_process, INFERENCE_SIZE)
                h_small, w_small = frame_small.shape[:2]
                
                # 2. Konversi ke RGB dan Set Image
                frame_rgb = cv2.cvtColor(frame_small, cv2.COLOR_BGR2RGB)
                predictor.set_image(frame_rgb)
                
                # 3. Prompt Points (Area Kepala/Rambut)
                points = np.array([
                    [w_small // 2, h_small // 5],      # Tengah agak atas
                    [w_small // 2, h_small // 4],      # Tengah
                    [w_small // 3, h_small // 3],      # Kiri
                    [2 * w_small // 3, h_small // 3],  # Kanan
                ])
                labels = np.array([1, 1, 1, 1])

                # 4. Prediksi Mask
                masks, scores, _ = predictor.predict(
                    point_coords=points,
                    point_labels=labels,
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

print("Tekan 'q' untuk keluar, 'r' untuk ganti warna")

fps_clock = cv2.getTickCount()

try:
    while True:
        ret, frame = cap.read()
        if not ret: break
        
        frame = cv2.resize(frame, (640, 480))
        
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
            
            # Blend area rambut
            # Area dimana mask > 0
            hair_region = mask_blur > 0
            
            # Cara cepat blending: Weighted Add
            output_frame[hair_region] = cv2.addWeighted(
                frame[hair_region], 0.6, 
                colored_layer[hair_region], 0.4, 
                0
            )

        # 4. Hitung FPS (Visual Only)
        fps = cv2.getTickFrequency() / (cv2.getTickCount() - fps_clock)
        fps_clock = cv2.getTickCount()
        
        cv2.putText(output_frame, f"FPS: {int(fps)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(output_frame, f"Warna: {color_names[current_color_idx]}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        cv2.imshow("Smooth SAM2 Hair Color", output_frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('r'):
            current_color_idx = (current_color_idx + 1) % len(colors)

finally:
    is_running = False
    worker.join(timeout=1.0)
    cap.release()
    cv2.destroyAllWindows()