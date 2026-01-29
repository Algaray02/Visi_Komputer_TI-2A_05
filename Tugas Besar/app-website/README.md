# 🏍️ Helmet Detection System - Web Version

Modern web application untuk deteksi helm pada pengendara motor menggunakan YOLOv11 dan Next.js.

## ✨ Features

- ✅ **Image Detection** - Upload gambar untuk deteksi helm
- ✅ **Video Detection** - Proses video dengan anotasi otomatis
- ✅ **Live Camera** - Real-time detection dari webcam
- ✅ **Safety Analysis** - Compliance rate dan statistik keselamatan
- ✅ **Responsive Design** - Mobile-friendly interface
- ✅ **Production Ready** - Optimized untuk deployment

## 📋 Tech Stack

### Frontend
- **Framework**: Next.js 15
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **HTTP Client**: Axios

### Backend
- **Framework**: Flask (Python)
- **Model**: YOLOv11 (Ultralytics)
- **Video Processing**: OpenCV
- **Server**: Gunicorn

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.8+
- npm atau yarn

### Installation

#### 1. Backend Setup

```bash
# Install Python dependencies
pip install -r ../requirements.txt

# Run Flask backend
python ../app_backend.py
```

Backend akan berjalan di `http://localhost:5000`

#### 2. Frontend Setup

```bash
# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend akan berjalan di `http://localhost:3000`

### 3. Akses Aplikasi

Open http://localhost:3000 di browser Anda

---

## 🎮 Usage Guide

### Image Detection
1. Navigate to **📷 Image** tab
2. Click upload area atau drag gambar
3. Adjust confidence threshold (optional)
4. Click **🔍 Detect**
5. Lihat hasil dengan statistik dan compliance analysis

### Video Detection
1. Navigate to **🎬 Video** tab
2. Upload video file
3. Configure settings (confidence, sample rate)
4. Click **🎬 Start Detection**
5. Preview video hasil dengan anotasi deteksi

### Camera Detection
1. Navigate to **📹 Camera** tab
2. Click **📹 Start Camera**
3. Browser akan request camera permission
4. Live detection akan berjalan otomatis
5. Lihat hasil real-time di panel kanan

---

## 🚀 Production Deployment

For detailed deployment guide, see [DEPLOYMENT_GUIDE.md](../DEPLOYMENT_GUIDE.md)

### Quick Deploy Options

1. **Vercel (Frontend)** - Best for Next.js
2. **Railway.app (Backend)** - Easy Python deployment
3. **Google Cloud Run** - Scalable serverless
4. **Render.com** - Free tier available

---

## 💡 Tips

- Adjust confidence threshold untuk akurasi yang lebih baik
- Use camera feature untuk real-time monitoring
- Video processing lebih akurat dengan sample rate yang lebih rendah
- Deployment ke Vercel + Railway recommended untuk production

Selamat mencoba! 🏍️
