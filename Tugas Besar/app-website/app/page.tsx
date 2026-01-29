'use client';

import { useState, useRef } from 'react';
import Image from 'next/image';
import axios from 'axios';
import DetectionStats from '@/components/DetectionStats';
import ComplianceStatus from '@/components/ComplianceStatus';
import LoadingIndicator from '@/components/LoadingIndicator';

interface Detection {
  class: string;
  confidence: string;
  bbox?: [number, number, number, number];
}

interface DetectionResult {
  with_helmet: number;
  no_helmet: number;
  motorcycle: number;
  details: Detection[];
  processed_image?: string;
}

export default function ImageDetection() {
  const [image, setImage] = useState<string | null>(null);
  const [result, setResult] = useState<DetectionResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [confidence, setConfidence] = useState(0.5);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleImageChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Preview image
    const reader = new FileReader();
    reader.onload = (event) => {
      setImage(event.target?.result as string);
      setResult(null);
      setError(null);
    };
    reader.readAsDataURL(file);
  };

  const handleDetect = async () => {
    if (!image) return;

    setLoading(true);
    setError(null);

    try {
      const response = await axios.post<DetectionResult>(
        `${process.env.NEXT_PUBLIC_API_URL || 'https://helmdect.api.algaray.biz.id'}/api/detect-image`,
        {
          image: image,
          confidence_threshold: confidence,
        }
      );

      setResult(response.data);
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

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-900 via-slate-800 to-slate-900 pt-8 pb-16">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-12">
          <h1 className="text-4xl font-bold text-transparent bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text mb-3">
            📷 Image Detection
          </h1>
          <p className="text-slate-400 text-lg">
            Upload gambar untuk mendeteksi helm pada pengendara motor dengan AI
          </p>
        </div>

        <div className="grid lg:grid-cols-2 gap-8">
          {/* Upload Section */}
          <div className="bg-slate-800/40 backdrop-blur border border-slate-700/50 rounded-2xl p-8">
            <h2 className="text-2xl font-bold text-slate-100 mb-6">Upload Gambar</h2>

            <div
              className="border-2 border-dashed border-slate-600 hover:border-blue-500/50 rounded-xl p-12 text-center cursor-pointer transition-all duration-300 bg-slate-900/20"
              onClick={() => fileInputRef.current?.click()}
            >
              <div className="text-5xl mb-3">{image ? '✅' : '📁'}</div>
              <p className="text-slate-400">
                {image ? 'Gambar siap dianalisis' : 'Klik atau drag gambar ke sini'}
              </p>
              <p className="text-sm text-slate-500 mt-2">Format: JPG, PNG, WebP</p>
            </div>

            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleImageChange}
              className="hidden"
            />

            {image && !result && (
              <div className="mt-8">
                <p className="text-sm text-slate-400 mb-3">Preview Original:</p>
                <img
                  src={image}
                  alt="Preview"
                  className="max-h-80 rounded-xl mx-auto border border-slate-700/50"
                />
              </div>
            )}

            {/* Settings */}
            <div className="mt-8 space-y-4">
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
                <div className="flex justify-between text-xs text-slate-500 mt-1">
                  <span>Rendah (0%)</span>
                  <span>Tinggi (100%)</span>
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="mt-8 flex gap-3">
              <button
                onClick={handleDetect}
                disabled={!image || loading}
                className="flex-1 bg-gradient-to-r from-blue-600 to-blue-500 text-white px-6 py-3 rounded-lg font-semibold hover:from-blue-700 hover:to-blue-600 disabled:from-slate-600 disabled:to-slate-600 transition-all duration-200 disabled:cursor-not-allowed"
              >
                {loading ? '⏳ Processing...' : '🔍 Deteksi'}
              </button>
              <button
                onClick={() => {
                  setImage(null);
                  setResult(null);
                  setError(null);
                  if (fileInputRef.current) fileInputRef.current.value = '';
                }}
                className="flex-1 bg-slate-700 hover:bg-slate-600 text-slate-200 px-6 py-3 rounded-lg font-semibold transition-colors"
              >
                Bersihkan
              </button>
            </div>
          </div>

          {/* Results Section */}
          <div className="bg-slate-800/40 backdrop-blur border border-slate-700/50 rounded-2xl p-8">
            <h2 className="text-2xl font-bold text-slate-100 mb-6">📊 Hasil Analisis</h2>

            {loading && <LoadingIndicator message="🔍 Mendeteksi helm..." />}

            {error && (
              <div className="bg-red-500/10 text-red-400 p-5 rounded-xl border border-red-500/30 flex gap-3">
                <span className="text-2xl">❌</span>
                <div>
                  <p className="font-bold">Terjadi Kesalahan</p>
                  <p className="text-sm mt-1">{error}</p>
                </div>
              </div>
            )}

            {result && (
              <div className="space-y-6">
                {/* Processed Image Preview */}
                {result.processed_image && (
                  <div className="bg-slate-900/40 border border-slate-700/50 rounded-xl p-4">
                    <p className="text-sm text-slate-400 mb-3">📸 Hasil Deteksi:</p>
                    <img
                      src={result.processed_image}
                      alt="Processed"
                      className="w-full rounded-lg border border-slate-700/50"
                    />
                  </div>
                )}

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

                {result.details.length > 0 && (
                  <div>
                    <h3 className="font-bold text-slate-100 mb-3">🔍 Detail Deteksi ({result.details.length})</h3>
                    <div className="space-y-2 max-h-64 overflow-y-auto">
                      {result.details.map((detection, idx) => (
                        <div
                          key={idx}
                          className="bg-slate-700/30 p-3 rounded-lg flex justify-between border border-slate-700/50 text-sm"
                        >
                          <span className="font-semibold text-slate-200">{detection.class}</span>
                          <span className="text-blue-400">{detection.confidence}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {!loading && !result && !error && (
              <div className="text-center text-slate-400 py-16">
                <div className="text-5xl mb-3">🎯</div>
                <p className="text-lg">Upload gambar untuk memulai deteksi</p>
                <p className="text-sm text-slate-500 mt-2">Kami akan menganalisis dan memberikan hasil dalam hitungan detik</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
