import React, { useMemo, useState, useEffect } from 'react';
import { useNemesis } from '../hooks/useNemesisState.jsx';
import GlowChart from '../components/GlowChart';
import LogTerminal from '../components/LogTerminal';
import GlitchText from '../effects/GlitchText';

export default function ThreatIntel() {
  const { state } = useNemesis();
  const [trafficData, setTrafficData] = useState([]);
  const [heatmap, setHeatmap] = useState([]);

  const threats = state.threats;
  const topThreat = threats.length > 0 ? threats[0] : null;
  const sortedThreats = useMemo(() => threats.slice(0, 3), [threats]);

  // Simulate real-time traffic data for bar chart
  useEffect(() => {
    const iv = setInterval(() => {
      setTrafficData(prev => {
        const next = [...prev, Math.random() * 80 + 20];
        return next.slice(-16);
      });
      setHeatmap(prev => {
        const grid = [];
        for (let i = 0; i < 24; i++) {
          grid.push(Math.random() > 0.8 ? Math.random() * 100 : Math.random() * 30);
        }
        return grid;
      });
    }, 2000);
    return () => clearInterval(iv);
  }, []);

  const bandwidth = state.metrics?.network_throughput_gbps || 1.22;
  const latency = state.metrics?.ooda_latency_ms || 4.2;

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
    </div>
  );
}
