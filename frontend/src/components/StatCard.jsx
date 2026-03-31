import React from 'react';

export default function StatCard({ label, value, unit, sub, color = 'cyan', alert, progress }) {
  const colorMap = {
    cyan: { val: 'var(--cyan-400)', glow: 'var(--text-glow-cyan)', bar: 'cyan' },
    red: { val: 'var(--red-400)', glow: 'var(--text-glow-red)', bar: 'red' },
    amber: { val: 'var(--amber-400)', glow: '0 0 6px rgba(255,171,0,0.5)', bar: 'amber' },
    green: { val: 'var(--green-400)', glow: '0 0 6px rgba(0,230,118,0.5)', bar: 'green' },
  };
  const c = colorMap[color] || colorMap.cyan;

  return (
    <div className={`stat-card card ${alert ? 'stat-card--alert' : ''}`}>
      <div className="stat-card-label">{label}</div>
      <div className="stat-card-value" style={{ color: c.val, textShadow: c.glow }}>
        {value}
        {unit && <span className="stat-card-unit">{unit}</span>}
      </div>
      {sub && <div className="stat-card-sub">{sub}</div>}
      {progress !== undefined && (
        <div className="progress-bar" style={{ marginTop: 8 }}>
          <div className={`progress-fill ${c.bar}`} style={{ width: `${Math.min(100, progress)}%` }}/>
        </div>
      )}
      {alert && (
        <div className="stat-card-alert">
          <span className="stat-card-alert-icon">▲</span>
        </div>
      )}
    </div>
  );
}
