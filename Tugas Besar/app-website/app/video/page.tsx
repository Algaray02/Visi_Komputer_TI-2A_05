'use client';

import { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import DetectionStats from '@/components/DetectionStats';
import ComplianceStatus from '@/components/ComplianceStatus';
import LoadingIndicator from '@/components/LoadingIndicator';

interface DetectionResult {
  with_helmet: number;
  no_helmet: number;
  motorcycle: number;
  details: any[];
  preview_image?: string;
  video_path?: string;
  total_frames?: number;
  processed_frames?: number;
  ffmpeg_converted?: boolean;
}

export default function VideoDetection() {
  const [videoFile, setVideoFile] = useState<File | null>(null);
  const [videoPreview, setVideoPreview] = useState<string | null>(null);
  const [result, setResult] = useState<DetectionResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [confidence, setConfidence] = useState(0.5);
  const [sampleRate, setSampleRate] = useState(5);
  const [processedVideoUrl, setProcessedVideoUrl] = useState<string | null>(null);
  const [videoError, setVideoError] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const videoRef = useRef<HTMLVideoElement>(null);

  const handleVideoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setVideoFile(file);
    setResult(null);
    setError(null);
    setProcessedVideoUrl(null);
    setVideoError(false);

    // Create preview URL
    const url = URL.createObjectURL(file);
    setVideoPreview(url);
  };

  const handleDetect = async () => {
    if (!videoFile) return;

    setLoading(true);
    setError(null);
    setVideoError(false);

    try {
      const formData = new FormData();
      formData.append('video', videoFile);
      formData.append('confidence_threshold', confidence.toString());
      formData.append('sample_rate', sampleRate.toString());

      const response = await axios.post<DetectionResult>(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000'}/api/detect-video`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );

      setResult(response.data);
      
      // Set video URL with timestamp to force reload
      if (response.data.video_path) {
        const videoUrl = `${process.env.NEXT_PUBLIC_API_URL || 'localhost:5000'}${response.data.video_path}?t=${Date.now()}`;
        setProcessedVideoUrl(videoUrl);
      }
    } catch (err) {
      const errorMsg = axios.isAxiosError(err)
        ? err.response?.data?.error || 'Terjadi kesalahan saat deteksi'
        : 'Terjadi kesalahan';
      setError(errorMsg);
      console.error('Detection error:', err);
    } finally {
      setLoading(false);
    }
  };

  // Force video reload when URL changes
  useEffect(() => {
    if (processedVideoUrl && videoRef.current) {
      videoRef.current.load();
    }
  }, [processedVideoUrl]);

  const handleDownload = () => {
    if (processedVideoUrl) {
      const link = document.createElement('a');
      link.href = processedVideoUrl.split('?')[0]; // Remove timestamp
      link.download = `helmet_detection_${Date.now()}.mp4`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-900 via-slate-800 to-slate-900 pt-8 pb-16">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-12">
          <h1 className="text-4xl font-bold text-transparent bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text mb-3">
            🎬 Video Detection
          </h1>
          <p className="text-slate-400 text-lg">
            Upload video untuk mendeteksi helm pada pengendara motor dengan hasil preview real-time
          </p>
        </div>

        <div className="grid lg:grid-cols-2 gap-8">
          {/* Upload Section */}
          <div className="bg-slate-800/40 backdrop-blur border border-slate-700/50 rounded-2xl p-8">
            <h2 className="text-2xl font-bold text-slate-100 mb-6">Upload Video</h2>

            <div
              className="border-2 border-dashed border-slate-600 hover:border-blue-500/50 rounded-xl p-12 text-center cursor-pointer transition-all duration-300 bg-slate-900/20"
              onClick={() => fileInputRef.current?.click()}
            >
              <div className="text-5xl mb-3">{videoFile ? '✅' : '📹'}</div>
              <p className="text-slate-400">
                {videoFile ? 'Video siap dianalisis' : 'Klik atau drag video ke sini'}
              </p>
              <p className="text-sm text-slate-500 mt-2">Format: MP4, AVI, MOV, MKV</p>
            </div>

            <input
              ref={fileInputRef}
              type="file"
              accept="video/*"
              onChange={handleVideoChange}
              className="hidden"
            />

            {videoFile && (
              <div className="mt-6 bg-slate-700/30 rounded-lg p-4 border border-slate-700/50">
                <p className="text-sm text-slate-300 font-medium">📄 {videoFile.name}</p>
                <p className="text-xs text-slate-400 mt-2">
                  Ukuran: {(videoFile.size / (1024 * 1024)).toFixed(2)} MB
                </p>
              </div>
            )}

            {/* Settings */}
            <div className="mt-8 space-y-5">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-3">
                  Confidence Threshold: <span className="text-blue-400">{(confidence * 100).toFixed(0)}%</span>
                </label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.05"
                  value={confidence}
                  onChange={(e) => setConfidence(parseFloat(e.target.value))}
                  className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-3">
                  Sample Rate: <span className="text-cyan-400">Setiap {sampleRate} frame</span>
                </label>
                <input
                  type="range"
                  min="1"
                  max="10"
                  step="1"
                  value={sampleRate}
                  onChange={(e) => setSampleRate(parseInt(e.target.value))}
                  className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-cyan-500"
                />
                <p className="text-xs text-slate-400 mt-2">
                  📊 Semakin tinggi = lebih cepat (tapi akurasi berkurang), semakin rendah = lebih akurat (lebih lambat)
                </p>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="mt-8 flex gap-3">
              <button
                onClick={handleDetect}
                disabled={!videoFile || loading}
                className="flex-1 bg-gradient-to-r from-blue-600 to-blue-500 text-white px-6 py-3 rounded-lg font-semibold hover:from-blue-700 hover:to-blue-600 disabled:from-slate-600 disabled:to-slate-600 transition-all duration-200 disabled:cursor-not-allowed"
              >
                {loading ? '⏳ Processing...' : '🎬 Mulai Deteksi'}
              </button>
              <button
                onClick={() => {
                  setVideoFile(null);
                  setVideoPreview(null);
                  setResult(null);
                  setError(null);
                  setProcessedVideoUrl(null);
                  setVideoError(false);
                  if (fileInputRef.current) fileInputRef.current.value = '';
                }}
                className="flex-1 bg-slate-700 hover:bg-slate-600 text-slate-200 px-6 py-3 rounded-lg font-semibold transition-colors"
              >
                Bersihkan
              </button>
            </div>
          </div>

          {/* Preview & Results Section */}
          <div className="bg-slate-800/40 backdrop-blur border border-slate-700/50 rounded-2xl p-8">
            <h2 className="text-2xl font-bold text-slate-100 mb-6">📹 Preview & Hasil</h2>

            {loading && <LoadingIndicator message="🎯 Processing video..." />}

            {error && (
              <div className="bg-red-500/10 text-red-400 p-5 rounded-xl border border-red-500/30 flex gap-3">
                <span className="text-2xl">❌</span>
                <div>
                  <p className="font-bold">Terjadi Kesalahan</p>
                  <p className="text-sm mt-1">{error}</p>
                </div>
              </div>
            )}

            {processedVideoUrl && (
              <div className="space-y-6">
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="font-bold text-slate-100">🎥 Video Hasil Deteksi</h3>
                    <button
                      onClick={handleDownload}
                      className="text-xs bg-blue-600 hover:bg-blue-700 text-white px-3 py-1.5 rounded-lg transition-colors"
                    >
                      📥 Download
                    </button>
                  </div>

                  {!result?.ffmpeg_converted && (
                    <div className="bg-yellow-500/10 text-yellow-400 p-3 rounded-lg border border-yellow-500/30 mb-3 text-xs">
                      ⚠️ FFmpeg tidak tersedia. Video mungkin tidak bisa diputar di browser. Gunakan tombol Download untuk menyimpan video.
                    </div>
                  )}

                  <div className="relative bg-black rounded-xl overflow-hidden">
                    <video
                      ref={videoRef}
                      key={processedVideoUrl}
                      controls
                      preload="metadata"
                      playsInline
                      className="w-full"
                      style={{ maxHeight: '400px' }}
                      onError={() => setVideoError(true)}
                      onLoadedData={() => setVideoError(false)}
                    >
                      <source src={processedVideoUrl} type="video/mp4" />
                      Browser Anda tidak mendukung tag video.
                    </video>

                    {videoError && (
                      <div className="absolute inset-0 flex items-center justify-center bg-slate-900/90">
                        <div className="text-center p-6">
                          <div className="text-4xl mb-3">⚠️</div>
                          <p className="text-slate-300 text-sm mb-4">
                            Video tidak bisa diputar di browser
                          </p>
                          <button
                            onClick={handleDownload}
                            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm transition-colors"
                          >
                            📥 Download Video
                          </button>
                        </div>
                      </div>
                    )}
                  </div>

                  <p className="text-xs text-slate-400 mt-2">
                    💡 Jika video tidak bisa diputar, klik tombol Download untuk menyimpan dan putar dengan media player
                  </p>
                </div>

                {result?.preview_image && (
                  <div>
                    <h3 className="font-bold text-slate-100 mb-3">📸 Preview Frame</h3>
                    <img
                      src={result.preview_image}
                      alt="Preview"
                      className="w-full rounded-xl border border-slate-700/50"
                    />
                  </div>
                )}

                {result && (
                  <>
                    <DetectionStats
                      withHelmet={result.with_helmet}
                      noHelmet={result.no_helmet}
                      motorcycle={result.motorcycle}
                    />

                    <div>
                      <h3 className="font-bold text-slate-100 mb-3">Safety Compliance</h3>
                      <ComplianceStatus
                        withHelmet={result.with_helmet}
                        noHelmet={result.no_helmet}
                      />
                    </div>

                    {result.details && result.details.length > 0 && (
                      <div>
                        <h3 className="font-bold text-slate-100 mb-3">📋 Detail Deteksi</h3>
                        <div className="bg-slate-900/50 rounded-lg border border-slate-700/50 max-h-64 overflow-y-auto">
                          <div className="space-y-2 p-4">
                            {result.details.slice(0, 20).map((detail, idx) => (
                              <div
                                key={idx}
                                className="bg-slate-800/50 p-2 rounded border border-slate-700/30 text-xs text-slate-300"
                              >
                                <span className="font-medium text-slate-100">{detail.class}</span>
                                <span className="text-slate-500"> • </span>
                                <span className="text-blue-400">{detail.confidence}</span>
                                {detail.frame && (
                                  <>
                                    <span className="text-slate-500"> • </span>
                                    <span className="text-slate-400">Frame {detail.frame}</span>
                                  </>
                                )}
                              </div>
                            ))}
                            {result.details.length > 20 && (
                              <p className="text-xs text-slate-400 pt-2">+{result.details.length - 20} lebih banyak</p>
                            )}
                          </div>
                        </div>
                      </div>
                    )}

                    {result.total_frames && (
                      <div className="bg-slate-700/30 rounded-lg p-4 border border-slate-700/50 text-sm text-slate-300">
                        <p>📊 Total frames: {result.total_frames} | Diproses: {result.processed_frames}</p>
                      </div>
                    )}
                  </>
                )}
              </div>
            )}

            {!loading && !processedVideoUrl && !error && (
              <div className="text-center text-slate-400 py-16">
                <div className="text-5xl mb-3">🎯</div>
                <p className="text-lg">Upload video untuk memulai deteksi</p>
                <p className="text-sm text-slate-500 mt-2">Video akan diproses dan hasilnya ditampilkan langsung di sini</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}