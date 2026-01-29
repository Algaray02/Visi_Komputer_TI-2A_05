'use client';

interface LoadingIndicatorProps {
  message?: string;
  fullScreen?: boolean;
}

export default function LoadingIndicator({ 
  message = 'Processing...', 
  fullScreen = false 
}: LoadingIndicatorProps) {
  const content = (
    <div className="flex flex-col items-center justify-center gap-6">
      <div className="relative w-20 h-20">
        <div className="absolute inset-0 rounded-full border-4 border-slate-700/30"></div>
        <div className="absolute inset-0 rounded-full border-4 border-transparent border-t-blue-500 border-r-cyan-500 animate-spin"></div>
        <div className="absolute inset-4 rounded-full border-2 border-transparent border-b-blue-500/50 animate-spin" style={{ animationDirection: 'reverse', animationDuration: '1.5s' }}></div>
      </div>
      <div className="text-center">
        <p className="text-slate-200 font-semibold text-lg">{message}</p>
        <p className="text-sm text-slate-400 mt-2">Mohon tunggu sebentar...</p>
      </div>
    </div>
  );

  if (fullScreen) {
    return (
      <div className="fixed inset-0 bg-slate-900/80 backdrop-blur-sm flex items-center justify-center z-50">
        {content}
      </div>
    );
  }

  return (
    <div className="flex items-center justify-center py-16">
      {content}
    </div>
  );
}
