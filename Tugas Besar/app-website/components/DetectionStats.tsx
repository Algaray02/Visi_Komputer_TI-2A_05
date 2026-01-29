'use client';

interface DetectionStatsProps {
  withHelmet: number;
  noHelmet: number;
  motorcycle: number;
}

export default function DetectionStats({ 
  withHelmet, 
  noHelmet, 
  motorcycle 
}: DetectionStatsProps) {
  const total = withHelmet + noHelmet + motorcycle;
  const complianceRate = total > 0 ? Math.round((withHelmet / total) * 100) : 0;

  const stats = [
    {
      label: 'Pakai Helm',
      icon: '✅',
      count: withHelmet,
      bgColor: 'bg-emerald-500/10',
      borderColor: 'border-emerald-500/30',
      textColor: 'text-emerald-400',
      status: 'Aman',
    },
    {
      label: 'Tanpa Helm',
      icon: '❌',
      count: noHelmet,
      bgColor: 'bg-red-500/10',
      borderColor: 'border-red-500/30',
      textColor: 'text-red-400',
      status: 'Berbahaya',
    },
    {
      label: 'Total Motor',
      icon: '🏍️',
      count: motorcycle,
      bgColor: 'bg-blue-500/10',
      borderColor: 'border-blue-500/30',
      textColor: 'text-blue-400',
      status: 'Terdeteksi',
    },
  ];

  return (
    <div className="space-y-5">
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {stats.map((stat) => (
          <div 
            key={stat.label}
            className={`${stat.bgColor} border ${stat.borderColor} rounded-xl p-5 backdrop-blur transition-transform hover:scale-105`}
          >
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm font-medium text-slate-400">{stat.label}</p>
                <p className={`text-3xl font-bold ${stat.textColor} mt-2`}>
                  {stat.count}
                </p>
              </div>
              <span className="text-2xl">{stat.icon}</span>
            </div>
            <div className="mt-3 pt-3 border-t border-slate-700/30">
              <span className={`text-xs font-semibold ${stat.textColor}`}>
                {stat.status}
              </span>
            </div>
          </div>
        ))}
      </div>

      {total > 0 && (
        <div className="bg-gradient-to-r from-blue-500/10 to-cyan-500/10 border border-blue-500/30 rounded-xl p-5 backdrop-blur">
          <div className="flex items-center justify-between mb-4">
            <p className="text-sm font-medium text-slate-400">Compliance Rate</p>
            <span className="text-2xl font-bold text-blue-400">{complianceRate}%</span>
          </div>
          <div className="w-full bg-slate-700/30 rounded-full h-3 overflow-hidden border border-slate-700/50">
            <div 
              className="bg-gradient-to-r from-emerald-500 to-cyan-500 h-3 rounded-full transition-all duration-300"
              style={{ width: `${complianceRate}%` }}
            ></div>
          </div>
          <p className="text-xs text-slate-400 mt-3">
            {withHelmet} dari {total} pengendara memakai helm dengan benar
          </p>
        </div>
      )}
    </div>
  );
}
