import React from 'react';

export default function AlertPanel({ alerts = [], maxAlerts = 10 }) {
  const displayAlerts = alerts.slice(0, maxAlerts);

  const getSeverityStyle = (severity) => {
    switch (severity) {
      case 'critical':
        return { color: 'var(--red-400)', border: 'var(--border-alert)', bg: 'rgba(255,23,68,0.06)', icon: '✦' };
      case 'high':
        return { color: 'var(--red-400)', border: 'rgba(255,82,82,0.3)', bg: 'rgba(255,82,82,0.04)', icon: '⚠' };
      case 'warning':
      case 'medium':
        return { color: 'var(--amber-400)', border: 'var(--border-warning)', bg: 'rgba(255,171,0,0.04)', icon: '⚠' };
      default:
        return { color: 'var(--cyan-400)', border: 'var(--border-primary)', bg: 'rgba(0,229,255,0.04)', icon: 'ℹ' };
    }
  };

  const formatTime = (ts) => {
    if (!ts) return '';
    const d = new Date(ts * 1000);
    return d.toLocaleTimeString('en-US', { hour12: false });
  };

  return (
    <div className="alert-panel card">
      <div className="card-header">
        <span className="card-title" style={{ color: 'var(--red-400)' }}>
          <span style={{ marginRight: 6 }}>✦</span>THREAT_ALERTS
        </span>
      </div>
      <div className="alert-panel-body">
        {displayAlerts.map((alert, i) => {
          const style = getSeverityStyle(alert.severity);
          return (
            <div
              key={alert.id || i}
              className={`alert-entry ${i === 0 ? 'alert-entry--new' : ''}`}
              style={{ borderLeft: `2px solid ${style.color}`, background: style.bg }}
            >
              <div className="alert-entry-header">
                <span className="alert-time text-red">{formatTime(alert.timestamp)} // ALERT</span>
              </div>
              <div className="alert-entry-message">
                {alert.message || alert.title || 'Unknown alert'}
              </div>
            </div>
          );
        })}
        {displayAlerts.length === 0 && (
          <div className="alert-entry text-dim" style={{ padding: '12px', textAlign: 'center', fontFamily: 'var(--font-mono)', fontSize: 11 }}>
            No active threats detected
          </div>
        )}
      </div>
    </div>
  );
}
