import React, { useRef, useEffect, useState } from 'react';

export default function LogTerminal({ logs = [], maxLines = 60, title = 'KERNEL_LOG_OUTPUT' }) {
  const containerRef = useRef(null);
  const [autoScroll, setAutoScroll] = useState(true);

  useEffect(() => {
    if (autoScroll && containerRef.current) {
      containerRef.current.scrollTop = 0;
    }
  }, [logs, autoScroll]);

  const getLevelColor = (level) => {
    switch (level?.toUpperCase()) {
      case 'CRITICAL': return 'var(--red-400)';
      case 'WARNING': return 'var(--amber-400)';
      case 'DEBUG': return 'var(--green-400)';
      default: return 'var(--cyan-400)';
    }
  };

  const formatTime = (ts) => {
    if (!ts) return '00:00:00.0';
    const d = new Date(ts * 1000);
    return d.toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' }) +
      '.' + Math.floor(d.getMilliseconds() / 100);
  };

  const displayLogs = logs.slice(0, maxLines);

  return (
    <div className="log-terminal card">
      <div className="card-header">
        <span className="card-title">{title}</span>
        <div style={{ display: 'flex', gap: 8 }}>
          <button className="btn btn-ghost" style={{ padding: '3px 10px', fontSize: 9 }}
            onClick={() => setAutoScroll(!autoScroll)}>
            {autoScroll ? 'AUTO_SCROLL' : 'PAUSED'}
          </button>
        </div>
      </div>
      <div className="log-terminal-body" ref={containerRef}>
        {displayLogs.map((log, i) => (
          <div key={log.id || i} className={`log-entry ${i === 0 ? 'log-entry--new' : ''}`}>
            <span className="log-time">[{formatTime(log.timestamp)}]</span>
            <span className="log-level" style={{ color: getLevelColor(log.level) }}>
              {log.level || 'INFO'}
            </span>
            <span className="log-message">{log.message || ''}</span>
            {log.source && <span className="log-source">{log.source}</span>}
          </div>
        ))}
        {displayLogs.length === 0 && (
          <div className="log-entry text-dim">Awaiting data stream...</div>
        )}
      </div>
    </div>
  );
}
