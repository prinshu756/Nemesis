import React from 'react';

export default function DeviceCard({ device, onIsolate, onRelease, onHoneypot }) {
  if (!device) return null;

  const statusClass =
    device.status === 'isolated' ? 'badge-isolated' :
    device.status === 'suspicious' ? 'badge-warning' :
    device.risk_level === 'critical' ? 'badge-critical' :
    device.risk_level === 'high' ? 'badge-warning' :
    'badge-operational';

  const statusLabel =
    device.status === 'isolated' ? 'ISOLATED' :
    device.status === 'suspicious' ? 'SUSPICIOUS' :
    device.risk_level === 'critical' ? 'CRITICAL' :
    device.risk_level === 'high' ? 'WARNING' :
    'OPERATIONAL';

  const healthColor =
    device.health >= 80 ? 'green' :
    device.health >= 50 ? 'amber' :
    'red';

  const riskColor =
    device.risk_level === 'critical' ? 'red' :
    device.risk_level === 'high' ? 'red' :
    device.risk_level === 'medium' ? 'amber' :
    'green';

  return (
    <div className={`device-card card ${device.status === 'isolated' ? 'device-card--isolated' : ''}`}>
      <div className="device-card-main">
        <div className="device-card-icon">
          <DeviceIcon type={device.device_type} status={device.status} />
        </div>
        <div className="device-card-info">
          <div className="device-card-ref font-mono text-dim">{device.id}</div>
          <div className="device-card-name font-heading">{device.hostname}</div>
          <div className="device-card-meta font-mono">
            <span className={`text-${healthColor}`}>■ HEALTH: {device.health}%</span>
            <span className="text-dim" style={{ marginLeft: 12 }}>■ PWR: {device.power_level}%</span>
          </div>
        </div>
        <div className="device-card-chart">
          <MiniSparkline risk={device.risk_score} />
        </div>
        <div className="device-card-status">
          <span className="card-title">STATUS</span>
          <span className={`badge ${statusClass}`}>{statusLabel}</span>
        </div>
      </div>
      <div className="device-card-actions">
        {device.isolation_status === 'normal' ? (
          <>
            <button className="btn btn-danger" style={{ fontSize: 9, padding: '4px 10px' }}
              onClick={() => onIsolate && onIsolate(device.mac)}>
              ISOLATE
            </button>
            <button className="btn btn-ghost" style={{ fontSize: 9, padding: '4px 10px' }}
              onClick={() => onHoneypot && onHoneypot(device.ip)}>
              HONEYPOT
            </button>
          </>
        ) : (
          <button className="btn btn-primary" style={{ fontSize: 9, padding: '4px 10px' }}
            onClick={() => onRelease && onRelease(device.mac)}>
            RELEASE
          </button>
        )}
      </div>
    </div>
  );
}

function DeviceIcon({ type, status }) {
  const color = status === 'isolated' ? '#ff1744' : status === 'suspicious' ? '#ffab00' : '#00e5ff';
  return (
    <svg width="36" height="36" viewBox="0 0 36 36" fill="none">
      <rect x="4" y="4" width="28" height="28" rx="4" stroke={color} strokeWidth="1" fill="rgba(0,229,255,0.05)" />
      <circle cx="18" cy="16" r="6" stroke={color} strokeWidth="1" fill="none" />
      <line x1="12" y1="26" x2="24" y2="26" stroke={color} strokeWidth="1" />
    </svg>
  );
}

function MiniSparkline({ risk = 0 }) {
  const points = [];
  for (let i = 0; i < 12; i++) {
    const val = Math.max(0, Math.min(100, risk + (Math.random() - 0.5) * 30));
    points.push(val);
  }
  const h = 30;
  const w = 80;
  const max = 100;
  const pathData = points.map((v, i) => {
    const x = (i / (points.length - 1)) * w;
    const y = h - (v / max) * h;
    return `${i === 0 ? 'M' : 'L'}${x},${y}`;
  }).join(' ');

  const color = risk >= 70 ? '#ff1744' : risk >= 45 ? '#ffab00' : '#00e5ff';

  return (
    <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`}>
      <path d={pathData} stroke={color} strokeWidth="1.5" fill="none" opacity="0.8" />
    </svg>
  );
}
