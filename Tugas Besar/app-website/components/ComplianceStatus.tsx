'use client';

interface ComplianceStatusProps {
  withHelmet: number;
  noHelmet: number;
}

export default function ComplianceStatus({ 
  withHelmet, 
  noHelmet 
}: ComplianceStatusProps) {
  const totalRiders = withHelmet + noHelmet;
  
  if (totalRiders === 0) {
    return (
      <div className="bg-amber-500/10 border border-amber-500/30 rounded-xl p-5 backdrop-blur">
        <div className="flex items-start gap-3">
          <span className="text-3xl">⚠️</span>
          <div>
            <p className="font-semibold text-amber-400">Belum Ada Data</p>
            <p className="text-sm text-amber-400/70 mt-1">Tidak ada pengendara yang terdeteksi</p>
          </div>
        </div>
      </div>
    );
  }

  const complianceRate = (withHelmet / totalRiders) * 100;
  
  let statusConfig = {
    title: '',
    message: '',
    icon: '',
    bgColor: 'bg-emerald-500/10',
    borderColor: 'border-emerald-500/30',
    textColor: 'text-emerald-400',
    progressColor: 'from-emerald-500 to-cyan-500',
  };

  if (complianceRate === 100) {
    statusConfig = {
      ...statusConfig,
      title: '🎉 SEMPURNA',
      message: 'Semua pengendara memakai helm dengan aman',
      icon: '✅',
    };
  } else if (complianceRate >= 80) {
    statusConfig = {
      ...statusConfig,
      title: '👍 BAIK',
      message: 'Mayoritas pengendara memakai helm',
      icon: '👍',
    };
  } else if (complianceRate >= 50) {
    statusConfig = {
      ...statusConfig,
      title: '⚠️ SEDANG',
      message: 'Banyak pengendara tidak memakai helm',
      icon: '⚠️',
      bgColor: 'bg-amber-500/10',
      borderColor: 'border-amber-500/30',
      textColor: 'text-amber-400',
      progressColor: 'from-amber-500 to-orange-500',
    };
  } else {
    statusConfig = {
      ...statusConfig,
      title: '🚨 KRITIS',
      message: 'Mayoritas pengendara tidak memakai helm - RISIKO TINGGI',
      icon: '❌',
      bgColor: 'bg-red-500/10',
      borderColor: 'border-red-500/30',
      textColor: 'text-red-400',
      progressColor: 'from-red-500 to-rose-500',
    };
  }

  return (
    <div className="space-y-5">
      <div className={`${statusConfig.bgColor} border ${statusConfig.borderColor} rounded-xl p-5 backdrop-blur`}>
        <div className="flex items-start justify-between gap-4">
          <div>
            <p className={`text-lg font-bold ${statusConfig.textColor}`}>
              {statusConfig.title}
            </p>
            <p className={`text-sm ${statusConfig.textColor}/70 mt-2`}>
              {statusConfig.message}
            </p>
          </div>
          <span className="text-3xl">{statusConfig.icon}</span>
        </div>
      </div>

      <div className="bg-slate-800/40 border border-slate-700/50 rounded-xl p-5 backdrop-blur">
        <div className="flex items-center justify-between mb-4">
          <p className="text-sm font-semibold text-slate-300">Compliance Rate</p>
          <span className={`text-3xl font-bold ${statusConfig.textColor}`}>
            {complianceRate.toFixed(1)}%
          </span>
        </div>
        <div className="w-full bg-slate-700/30 rounded-full h-3 overflow-hidden border border-slate-700/50">
          <div
            className={`h-3 rounded-full transition-all duration-500 bg-gradient-to-r ${statusConfig.progressColor}`}
            style={{ width: `${complianceRate}%` }}
          ></div>
        </div>
        <div className="mt-4 grid grid-cols-3 gap-4 text-center">
          <div>
            <p className="text-2xl font-bold text-emerald-400">{withHelmet}</p>
            <p className="text-xs text-slate-400 mt-1">Pakai Helm</p>
          </div>
          <div className="border-l border-r border-slate-700">
            <p className="text-2xl font-bold text-red-400">{noHelmet}</p>
            <p className="text-xs text-slate-400 mt-1">Tanpa Helm</p>
          </div>
          <div>
            <p className="text-2xl font-bold text-blue-400">{totalRiders}</p>
            <p className="text-xs text-slate-400 mt-1">Total</p>
          </div>
        </div>
      </div>
    </div>
  );
}
