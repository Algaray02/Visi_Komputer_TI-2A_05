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
}

export default function CameraDetection() {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [cameraActive, setCameraActive] = useState(false);
  const [result, setResult] = useState<DetectionResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [confidence, setConfidence] = useState(0.5);
  const [detectionInterval, setDetectionInterval] = useState<NodeJS.Timeout | null>(null);

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 1280 },
          height: { ideal: 720 },
          facingMode: 'environment',
        },
      });

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        setCameraActive(true);
        setError(null);

        // Start detection every 2 seconds
        const interval = setInterval(() => {
          captureAndDetect();
        }, 2000);
        setDetectionInterval(interval);
      }
    } catch (err) {
      const errorMsg =
        err instanceof Error ? err.message : 'Failed to access camera';
      setError(errorMsg);
      console.error('Camera error:', err);
    }
  };

  const stopCamera = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      const stream = videoRef.current.srcObject as MediaStream;
      stream.getTracks().forEach((track) => track.stop());
      setCameraActive(false);
    }

    if (detectionInterval) {
      clearInterval(detectionInterval);
      setDetectionInterval(null);
    }
  };

  const captureAndDetect = async () => {
    if (!videoRef.current || !canvasRef.current) return;

    try {
      const context = canvasRef.current.getContext('2d');
      if (!context) return;

      canvasRef.current.width = videoRef.current.videoWidth;
      canvasRef.current.height = videoRef.current.videoHeight;

      context.drawImage(videoRef.current, 0, 0);

      const imageData = canvasRef.current.toDataURL('image/jpeg');

      const response = await axios.post<DetectionResult>(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000'}/api/detect-image`,
        {
          image: imageData,
          confidence_threshold: confidence,
        }
      );

      setResult(response.data);
    } catch (err) {
      console.error('Detection error:', err);
    }
  };

  useEffect(() => {
    return () => {
      stopCamera();
    };
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-900 via-slate-800 to-slate-900 pt-8 pb-16">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-12">
          <h1 className="text-4xl font-bold text-transparent bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text mb-3">
            📹 Camera Detection
          </h1>
          <p className="text-slate-400 text-lg">
            Gunakan kamera untuk real-time helmet detection dengan statistik langsung
          </p>
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Camera Feed */}
          <div className="lg:col-span-2 bg-slate-800/40 backdrop-blur border border-slate-700/50 rounded-2xl p-8">
            <h2 className="text-2xl font-bold text-slate-100 mb-6">🎥 Live Feed</h2>

            <div className="relative bg-slate-900 rounded-xl overflow-hidden border border-slate-700/50 mb-6">
              <video
                ref={videoRef}
                autoPlay
                playsInline
                className="w-full aspect-video object-cover"
                onLoadedMetadata={() => {
                  if (videoRef.current) {
                    canvasRef.current!.width = videoRef.current.videoWidth;
                    canvasRef.current!.height = videoRef.current.videoHeight;
                  }
                }}
              />
              {cameraActive && (
                <div className="absolute top-4 right-4 flex items-center gap-2 bg-red-500/20 px-3 py-2 rounded-lg border border-red-500/50">
                  <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
                  <span className="text-sm font-semibold text-red-400">Live</span>
                </div>
              )}
            </div>

            <canvas ref={canvasRef} className="hidden" />

            {/* Settings */}
            <div className="bg-slate-700/30 border border-slate-700/50 rounded-xl p-5 mb-6">
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
                disabled={!cameraActive}
                className="w-full h-2 bg-slate-600 rounded-lg appearance-none cursor-pointer accent-blue-500 disabled:opacity-50"
              />
            </div>

            {/* Control Buttons */}
            <div className="flex gap-3">
              {!cameraActive ? (
                <button
                  onClick={startCamera}
                  className="flex-1 bg-gradient-to-r from-emerald-600 to-emerald-500 text-white px-6 py-3 rounded-lg font-semibold hover:from-emerald-700 hover:to-emerald-600 transition-all duration-200"
                >
                  📹 Mulai Kamera
                </button>
              ) : (
                <button
                  onClick={stopCamera}
                  className="flex-1 bg-gradient-to-r from-red-600 to-red-500 text-white px-6 py-3 rounded-lg font-semibold hover:from-red-700 hover:to-red-600 transition-all duration-200"
                >
                  ⏹️ Matikan Kamera
                </button>
              )}
            </div>

            {error && (
              <div className="mt-6 bg-red-500/10 text-red-400 p-5 rounded-xl border border-red-500/30 flex gap-3">
                <span className="text-2xl">❌</span>
                <div>
                  <p className="font-bold">Kesalahan Kamera</p>
                  <p className="text-sm mt-1">{error}</p>
                </div>
              </div>
            )}
          </div>

          {/* Results Sidebar */}
          <div className="bg-slate-800/40 backdrop-blur border border-slate-700/50 rounded-2xl p-8 h-fit">
            <h2 className="text-2xl font-bold text-slate-100 mb-6">📊 Live Results</h2>

            {!cameraActive && !error && (
              <div className="text-center text-slate-400 py-12">
                <div className="text-4xl mb-3">🎯</div>
                <p className="text-sm">Mulai kamera untuk melihat hasil deteksi real-time</p>
              </div>
            )}

            {result && (
              <div className="space-y-6">
                <DetectionStats
                  withHelmet={result.with_helmet}
                  noHelmet={result.no_helmet}
                  motorcycle={result.motorcycle}
                />

                <div>
                  <h3 className="font-bold text-slate-100 mb-3">Safety Status</h3>
                  <ComplianceStatus
                    withHelmet={result.with_helmet}
                    noHelmet={result.no_helmet}
                  />
                </div>
              </div>
            )}

            {cameraActive && !result && (
              <LoadingIndicator message="Waiting for detection..." />
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
