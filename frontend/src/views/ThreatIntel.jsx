import React, { useMemo, useState, useEffect } from 'react';
import { useNemesis } from '../hooks/useNemesisState.jsx';
import GlowChart from '../components/GlowChart';
import LogTerminal from '../components/LogTerminal';
import GlitchText from '../effects/GlitchText';

export default function ThreatIntel() {
  const { state } = useNemesis();

  // Use real alerts/threats from state
  const threats = state.threats.length > 0 ? state.threats : state.anomalies;
  const topThreat = threats.length > 0 ? threats[0] : null;
  const sortedThreats = useMemo(() => threats.slice(0, 3), [threats]);

  // Generate traffic data visualization from real traffic logs
  const trafficData = useMemo(() => {
    if (state.trafficLogs.length === 0) return [];
    
    // Calculate packet sizes per log entry for visualization
    return state.trafficLogs.slice(-16).map(log => {
      const size = log.packet_size || 0;
      // Normalize to 0-100 range for display
      return Math.min(100, (size / 65535) * 100);
    });
  }, [state.trafficLogs]);

  // Generate heatmap from anomaly data
  const heatmap = useMemo(() => {
    if (state.anomalies.length === 0) {
      // Return empty grid if no data
      return Array(24).fill(0);
    }
    
    // Create heatmap based on anomaly severity distribution
    const grid = Array(24).fill(0);
    state.anomalies.slice(0, 24).forEach((anom, idx) => {
      const severityMap = { critical: 100, high: 80, medium: 50, low: 20 };
      grid[idx] = severityMap[anom.severity?.toLowerCase()] || 30;
    });
    return grid;
  }, [state.anomalies]);

  // Get metrics from backend status or fallback to defaults
  const bandwidth = state.backendStatus?.system?.network_throughput_gbps || 
                   state.metrics?.network_throughput_gbps || 
                   (state.trafficLogs.length > 0 ? (state.trafficLogs.length * 0.001) : 0);
  const latency = state.backendStatus?.system?.latency_ms || 
                 state.metrics?.ooda_latency_ms || 4.2;

  return (
    <div className="view-threat-intel" id="view-threat-intel">
      {/* Header */}
      <div className="threat-header">
        <div>
          <div className="font-mono text-dim" style={{ fontSize: 10 }}>SEC_PROTOCOL_DELTA // INTEL_LEVEL_05</div>
          <h1 className="font-heading" style={{ fontSize: 28, fontWeight: 700, letterSpacing: '2px' }}>
            <GlitchText mode="interval" intervalMs={5000} durationMs={250}>THREAT_INTELLIGENCE_BOARD</GlitchText>
          </h1>
        </div>
        <div className="font-mono text-dim" style={{ fontSize: 10, textAlign: 'right' }}>
          <div>LAT: 35.6895° N / LON: 139.6917° E</div>
          <div>REF_SESSION: 992-X-GAMMA</div>
        </div>
      </div>

      {/* Critical Alert Banner */}
      {topThreat && (
        <div className="threat-critical-banner card" id="threat-critical-alert">
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <div className="threat-alert-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                <path d="M12 2L22 20H2L12 2z" stroke="#ffab00" strokeWidth="2" fill="rgba(255,171,0,0.15)" />
                <line x1="12" y1="9" x2="12" y2="14" stroke="#ffab00" strokeWidth="2" />
                <circle cx="12" cy="17" r="1" fill="#ffab00" />
              </svg>
            </div>
            <div style={{ flex: 1 }}>
              <div className="font-heading text-red" style={{ fontSize: 13, fontWeight: 700 }}><GlitchText mode="continuous" intensity={1.5} glitchColor1="#ff5252" glitchColor2="#ffab00">CRITICAL ALERT</GlitchText></div>
              <div className="font-mono" style={{ fontSize: 11, color: 'var(--text-primary)' }}>
                {topThreat.description || topThreat.message || topThreat.name || 'ANOMALOUS SIGNAL DETECTED'}
              </div>
            </div>
            <div style={{ textAlign: 'right' }}>
              <div className="font-mono text-dim" style={{ fontSize: 9 }}>THREAT_LEVEL</div>
              <div className="font-heading text-red" style={{ fontSize: 20, fontWeight: 700 }}>
                {topThreat.severity?.toUpperCase() === 'CRITICAL' ? 'X-TYPE' :
                 topThreat.severity?.toUpperCase() || 'HIGH'}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Charts Row */}
      <div className="threat-charts-row">
        {/* Signal Traffic Analysis */}
        <div className="card" style={{ flex: 2 }}>
          <div className="card-header">
            <span className="card-title">
              <span className="font-mono text-dim" style={{ marginRight: 8, fontSize: 9 }}>REF_0063-K</span>
              SIGNAL_TRAFFIC_ANALYSIS
            </span>
          </div>
          <div className="card-body">
            <GlowChart data={trafficData} height={200} color="cyan" />
            <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 12 }}>
              <div>
                <div className="font-mono text-dim" style={{ fontSize: 9 }}>BANDWIDTH</div>
                <div className="font-heading text-cyan" style={{ fontSize: 16, fontWeight: 700 }}>
                  {bandwidth.toFixed(2)} <span style={{ fontSize: 10 }}>GBPS</span>
                </div>
              </div>
              <div>
                <div className="font-mono text-dim" style={{ fontSize: 9 }}>LATENCY</div>
                <div className="font-heading text-cyan" style={{ fontSize: 16, fontWeight: 700 }}>
                  {latency.toFixed(1)} <span style={{ fontSize: 10 }}>MS</span>
                </div>
              </div>
              <div className="font-mono text-dim" style={{ fontSize: 9, alignSelf: 'flex-end' }}>
                ENCRYPTION: AES-4096-QUANTUM
              </div>
            </div>
          </div>
        </div>

        {/* Heatmap */}
        <div className="card" style={{ flex: 1 }}>
          <div className="card-header">
            <span className="card-title">
              <span className="font-mono text-dim" style={{ marginRight: 8, fontSize: 9 }}>REF_0045-H</span>
              HEATMAP_ACTIVITY
            </span>
          </div>
          <div className="card-body">
            <div className="threat-heatmap">
              {heatmap.map((val, i) => (
                <div key={i} className="threat-heatmap-cell" style={{
                  background: val > 70 ? 'var(--red-400)' :
                              val > 40 ? 'rgba(0, 229, 255, 0.5)' :
                              'rgba(0, 229, 255, 0.1)',
                  boxShadow: val > 70 ? 'var(--glow-red)' :
                             val > 40 ? '0 0 4px rgba(0,229,255,0.3)' : 'none',
                }} />
              ))}
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 12 }}>
              <div className="font-mono text-dim" style={{ fontSize: 9 }}>SEC_ZONE: SECTOR_7G</div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                <span className={`live-dot ${threats.length > 0 ? 'red' : ''}`} />
                <span className={`font-mono ${threats.length > 0 ? 'text-red' : 'text-dim'}`} style={{ fontSize: 9 }}>
                  {threats.length > 0 ? 'HIGH ALERT' : 'NOMINAL'}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Active Enemy Assets */}
      <div style={{ marginTop: 16 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
          <h2 className="font-heading" style={{ fontSize: 18, fontWeight: 700, letterSpacing: '2px' }}>
            ACTIVE_ENEMY_ASSETS
          </h2>
          <button className="btn btn-ghost" id="btn-refresh-intel">REFRESH_INTEL</button>
        </div>
        <div className="threat-assets-grid">
          {sortedThreats.map((threat, i) => {
            const classLabel = threat.severity === 'critical' ? 'CLASS-V' : threat.severity === 'high' ? 'CLASS-II' : 'CLASS-IX';
            const proximity = threat.source_ip ? `${(Math.random() * 50).toFixed(1)} KM` : 'UNKNOWN';
            return (
              <div key={threat.id || i} className="card threat-asset-card">
                <div className="card-body">
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                    <span className="font-mono text-dim" style={{ fontSize: 9 }}>ASSET_ID: {threat.attack_id || threat.id}</span>
                    <span className={`badge ${threat.severity === 'critical' ? 'badge-critical' : 'badge-warning'}`}>
                      {classLabel}
                    </span>
                  </div>
                  <div className="font-heading text-red" style={{ fontSize: 15, fontWeight: 700, marginBottom: 4 }}>
                    {threat.name || threat.type || 'UNKNOWN'}
                  </div>
                  <div className="font-mono text-dim" style={{ fontSize: 10 }}>
                    {threat.description || `Source: ${threat.source_ip || 'unknown'}`}
                  </div>
                  <div style={{ marginTop: 12 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span className="font-mono text-dim" style={{ fontSize: 9 }}>PROXIMITY</span>
                      <span className="font-mono text-cyan" style={{ fontSize: 9 }}>{proximity}</span>
                    </div>
                    <div className="progress-bar" style={{ marginTop: 4 }}>
                      <div className={`progress-fill ${threat.severity === 'critical' ? 'red' : 'cyan'}`}
                        style={{ width: `${Math.random() * 60 + 20}%` }} />
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
          {sortedThreats.length === 0 && (
            <div className="card" style={{ gridColumn: '1 / -1', padding: 24, textAlign: 'center' }}>
              <span className="font-mono text-dim">No active enemy assets detected</span>
            </div>
          )}
        </div>
      </div>

      {/* Live Tactical Stream */}
      <div style={{ marginTop: 16 }}>
        <LogTerminal logs={state.logs} maxLines={40} title="◎ LIVE_TACTICAL_STREAM" />
      </div>

      {/* Database Status */}
      <div style={{ marginTop: 16 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
          <h2 className="font-heading" style={{ fontSize: 18, fontWeight: 700, letterSpacing: '2px' }}>
            💾 DATABASE_STATUS
          </h2>
        </div>
        {state.backendStatus?.database ? (
          <div className="threat-assets-grid" style={{ gridTemplateColumns: '1fr 1fr' }}>
            <div className="card">
              <div className="card-body">
                <div className="font-heading text-cyan" style={{ fontSize: 13, fontWeight: 700, marginBottom: 12 }}>
                  📁 SQLite LOCAL
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8, fontSize: 12 }}>
                  <div className="font-mono text-dim">Devices:<span className="text-cyan"> {state.backendStatus.database.local?.devices || 0}</span></div>
                  <div className="font-mono text-dim">Alerts:<span className="text-cyan"> {state.backendStatus.database.local?.alerts || 0}</span></div>
                  <div className="font-mono text-dim">Traffic:<span className="text-cyan"> {state.backendStatus.database.local?.traffic_logs || 0}</span></div>
                  <div className="font-mono text-dim">Honeypots:<span className="text-cyan"> {state.backendStatus.database.local?.honeypot_interactions || 0}</span></div>
                </div>
                <div className="font-mono text-green" style={{ marginTop: 8, fontSize: 11, fontWeight: 700 }}>
                  Total: {state.backendStatus.database.local?.total_records || 0} records
                </div>
              </div>
            </div>

            <div className="card">
              <div className="card-body">
                <div className="font-heading text-cyan" style={{ fontSize: 13, fontWeight: 700, marginBottom: 12 }}>
                  ☁️ NEON POSTGRESQL
                </div>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <span className="font-mono text-dim">Connection:</span>
                  <span className={`font-heading ${state.backendStatus.database.neon?.status === 'connected' ? 'text-green' : 'text-red'}`}>
                    {state.backendStatus.database.neon?.status?.toUpperCase() || 'UNKNOWN'} 🟢
                  </span>
                </div>
                <div className="font-mono text-dim" style={{ marginTop: 8, fontSize: 10 }}>
                  Production Cloud Database - Ready
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="card text-dim" style={{ padding: 16, textAlign: 'center' }}>No database info available</div>
        )}
      </div>

      {/* Recent Events - Latest Discoveries */}
      <div style={{ marginTop: 16 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
          <h2 className="font-heading" style={{ fontSize: 18, fontWeight: 700, letterSpacing: '2px' }}>
            📋 RECENT_EVENTS_LOG
          </h2>
        </div>
        {state.backendStatus?.recent_events || state.trafficLogs.length > 0 ? (
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
            {/* Latest Devices */}
            <div className="card">
              <div className="card-body">
                <div className="font-heading text-cyan" style={{ fontSize: 13, fontWeight: 700, marginBottom: 12 }}>
                  📱 Latest Devices Discovered
                </div>
                <div style={{ maxHeight: 200, overflowY: 'auto' }}>
                  {state.backendStatus?.recent_events?.latest_devices?.slice(0, 5).map((dev, idx) => (
                    <div key={idx} className="font-mono" style={{ padding: 4, borderBottom: '1px solid rgba(0,229,255,0.1)', fontSize: 10 }}>
                      <div className="text-cyan">{dev.ip || 'N/A'}</div>
                      <div className="text-dim">{dev.hostname || dev.device_type || 'Unknown'}</div>
                    </div>
                  )) || <div className="text-dim">No recent devices</div>}
                </div>
              </div>
            </div>

            {/* Latest Alerts */}
            <div className="card">
              <div className="card-body">
                <div className="font-heading text-red" style={{ fontSize: 13, fontWeight: 700, marginBottom: 12 }}>
                  🚨 Latest Alerts Triggered
                </div>
                <div style={{ maxHeight: 200, overflowY: 'auto' }}>
                  {state.backendStatus?.recent_events?.latest_alerts?.slice(0, 5).map((alert, idx) => (
                    <div key={idx} className="font-mono" style={{ padding: 4, borderBottom: '1px solid rgba(255,0,0,0.1)', fontSize: 10 }}>
                      <div className={`${alert.severity === 'critical' ? 'text-red' : alert.severity === 'high' ? 'text-orange' : 'text-yellow'}`}>
                        {alert.message || alert.name || 'Alert'}
                      </div>
                      <div className="text-dim text-cyan">{alert.source_ip || alert.device_mac || 'Unknown'}</div>
                    </div>
                  )) || <div className="text-dim">No recent alerts</div>}
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="card text-dim" style={{ padding: 16, textAlign: 'center' }}>No recent events</div>
        )}
      </div>
    </div>
  );
}
