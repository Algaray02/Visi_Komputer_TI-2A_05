export default function About() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-900 via-slate-800 to-slate-900 pt-8 pb-16">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-12">
          <h1 className="text-4xl font-bold text-transparent bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text mb-3">
            ℹ️ Tentang Aplikasi Ini
          </h1>
          <p className="text-slate-400 text-lg">
            Sistem deteksi helm berbasis AI untuk meningkatkan keselamatan berkendara
          </p>
        </div>

        {/* Main Features */}
        <div className="bg-slate-800/40 backdrop-blur border border-slate-700/50 rounded-2xl p-8 mb-8">
          <h2 className="text-2xl font-bold text-slate-100 mb-6">🎯 Fitur Utama</h2>
          <div className="grid md:grid-cols-2 gap-6">
            <div className="flex gap-4">
              <span className="text-3xl">✅</span>
              <div>
                <p className="font-semibold text-slate-100">Deteksi Helm Real-time</p>
                <p className="text-sm text-slate-400 mt-1">
                  Mendeteksi penggunaan helm pada pengendara motor dengan akurasi tinggi
                </p>
              </div>
            </div>
            <div className="flex gap-4">
              <span className="text-3xl">📊</span>
              <div>
                <p className="font-semibold text-slate-100">Analisis Kepatuhan</p>
                <p className="text-sm text-slate-400 mt-1">
                  Analisis compliance keselamatan berkendara secara real-time
                </p>
              </div>
            </div>
            <div className="flex gap-4">
              <span className="text-3xl">📷</span>
              <div>
                <p className="font-semibold text-slate-100">Support Gambar</p>
                <p className="text-sm text-slate-400 mt-1">
                  Upload dan analisis foto pengendara dengan mudah
                </p>
              </div>
            </div>
            <div className="flex gap-4">
              <span className="text-3xl">🎬</span>
              <div>
                <p className="font-semibold text-slate-100">Support Video</p>
                <p className="text-sm text-slate-400 mt-1">
                  Proses video dengan preview hasil deteksi langsung
                </p>
              </div>
            </div>
            <div className="flex gap-4">
              <span className="text-3xl">📹</span>
              <div>
                <p className="font-semibold text-slate-100">Live Camera</p>
                <p className="text-sm text-slate-400 mt-1">
                  Deteksi real-time langsung dari perangkat Anda
                </p>
              </div>
            </div>
            <div className="flex gap-4">
              <span className="text-3xl">⚙️</span>
              <div>
                <p className="font-semibold text-slate-100">Konfigurable</p>
                <p className="text-sm text-slate-400 mt-1">
                  Sesuaikan confidence threshold sesuai kebutuhan
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Detection Classes */}
        <div className="bg-slate-800/40 backdrop-blur border border-slate-700/50 rounded-2xl p-8 mb-8">
          <h2 className="text-2xl font-bold text-slate-100 mb-6">📋 Kelas Deteksi</h2>
          <div className="grid md:grid-cols-3 gap-4">
            <div className="bg-emerald-500/10 border border-emerald-500/30 p-5 rounded-xl">
              <p className="font-bold text-lg text-emerald-400 mb-2">🟢 Pakai Helm</p>
              <p className="text-sm text-slate-400">
                Pengendara yang mengenakan helm dengan benar
              </p>
            </div>
            <div className="bg-red-500/10 border border-red-500/30 p-5 rounded-xl">
              <p className="font-bold text-lg text-red-400 mb-2">🔴 Tanpa Helm</p>
              <p className="text-sm text-slate-400">
                Pengendara yang tidak mengenakan helm
              </p>
            </div>
            <div className="bg-blue-500/10 border border-blue-500/30 p-5 rounded-xl">
              <p className="font-bold text-lg text-blue-400 mb-2">🟠 Motor</p>
              <p className="text-sm text-slate-400">
                Kendaraan roda dua (motor/scooter)
              </p>
            </div>
          </div>
        </div>

        {/* Safety Levels */}
        <div className="bg-slate-800/40 backdrop-blur border border-slate-700/50 rounded-2xl p-8 mb-8">
          <h2 className="text-2xl font-bold text-slate-100 mb-6">🏆 Tingkat Keselamatan</h2>
          <div className="grid md:grid-cols-4 gap-4">
            <div className="bg-emerald-500/10 border border-emerald-500/30 p-4 rounded-xl text-center">
              <p className="font-bold text-lg text-emerald-400">✅ 100%</p>
              <p className="text-xs text-slate-400 mt-2">Semua aman</p>
            </div>
            <div className="bg-emerald-500/10 border border-emerald-500/30 p-4 rounded-xl text-center">
              <p className="font-bold text-lg text-emerald-400">✅ 80-99%</p>
              <p className="text-xs text-slate-400 mt-2">Sebagian besar aman</p>
            </div>
            <div className="bg-amber-500/10 border border-amber-500/30 p-4 rounded-xl text-center">
              <p className="font-bold text-lg text-amber-400">⚠️ 50-79%</p>
              <p className="text-xs text-slate-400 mt-2">Menengah</p>
            </div>
            <div className="bg-red-500/10 border border-red-500/30 p-4 rounded-xl text-center">
              <p className="font-bold text-lg text-red-400">❌ &lt;50%</p>
              <p className="text-xs text-slate-400 mt-2">Sangat berbahaya</p>
            </div>
          </div>
        </div>

        {/* Model Information */}
        <div className="bg-gradient-to-r from-blue-500/10 to-cyan-500/10 border border-blue-500/30 rounded-2xl p-8 mb-8">
          <h2 className="text-2xl font-bold text-slate-100 mb-6">🤖 Informasi Model AI</h2>
          <div className="grid md:grid-cols-2 gap-6">
            <div className="space-y-3">
              <p className="text-slate-300">
                <span className="font-bold text-blue-400">Model:</span> YOLOv11 (State-of-the-art)
              </p>
              <p className="text-slate-300">
                <span className="font-bold text-blue-400">Framework:</span> Ultralytics YOLO
              </p>
              <p className="text-slate-300">
                <span className="font-bold text-blue-400">Classes:</span> 3 (pakai helm, tanpa helm, motor)
              </p>
            </div>
            <div className="space-y-3">
              <p className="text-slate-300">
                <span className="font-bold text-cyan-400">Training Data:</span> 18,731+ images
              </p>
              <p className="text-slate-300">
                <span className="font-bold text-cyan-400">Dataset:</span> 14 sumber berbeda
              </p>
              <p className="text-slate-300">
                <span className="font-bold text-cyan-400">Akurasi:</span> High precision detection
              </p>
            </div>
          </div>
        </div>

        {/* Technology Stack */}
        <div className="bg-slate-800/40 backdrop-blur border border-slate-700/50 rounded-2xl p-8 mb-8">
          <h2 className="text-2xl font-bold text-slate-100 mb-6">⚙️ Technology Stack</h2>
          <div className="grid md:grid-cols-2 gap-8">
            <div>
              <h3 className="font-bold text-lg text-slate-100 mb-4">Frontend</h3>
              <ul className="text-sm text-slate-400 space-y-2">
                <li className="flex gap-2"><span className="text-blue-400">▸</span> Next.js 16 (React Framework)</li>
                <li className="flex gap-2"><span className="text-blue-400">▸</span> TypeScript</li>
                <li className="flex gap-2"><span className="text-blue-400">▸</span> Tailwind CSS 3.4</li>
                <li className="flex gap-2"><span className="text-blue-400">▸</span> Axios (HTTP Client)</li>
              </ul>
            </div>
            <div>
              <h3 className="font-bold text-lg text-slate-100 mb-4">Backend</h3>
              <ul className="text-sm text-slate-400 space-y-2">
                <li className="flex gap-2"><span className="text-cyan-400">▸</span> Python 3.8+</li>
                <li className="flex gap-2"><span className="text-cyan-400">▸</span> Flask 2.3</li>
                <li className="flex gap-2"><span className="text-cyan-400">▸</span> OpenCV</li>
                <li className="flex gap-2"><span className="text-cyan-400">▸</span> Ultralytics YOLO</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Usage Guidelines */}
        <div className="bg-slate-800/40 backdrop-blur border border-slate-700/50 rounded-2xl p-8 mb-8">
          <h2 className="text-2xl font-bold text-slate-100 mb-6">📖 Panduan Penggunaan</h2>
          <div className="space-y-4">
            <div className="flex gap-4">
              <div className="text-2xl">1️⃣</div>
              <div>
                <p className="font-bold text-slate-100">Image Detection</p>
                <p className="text-sm text-slate-400 mt-1">
                  Upload foto pengendara motor untuk mendeteksi penggunaan helm dan mendapatkan hasil analisis.
                </p>
              </div>
            </div>
            <div className="flex gap-4">
              <div className="text-2xl">2️⃣</div>
              <div>
                <p className="font-bold text-slate-100">Video Detection</p>
                <p className="text-sm text-slate-400 mt-1">
                  Upload video untuk analisis helm pada seluruh durasi video. Hasil akan menampilkan video yang sudah diberi anotasi deteksi.
                </p>
              </div>
            </div>
            <div className="flex gap-4">
              <div className="text-2xl">3️⃣</div>
              <div>
                <p className="font-bold text-slate-100">Camera Detection</p>
                <p className="text-sm text-slate-400 mt-1">
                  Gunakan kamera perangkat untuk real-time detection. Sistem akan melakukan deteksi setiap beberapa detik secara otomatis.
                </p>
              </div>
            </div>
            <div className="flex gap-4">
              <div className="text-2xl">⚙️</div>
              <div>
                <p className="font-bold text-slate-100">Confidence Threshold</p>
                <p className="text-sm text-slate-400 mt-1">
                  Sesuaikan tingkat kepercayaan deteksi (semakin tinggi = semakin akurat tapi mungkin ada yang terlewat).
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Safety Information */}
        <div className="bg-gradient-to-r from-amber-500/10 to-orange-500/10 border border-amber-500/30 rounded-2xl p-8">
          <h2 className="text-2xl font-bold text-slate-100 mb-4">⚠️ Informasi Keselamatan</h2>
          <p className="text-slate-300 mb-4">
            Sistem ini dirancang untuk mendukung enforcement keselamatan berkendara. Penggunaan helm tetap merupakan tanggung jawab pengemudi untuk:
          </p>
          <ul className="text-slate-300 space-y-2">
            <li className="flex gap-3">
              <span className="text-amber-400">✓</span>
              <span>Memenuhi persyaratan hukum lokal tentang penggunaan helm</span>
            </li>
            <li className="flex gap-3">
              <span className="text-amber-400">✓</span>
              <span>Mengurangi risiko cedera kepala secara signifikan</span>
            </li>
            <li className="flex gap-3">
              <span className="text-amber-400">✓</span>
              <span>Meningkatkan kesadaran keselamatan diri sendiri dan pengguna jalan lainnya</span>
            </li>
            <li className="flex gap-3">
              <span className="text-amber-400">✓</span>
              <span>Melindungi diri dan penumpang dari kecelakaan</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}
