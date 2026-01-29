import type { Metadata } from 'next';
import Navbar from '@/components/Navbar';
import './globals.css';

export const metadata: Metadata = {
  title: '🏍️ Helmet Detection System | AI-Powered Safety',
  description: 'Sistem deteksi helm real-time menggunakan YOLOv11 untuk keselamatan berkendara',
  keywords: ['helmet detection', 'safety', 'motorcycle', 'AI', 'YOLO'],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="id" suppressHydrationWarning>
      <body className="bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-slate-50 min-h-screen flex flex-col">
        <Navbar />
        <main className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-12">
          {children}
        </main>
        <footer className="border-t border-slate-700 py-8 mt-16">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-slate-400 text-sm">
            <p>🏍️ Helmet Detection System v1.0 | AI-Powered Road Safety</p>
          </div>
        </footer>
      </body>
    </html>
  );
}
