# Perbandingan SAM2 vs Hair Segmenter (MediaPipe)

## 📌 Overview

Kedua kode melakukan segmentasi rambut untuk mengganti warna, namun menggunakan model dan pendekatan yang **sangat berbeda**.

---

## 1. **Model yang Digunakan**

### SAM2 (Segment Anything Model 2)

```python
sam2_checkpoint = "sam2.1_hiera_tiny.pt"
model_cfg = "sam2.1_hiera_t.yaml"
```

- **Ukuran Model**: ~80MB (tiny), 500MB (large)
- **Tipe Model**: Vision Transformer (ViT) - General Purpose
- **Keunggulan**: Bisa segment **banyak objek**, tidak hanya rambut
- **Kelemahan**: Lebih berat, membutuhkan GPU yang decent
- **Download**: Harus di-download manual (~2.5GB untuk versi large)

### Hair Segmenter (MediaPipe)

```python
MODEL_PATH = 'hair_segmenter.tflite'
```

- **Ukuran Model**: ~3MB (sangat kecil!)
- **Tipe Model**: TensorFlow Lite - Specialized Task
- **Keunggulan**: Ringan, cepat, khusus untuk rambut, bisa CPU-only
- **Kelemahan**: **Hanya bisa segment rambut**, tidak generic
- **Format**: `.tflite` - built-in di MediaPipe

---

## 2. **Arsitektur & Pendekatan**

| Aspek            | SAM2                              | Hair Segmenter               |
| ---------------- | --------------------------------- | ---------------------------- |
| **Framework**    | PyTorch + SAM2 Library            | MediaPipe (Google)           |
| **Input Prompt** | Points + Labels (interactive)     | Direct image (automatic)     |
| **Output**       | Masks dengan confidence scores    | Category mask (probabilitas) |
| **Inference**    | Butuh GPU, multimask output       | CPU-friendly, single output  |
| **Processing**   | Threading (background processing) | Single thread (blocking)     |

### SAM2 - Interactive Approach

```python
# Butuh points untuk tell model area mana yg rambut
points = np.array([
    [w_small // 2, h_small // 5],
    [w_small // 2, h_small // 4],
    ...
])
masks, scores, _ = predictor.predict(
    point_coords=points,
    point_labels=labels,  # 1=foreground, 0=background
    multimask_output=False
)
```

**Cara kerja**: Model mendengarkan instruksi berupa titik/points, baru bikin mask

### Hair Segmenter - Automatic Approach

```python
# Langsung segment tanpa perlu points
segmentation_result = segmenter.segment(image)
category_mask = segmentation_result.category_mask

# Threshold untuk get binary mask
condition = category_mask.numpy_view() > 0.2
```

**Cara kerja**: Model langsung tahu rambut itu apa, tidak perlu instruksi

---

## 3. **Performa & Kecepatan**

| Metrik             | SAM2 (Tiny)                    | Hair Segmenter        |
| ------------------ | ------------------------------ | --------------------- |
| **Model Size**     | 80MB                           | 3MB                   |
| **Inference Time** | ~200-500ms per frame           | ~50-100ms per frame   |
| **FPS (típico)**   | 2-5 FPS (CPU), 10-20 FPS (GPU) | 10-30 FPS (CPU only!) |
| **Memory**         | 2GB+ (GPU)                     | 100-300MB             |
| **Device Support** | GPU/CPU (GPU recommended)      | CPU only              |

**Mengapa SAM2 lebih lambat?**

- Model besar (Vision Transformer)
- Proses kompleks dengan attention mechanisms
- Butuh infer pada resolution penuh

**Mengapa Hair Segmenter lebih cepat?**

- Model tiny (3MB)
- Specialized untuk 1 task saja
- Optimized dengan TensorFlow Lite

---

## 4. **Kualitas Hasil**

### SAM2

✅ **Keuntungan:**

- Lebih akurat untuk hair segmentation kompleks
- Bisa handle berbagai pose kepala
- Consistent dengan berbagai lighting
- Bisa refine dengan points tambahan

❌ **Kekurangan:**

- Kadang over-segment (include shoulder/neck)
- Sensitif terhadap placement points

### Hair Segmenter

✅ **Keuntungan:**

- Khusus training untuk rambut → lebih smooth mask
- Tidak ambil background secara tidak sengaja
- Konsisten untuk hair boundaries

❌ **Kekurangan:**

- Bisa miss area rambut yang ada shadows
- Tidak adaptif seperti SAM2
- Trained untuk wajah frontal

---

## 5. **Threading & Optimisasi**

### SAM2 - Multi-threading

```python
def ai_worker_thread():
    while is_running:
        # Process frame di background thread
        predictor.set_image(frame_rgb)
        masks, scores, _ = predictor.predict(...)

# Main thread tetap smooth
worker = threading.Thread(target=ai_worker_thread)
worker.daemon = True
worker.start()
```

**Benefit**: Main thread tetap responsive untuk UI, AI process di background

### Hair Segmenter - Single Thread

```python
# Process blocking di main thread
segmentation_result = segmenter.segment(image)
```

**Benefit**: Lebih simple, tapi bisa lag kalau processing lambat

---

## 6. **Use Case: Kapan Pakai Apa?**

### Gunakan **SAM2** jika:

- ✅ Butuh segmentasi yang fleksibel (multi-object)
- ✅ Punya GPU yang decent
- ✅ User bisa click untuk select area
- ✅ Butuh high accuracy
- ✅ Contoh: Photo editing app professional

### Gunakan **Hair Segmenter** jika:

- ✅ Hanya fokus hair segmentation
- ✅ Device terbatas (laptop, smartphone)
- ✅ Butuh FPS tinggi real-time
- ✅ Battery consumption penting
- ✅ Contoh: Mobile app, live streaming

---

## 7. **Perbandingan Kode Side-by-Side**

### Initialization

```python
# SAM2
sam2_model = build_sam2(model_cfg, sam2_checkpoint, device=device)
predictor = SAM2ImagePredictor(sam2_model)

# Hair Segmenter
options = vision.ImageSegmenterOptions(base_options=base_options)
segmenter = vision.ImageSegmenter.create_from_options(options)
```

### Segmentation

```python
# SAM2
masks, scores, _ = predictor.predict(
    point_coords=points,
    point_labels=labels,
    multimask_output=False
)
generated_mask = masks[0].astype(np.uint8) * 255

# Hair Segmenter
segmentation_result = segmenter.segment(image)
category_mask = segmentation_result.category_mask
condition = category_mask.numpy_view() > 0.2
```

### Color Blending

```python
# SAM2 - Smooth blending dengan addWeighted
output_frame[hair_region] = cv2.addWeighted(
    frame[hair_region], 0.6,
    colored_layer[hair_region], 0.4,
    0
)

# Hair Segmenter - Direct replacement
output_image = np.where(condition, hair_overlay, frame_rgb)
```

---

## 8. **Kesimpulan Akhir**

| Aspek             | Winner            | Alasan                 |
| ----------------- | ----------------- | ---------------------- |
| **Kecepatan**     | 🎯 Hair Segmenter | 5-10x lebih cepat      |
| **Akurasi**       | 🎯 SAM2           | Lebih robust           |
| **Efisiensi**     | 🎯 Hair Segmenter | 26x lebih kecil        |
| **Fleksibilitas** | 🎯 SAM2           | Generic, multi-purpose |
| **Hardware**      | 🎯 Hair Segmenter | CPU-only cukup         |
| **Mobile-ready**  | 🎯 Hair Segmenter | Designed untuk mobile  |

---

## 📊 Rekomendasi untuk Tugas Ini

Untuk **university project** (performa vs accuracy):

- **Pakai SAM2** jika punya GPU + waktu
- **Pakai Hair Segmenter** jika laptop performance rendah
- **Kombinasi**: Gunakan Hair Segmenter untuk real-time preview, SAM2 untuk final export quality

```python
# Best practice hybrid approach
if device == "cuda":
    use_sam2 = True  # Accuracy priority
else:
    use_sam2 = False  # Speed priority
```

---

**Created**: November 27, 2025  
**For**: Visi Komputer - Tugas 5
