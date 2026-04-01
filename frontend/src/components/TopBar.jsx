import React, { useState, useEffect } from 'react';
import { useNemesis } from '../hooks/useNemesisState.jsx';
import GlitchText from '../effects/GlitchText';

const VIEW_LABELS = {
  strat_map: 'STRAT_MAP // SECTOR_7G',
  unit_stat: 'UNIT_STAT_ENVIRONMENT',
  threat_intel: 'STATUS: OPTIMAL',
  diagnostics: 'ACTIVE_NODE: DIAGNOSTICS',
};

const STATE_COLORS = {
  MONITORING: '#00e5ff',
  ALERT: '#ffab00',
  DEFENSE: '#ff5252',
  LOCKDOWN: '#ff1744',
};

export default function TopBar({ activeView }) {
  const { state, actions } = useNemesis();
  const [clock, setClock] = useState('');

  useEffect(() => {
    const iv = setInterval(() => {
      const d = new Date();
      setClock(d.toLocaleTimeString('en-US', { hour12: false }));
    }, 1000);
    return () => clearInterval(iv);
  }, []);

  const stateColor = STATE_COLORS[state.systemState] || '#00e5ff';
  const deviceCount = Object.keys(state.devices).length;

  return (
    <header className="topbar" id="main-topbar">
      <div className="topbar-left">
        <span className="topbar-system" style={{ color: stateColor }}>
          <GlitchText mode="interval" intervalMs={8000} durationMs={150}>SYS_COM_v4.2</GlitchText>
        </span>
        <span className="topbar-divider">│</span>
        <span className="topbar-view">{VIEW_LABELS[activeView] || activeView}</span>
      </div>

      <div className="topbar-center">
        <div className="topbar-state-indicator" style={{ borderColor: stateColor }}>
          <span className="live-dot" style={{ background: stateColor, boxShadow: `0 0 6px ${stateColor}` }} />
          <span style={{ color: stateColor }}>{state.systemState}</span>
        </div>
      </div>

      <div className="topbar-right">
        <div className="topbar-clock">{clock}</div>
        <div className="topbar-stats font-mono">
          <span className="text-cyan">{deviceCount}</span>
          <span className="text-dim"> DEV</span>
        </div>
        <div className="topbar-connection">
          <span className={`live-dot ${state.connected ? '' : 'red'}`} />
          <span className="text-dim">{state.connected ? 'LINKED' : 'OFFLINE'}</span>
        </div>
        <button className="topbar-icon-btn" title="Alerts">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M8 1a5 5 0 015 5v3l1 2H2l1-2V6a5 5 0 015-5z" stroke="#8899aa" strokeWidth="1.2"/>
            <path d="M6 13a2 2 0 004 0" stroke="#8899aa" strokeWidth="1.2"/>
          </svg>
          {state.alerts.length > 0 && <span className="topbar-icon-badge">{Math.min(state.alerts.length, 99)}</span>}
        </button>
      </div>
    </header>
  );
}
