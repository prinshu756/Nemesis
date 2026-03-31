import React from 'react';
import { useNemesis } from '../hooks/useNemesisState.jsx';

const NAV_ITEMS = [
  { id: 'strat_map', icon: '◻', label: 'STRAT_MAP' },
  { id: 'unit_stat', icon: '⚎', label: 'UNIT_STAT' },
  { id: 'threat_intel', icon: '◎', label: 'THREAT_INTEL' },
  { id: 'diagnostics', icon: '⚙', label: 'DIAG' },
];

export default function Sidebar({ activeView, onNavigate }) {
  const { state } = useNemesis();
  const threatCount = state.threats.filter(t => t.severity === 'critical').length;

  return (
    <nav className="sidebar" id="main-sidebar">
      {/* Logo */}
      <div className="sidebar-logo">
        <div className="sidebar-logo-icon">
          <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
            <path d="M14 2L26 8v12l-12 6L2 20V8l12-6z" stroke="#00e5ff" strokeWidth="1.2" fill="none" opacity="0.6"/>
            <path d="M14 6l8 4v8l-8 4-8-4V10l8-4z" stroke="#00e5ff" strokeWidth="1" fill="rgba(0,229,255,0.05)"/>
            <circle cx="14" cy="14" r="3" fill="#00e5ff" opacity="0.8"/>
          </svg>
        </div>
        <span className="sidebar-version">V01</span>
      </div>

      {/* Navigation Items */}
      <div className="sidebar-nav">
        {NAV_ITEMS.map((item) => (
          <button
            key={item.id}
            id={`nav-${item.id}`}
            className={`sidebar-item ${activeView === item.id ? 'active' : ''}`}
            onClick={() => onNavigate(item.id)}
            title={item.label}
          >
            <div className="sidebar-item-icon">{item.icon}</div>
            <span className="sidebar-item-label">{item.label}</span>
            {item.id === 'threat_intel' && threatCount > 0 && (
              <span className="sidebar-badge">{threatCount}</span>
            )}
          </button>
        ))}
      </div>

      {/* Bottom Actions */}
      <div className="sidebar-bottom">
        <button className="sidebar-item" id="nav-settings" title="Settings">
          <div className="sidebar-item-icon">⚙</div>
          <span className="sidebar-item-label">SET</span>
        </button>
        <button className="sidebar-item sidebar-power" id="nav-power" title="System">
          <div className="sidebar-item-icon">⏻</div>
        </button>
      </div>
    </nav>
  );
}
