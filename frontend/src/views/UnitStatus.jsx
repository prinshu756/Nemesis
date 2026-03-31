import React, { useMemo } from 'react';
import { useNemesis } from '../hooks/useNemesisState.jsx';
import StatCard from '../components/StatCard';
import DeviceCard from '../components/DeviceCard';
import AlertPanel from '../components/AlertPanel';

export default function UnitStatus() {
  const { state, actions } = useNemesis();
  const devices = useMemo(() => Object.values(state.devices), [state.devices]);

  const totalDeployed = devices.length;
  const operational = devices.filter(d => d.status === 'online' && d.health >= 50).length;
  const combatReady = totalDeployed > 0 ? ((operational / totalDeployed) * 100).toFixed(1) : 0;
  const criticalRepair = devices.filter(d => d.health < 50).length;
  const avgHealth = totalDeployed > 0
    ? (devices.reduce((sum, d) => sum + (d.health || 0), 0) / totalDeployed).toFixed(1)
    : 0;

  const sorted = useMemo(() =>
    [...devices].sort((a, b) => (b.risk_score || 0) - (a.risk_score || 0)),
    [devices]
  );

  const avgHardware = totalDeployed > 0
    ? (devices.reduce((sum, d) => sum + (d.power_level || 0), 0) / totalDeployed).toFixed(0)
    : 0;

  const signalStatus = state.metrics?.network_throughput_gbps > 0.5 ? 'NOMINAL' : 'LOW';

  return (
    <div className="view-unit-status" id="view-unit-status">
      {/* Top Stats Row */}
      <div className="unit-stats-row">
        <StatCard label="TOTAL_DEPLOYED" value={totalDeployed.toLocaleString()} unit=" UNITS" color="cyan" />
        <StatCard label="COMBAT_READY" value={combatReady} unit="%" color="cyan" />
        <StatCard label="CRITICAL_REPAIR" value={criticalRepair} unit=" UNITS"
          color={criticalRepair > 0 ? 'red' : 'cyan'}
          alert={criticalRepair > 0}
          sub={criticalRepair > 0 ? 'HIGH_PRIORITY' : ''} />
        <StatCard label="AVG_HEALTH" value={avgHealth} unit="%" color="green"
          progress={parseFloat(avgHealth)} />
      </div>

      {/* Main Content: Device Roster + Right Panel */}
      <div className="unit-main-grid">
        {/* Device Roster */}
        <div className="unit-roster">
          <div className="card-header" style={{ padding: '8px 16px', background: 'var(--bg-card)', borderBottom: '1px solid var(--border-primary)' }}>
            <span className="card-title">◻ TACTICAL_UNIT_ROSTER</span>
            <span className="font-mono text-dim" style={{ fontSize: 9 }}>SORT: RISK_DESC</span>
          </div>
          <div className="unit-roster-list">
            {sorted.map(device => (
              <DeviceCard
                key={device.mac}
                device={device}
                onIsolate={actions.isolateDevice}
                onRelease={actions.releaseDevice}
                onHoneypot={actions.deployHoneypot}
              />
            ))}
            {sorted.length === 0 && (
              <div className="text-dim font-mono" style={{ padding: 24, textAlign: 'center' }}>
                Awaiting device discovery...
              </div>
            )}
          </div>
        </div>

        {/* Right Panel */}
        <div className="unit-right-panel">
          {/* Readiness Metrics */}
          <div className="card" style={{ marginBottom: 12 }}>
            <div className="card-header">
              <span className="card-title">READINESS_METRICS</span>
            </div>
            <div className="card-body">
              <div className="unit-metric-row">
                <span className="font-mono" style={{ fontSize: 11 }}>PERSONNEL_AVAILABILITY</span>
                <span className="font-mono text-cyan" style={{ fontSize: 11 }}>{combatReady}%</span>
              </div>
              <div className="progress-bar" style={{ marginBottom: 12 }}>
                <div className="progress-fill cyan" style={{ width: `${combatReady}%` }} />
              </div>

              <div className="unit-metric-row">
                <span className="font-mono" style={{ fontSize: 11 }}>HARDWARE_INTEGRITY</span>
                <span className="font-mono text-cyan" style={{ fontSize: 11 }}>{avgHardware}%</span>
              </div>
              <div className="progress-bar" style={{ marginBottom: 12 }}>
                <div className={`progress-fill ${parseInt(avgHardware) > 60 ? 'cyan' : 'amber'}`}
                  style={{ width: `${avgHardware}%` }} />
              </div>

              <div className="unit-metric-row">
                <span className="font-mono" style={{ fontSize: 11 }}>SIGNAL_STRENGTH</span>
                <span className={`font-mono ${signalStatus === 'LOW' ? 'text-red' : 'text-green'}`}
                  style={{ fontSize: 11 }}>{signalStatus}</span>
              </div>
              <div className="progress-bar" style={{ marginBottom: 16 }}>
                <div className={`progress-fill ${signalStatus === 'LOW' ? 'red' : 'green'}`}
                  style={{ width: signalStatus === 'LOW' ? '25%' : '85%' }} />
              </div>

              <button className="btn btn-ghost" style={{ width: '100%' }} id="btn-run-diagnostics"
                onClick={() => actions.setSystemState('DEFENSE')}>
                RUN_ALL_DIAGNOSTICS
              </button>
            </div>
          </div>

          {/* Alerts */}
          <AlertPanel alerts={state.alerts} maxAlerts={5} />
        </div>
      </div>

      {/* Bottom Telemetry Table */}
      <div className="unit-telemetry card" style={{ marginTop: 12 }}>
        <div className="card-header">
          <div>
            <span className="font-mono text-dim" style={{ fontSize: 9, marginRight: 16 }}>SECURE_CHANNEL_ENCRYPTION: AES-4096-QUANTUM</span>
            <span className="font-heading" style={{ fontSize: 13, fontWeight: 600 }}>UNIT_HEALTH_TELEMETRY_STREAM</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span className="live-dot" />
            <span className="font-mono text-dim" style={{ fontSize: 9 }}>LIVE_FEED</span>
          </div>
        </div>
        <div style={{ overflowX: 'auto' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>UNIT_ID</th>
                <th>DESIGNATION</th>
                <th>HEALTH</th>
                <th>PWR_LEVEL</th>
                <th>TEMP_CORE</th>
                <th>STATUS_TAG</th>
                <th>LAST_PING</th>
              </tr>
            </thead>
            <tbody>
              {sorted.slice(0, 8).map(dev => (
                <tr key={dev.mac}>
                  <td className="text-cyan">#{dev.id}</td>
                  <td className={dev.health < 50 ? 'text-red' : ''}>{dev.hostname}</td>
                  <td className={dev.health < 50 ? 'text-red' : dev.health < 80 ? 'text-amber' : 'text-green'}>
                    {dev.health}%
                  </td>
                  <td>{dev.power_level}%</td>
                  <td>{dev.temperature}°C</td>
                  <td>
                    <span className={`badge ${
                      dev.status === 'isolated' ? 'badge-isolated' :
                      dev.status === 'suspicious' ? 'badge-warning' :
                      dev.risk_level === 'critical' ? 'badge-critical' :
                      'badge-active'
                    }`}>
                      {dev.status === 'isolated' ? 'ISOLATED' :
                       dev.status === 'suspicious' ? 'WARNING' :
                       dev.risk_level === 'critical' ? 'CRITICAL' :
                       'ACTIVE'}
                    </span>
                  </td>
                  <td>{dev.last_ping?.toFixed(2)}s AGO</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
