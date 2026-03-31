import React, { useMemo, useState, useEffect } from 'react';
import { useNemesis } from '../hooks/useNemesisState.jsx';
import GlowChart from '../components/GlowChart';
import LogTerminal from '../components/LogTerminal';
import GlitchText from '../effects/GlitchText';

export default function Diagnostics() {
  const { state } = useNemesis();
  const [cpuHistory, setCpuHistory] = useState([]);

  const m = state.metrics || {};
  const cpuUsage = m.cpu_usage || 42.8;
  const cpuCores = m.cpu_cores || [45, 62, 38, 71, 55, 29, 48, 60];
  const temp = m.temperature || 54;
  const memUsed = m.memory_used || 52;
  const memTotal = m.memory_total_gb || 16.4;
  const throughput = m.network_throughput_gbps || 1.2;
  const powerLevel = m.power_level || 98;
  const powerStatus = m.power_status || 'STABLE';
  const thermalStatus = m.thermal_status || 'NOMINAL';
  const storageUsed = m.storage_used_tb || 842;
  const storageTotal = m.storage_total_tb || 1200;

  // Build CPU history for chart
  useEffect(() => {
    if (cpuCores && cpuCores.length > 0) {
      setCpuHistory(prev => {
        const next = [...prev, ...cpuCores];
        return next.slice(-16);
      });
    }
  }, [cpuCores.join(',')]);

  const uptimeStr = useMemo(() => {
    const s = m.uptime_seconds || 0;
    const h = String(Math.floor(s / 3600)).padStart(2, '0');
    const min = String(Math.floor((s % 3600) / 60)).padStart(2, '0');
    const sec = String(s % 60).padStart(2, '0');
    return `${h}:${min}:${sec}`;
  }, [m.uptime_seconds]);

  return (
    <div className="view-diagnostics" id="view-diagnostics">
      {/* Header */}
      <div className="diag-header">
        <div>
          <div className="font-mono text-dim" style={{ fontSize: 10 }}>SYSTEM_INTEGRITY_INDEX</div>
          <h1 className="font-heading" style={{ fontSize: 28, fontWeight: 700, letterSpacing: '2px' }}>
            <GlitchText mode="interval" intervalMs={6000} durationMs={200}>DIAGNOSTICS_OVERRIDE</GlitchText>
          </h1>
        </div>
        <div className="font-mono text-dim" style={{ fontSize: 10, textAlign: 'right' }}>
          <div>ENCRYPTION: AES_256_ACTIVE</div>
          <div className={thermalStatus === 'WARNING' ? 'text-red' : 'text-green'}>
            THREAT_LEVEL: {state.systemState === 'MONITORING' ? 'NULL' : state.systemState}
          </div>
        </div>
      </div>

      {/* Top Row: CPU + Side Cards */}
      <div className="diag-top-row">
        {/* CPU Chart */}
        <div className="card diag-cpu-card" style={{ flex: 2 }}>
          <div className="card-header">
            <span className="card-title">
              ◻ CPU_CORE_ORCHESTRATION
              <span className="font-mono text-dim" style={{ display: 'block', fontSize: 9, marginTop: 2 }}>
                REAL-TIME_LOAD_DISTRIBUTION
              </span>
            </span>
            <div className="font-mono" style={{ display: 'flex', gap: 16 }}>
              <div>
                <span className="text-cyan" style={{ fontSize: 18, fontWeight: 700, fontFamily: 'var(--font-heading)' }}>
                  {cpuUsage.toFixed(1)}%
                </span>
                <span className="text-dim" style={{ fontSize: 9, display: 'block' }}>AVG_LOAD</span>
              </div>
              <div>
                <span className={`${temp > 65 ? 'text-red' : 'text-cyan'}`}
                  style={{ fontSize: 18, fontWeight: 700, fontFamily: 'var(--font-heading)' }}>
                  {temp.toFixed(0)}°C
                </span>
                <span className="text-dim" style={{ fontSize: 9, display: 'block' }}>CORE_TEMP</span>
              </div>
            </div>
          </div>
          <div className="card-body">
            <GlowChart data={cpuHistory} height={180} maxBars={16} color="cyan" />
          </div>
        </div>

        {/* Side Cards */}
        <div className="diag-side-cards">
          <div className="card" style={{ marginBottom: 8 }}>
            <div className="card-body" style={{ padding: '12px 16px' }}>
              <div className="font-mono text-dim" style={{ fontSize: 9 }}>POWER_CELL</div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 4 }}>
                <span className="font-heading text-green" style={{ fontSize: 16, fontWeight: 700 }}>
                  {powerStatus}
                </span>
                <span className="badge badge-online" style={{ fontSize: 10 }}>{powerLevel}%</span>
              </div>
            </div>
          </div>

          <div className={`card ${thermalStatus === 'WARNING' ? 'diag-card-warning' : ''}`} style={{ marginBottom: 8 }}>
            <div className="card-body" style={{ padding: '12px 16px' }}>
              <div className="font-mono text-dim" style={{ fontSize: 9 }}>THERMAL_VENT</div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 4 }}>
                <span className={`font-heading ${thermalStatus === 'WARNING' ? 'text-amber' : 'text-green'}`}
                  style={{ fontSize: 16, fontWeight: 700 }}>
                  {thermalStatus}
                </span>
                <span className={`badge ${thermalStatus === 'WARNING' ? 'badge-warning' : 'badge-online'}`}>
                  {temp > 65 ? 'HIGH' : 'NORM'}
                </span>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="card-body" style={{ padding: '12px 16px' }}>
              <div className="font-mono text-dim" style={{ fontSize: 9 }}>NETWORK_THROUGHPUT</div>
              <div className="font-heading text-cyan" style={{ fontSize: 24, fontWeight: 700, marginTop: 4 }}>
                {throughput.toFixed(1)} <span style={{ fontSize: 11 }}>GBPS</span>
              </div>
              <div className="progress-bar" style={{ marginTop: 6 }}>
                <div className="progress-fill cyan" style={{ width: `${Math.min(100, throughput * 10)}%` }} />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Log Output */}
      <div style={{ marginTop: 12 }}>
        <LogTerminal logs={state.logs} maxLines={50} title="KERNEL_LOG_OUTPUT" />
      </div>

      {/* Bottom Cards */}
      <div className="diag-bottom-row">
        <div className="card">
          <div className="card-body" style={{ padding: '16px' }}>
            <div className="font-mono text-dim" style={{ fontSize: 9 }}>MEMORY_ALLOC_A</div>
            <div className="font-heading text-cyan glow-cyan" style={{ fontSize: 28, fontWeight: 700, marginTop: 4 }}>
              {memTotal.toFixed(1)} <span style={{ fontSize: 11 }}>GB</span>
            </div>
            <div className="font-mono text-dim" style={{ fontSize: 9 }}>USED: {memUsed.toFixed(0)}%</div>
            <div className="progress-bar" style={{ marginTop: 4 }}>
              <div className={`progress-fill ${memUsed > 80 ? 'red' : 'cyan'}`} style={{ width: `${memUsed}%` }} />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-body" style={{ padding: '16px' }}>
            <div className="font-mono text-dim" style={{ fontSize: 9 }}>STORAGE_ARRAY_B</div>
            <div className="font-heading text-cyan glow-cyan" style={{ fontSize: 28, fontWeight: 700, marginTop: 4 }}>
              {storageUsed} <span style={{ fontSize: 11 }}>TB</span>
            </div>
            <div className="font-mono text-dim" style={{ fontSize: 9 }}>CAP: {(storageTotal / 1000).toFixed(1)}PB</div>
            <div className="progress-bar" style={{ marginTop: 4 }}>
              <div className="progress-fill cyan" style={{ width: `${(storageUsed / storageTotal) * 100}%` }} />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-body" style={{ padding: '16px', display: 'flex', gap: 16, alignItems: 'center' }}>
            <div>
              <svg width="36" height="36" viewBox="0 0 36 36" fill="none">
                <rect x="8" y="4" width="20" height="28" rx="3" stroke="#00e5ff" strokeWidth="1.2" fill="rgba(0,229,255,0.05)" />
                <rect x="14" y="16" width="8" height="10" stroke="#00e5ff" strokeWidth="1" fill="none" />
                <circle cx="18" cy="13" r="3" stroke="#00e5ff" strokeWidth="1" fill="rgba(0,229,255,0.1)" />
              </svg>
            </div>
            <div>
              <div className="font-mono text-dim" style={{ fontSize: 9 }}>QUANTUM_KEY_EXCHANGE</div>
              <div className="font-heading text-green glow-cyan" style={{ fontSize: 16, fontWeight: 700, marginTop: 2 }}>
                SECURE_ACTIVE
              </div>
              <div className="font-mono text-dim" style={{ fontSize: 8, marginTop: 4 }}>
                HASH: F7E1.9692.AEC1.D4E2.B8DF.6912.CC33.86N1
              </div>
              <div className="progress-bar" style={{ marginTop: 4, width: 120 }}>
                <div className="progress-fill green" style={{ width: '100%' }} />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="diag-footer font-mono text-dim" style={{ fontSize: 9, marginTop: 12 }}>
        <div style={{ display: 'flex', gap: 24 }}>
          <span>LATITUDE: 34.0522 N</span>
          <span>LONGITUDE: 118.2437 W</span>
          <span>ALTITUDE: 12.4 KM</span>
        </div>
        <div style={{ display: 'flex', gap: 16 }}>
          <span>PROTOCOL_V4.01-REVISION_B</span>
          <span className="text-red"><GlitchText mode="continuous" intensity={0.8} glitchColor1="#ff1744" glitchColor2="#d50000">UNAUTHORIZED_ACCESS_IS_LETHAL</GlitchText></span>
        </div>
      </div>
    </div>
  );
}
