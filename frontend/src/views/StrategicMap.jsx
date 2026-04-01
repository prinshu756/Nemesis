import React, { useState, useMemo } from 'react';
import { useNemesis } from '../hooks/useNemesisState.jsx';
import NetworkCanvas from '../components/NetworkCanvas';

export default function StrategicMap() {
  const { state, actions } = useNemesis();
  const [selectedDevice, setSelectedDevice] = useState(null);

  const devices = Object.values(state.devices);
  const mapData = state.networkMap;
  const recentAlerts = state.alerts.slice(0, 3);

  const mapDevices = useMemo(() => {
    return devices.map((d, idx) => ({
      mac: d.mac,
      ip: d.ip,
      hostname: d.hostname,
      type: d.device_type,
      device_type: d.device_type,
      status: d.status,
      risk_level: d.risk_level,
      isolation: d.isolation_status,
      // Use real coordinates if available, otherwise deterministic placement based on hash
      x: d.coordinates?.x !== undefined ? d.coordinates.x : (Math.abs(d.mac.split(':').reduce((a, b) => parseInt(a, 16) + parseInt(b, 16))) % 100) / 100,
      y: d.coordinates?.y !== undefined ? d.coordinates.y : (Math.abs((d.ip || '').split('.').reduce((a, b) => parseInt(a) + parseInt(b))) % 100) / 100,
      coordinates: d.coordinates,
    }));
  }, [devices]);

  const connections = mapData.connections || [];
  const onlineCount = devices.filter(d => d.status === 'online').length;
  const isolatedCount = devices.filter(d => d.status === 'isolated').length;
  const criticalCount = devices.filter(d => d.risk_level === 'critical').length;
  const topThreat = recentAlerts.length > 0 ? recentAlerts[0] : null;

  const handleNodeClick = (node) => {
    const fullDevice = state.devices[node.mac];
    setSelectedDevice(fullDevice || node);
  };

  const missionClock = useMemo(() => {
    const uptime = state.backendStatus?.system?.uptime_seconds || 
                   state.metrics?.uptime_seconds || 0;
    const hrs = String(Math.floor(uptime / 3600)).padStart(2, '0');
    const mins = String(Math.floor((uptime % 3600) / 60)).padStart(2, '0');
    const secs = String(uptime % 60).padStart(2, '0');
    return `${hrs}:${mins}:${secs}`;
  }, [state.backendStatus?.system?.uptime_seconds, state.metrics?.uptime_seconds]);

  return (
    <div className="view-strat-map" id="view-strat-map">
      {/* Main grid: map left, intel right */}
      <div className="strat-grid">
        {/* Map Area */}
        <div className="strat-map-area card corner-brackets">
          <div className="strat-map-coords font-mono text-cyan">
            <div>DEVICES_TRACKED: {devices.length}</div>
            <div>ONLINE_COUNT: {onlineCount}</div>
          </div>
          <NetworkCanvas
            devices={mapDevices}
            connections={connections}
            onNodeClick={handleNodeClick}
          />
          <div className="strat-map-version font-mono text-dim">MAP_RENDER_V4.30 | ANALYSIS_MODE: REALTIME</div>
        </div>

        {/* Right Panel */}
        <div className="strat-right-panel">
          {/* Tactical Overview */}
          <div className="card" style={{ marginBottom: 12 }}>
            {topThreat && (
              <div className="strat-priority-badge">HIGH_PRIORITY</div>
            )}
            <div className="card-body">
              <div className="font-mono text-dim" style={{ fontSize: 10, marginBottom: 4 }}>
                RCF_0092-X
              </div>
              <h2 className="font-heading" style={{ fontSize: 18, fontWeight: 700, color: 'var(--text-primary)', marginBottom: 12 }}>
                TACTICAL_OBJ_OVERVIEW
              </h2>
              <div className="font-mono text-dim" style={{ fontSize: 10, marginBottom: 4 }}>
                NETWORK_STATUS
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
                <span className="font-heading" style={{ fontSize: 15, fontWeight: 600 }}>
                  {onlineCount} ONLINE / {devices.length} TOTAL
                </span>
                <span className="font-mono text-cyan" style={{ fontSize: 10 }}>
                  {state.connected ? '92%_LOCK' : 'NO_LOCK'}
                </span>
              </div>
              <div style={{ display: 'flex', gap: 12 }}>
                <div style={{ flex: 1 }}>
                  <div className="font-mono text-dim" style={{ fontSize: 9 }}>THREAT_LVL</div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginTop: 4 }}>
                    <span className={`live-dot ${criticalCount > 0 ? 'red' : ''}`} />
                    <span className={`font-heading ${criticalCount > 0 ? 'text-red' : 'text-green'}`}
                      style={{ fontSize: 13, fontWeight: 600 }}>
                      {criticalCount > 0 ? 'CRITICAL' : 'NOMINAL'}
                    </span>
                  </div>
                </div>
                <div style={{ flex: 1 }}>
                  <div className="font-mono text-dim" style={{ fontSize: 9 }}>ENVIRONMENT</div>
                  <div className="font-heading" style={{ fontSize: 13, fontWeight: 600, marginTop: 4 }}>
                    URBAN_DENSE
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Active Assets */}
          <div className="card" style={{ flex: 1 }}>
            <div className="card-header">
              <span className="card-title">ACTIVE_ASSETS [{devices.length.toString().padStart(2, '0')}]</span>
            </div>
            <div className="strat-assets-list">
              {devices.slice(0, 8).map(dev => (
                <div key={dev.mac} className="strat-asset-item" onClick={() => setSelectedDevice(dev)}>
                  <div className="strat-asset-icon">
                    <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
                      <circle cx="14" cy="14" r="10" stroke={
                        dev.status === 'isolated' ? '#ff1744' :
                        dev.risk_level === 'critical' ? '#ff5252' :
                        '#00e5ff'
                      } strokeWidth="1" fill="rgba(0,229,255,0.05)" />
                    </svg>
                  </div>
                  <div style={{ flex: 1 }}>
                    <div className="font-heading" style={{ fontSize: 12, fontWeight: 600 }}>{dev.hostname}</div>
                  </div>
                  <span className={`badge ${
                    dev.status === 'isolated' ? 'badge-isolated' :
                    dev.status === 'suspicious' ? 'badge-warning' :
                    dev.risk_level === 'high' || dev.risk_level === 'critical' ? 'badge-warning' :
                    'badge-online'
                  }`}>
                    {dev.status === 'isolated' ? 'ISOLATED' :
                     dev.status === 'suspicious' ? 'SUSPECT' :
                     'ONLINE'}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Action Buttons */}
          <div style={{ display: 'flex', gap: 8, marginTop: 12 }}>
            <button className="btn btn-primary" style={{ flex: 1 }}
              onClick={() => actions.setSystemState('DEFENSE')} id="btn-execute-op">
              EXECUTE_OP
            </button>
            <button className="btn btn-danger" style={{ flex: 1 }}
              onClick={() => actions.setSystemState('MONITORING')} id="btn-abort-miss">
              ABORT_MISS
            </button>
          </div>
        </div>
      </div>

      {/* Bottom Stats */}
      <div className="strat-bottom-stats">
        <div className="strat-stat-item card">
          <div className="font-mono text-dim" style={{ fontSize: 9 }}>ATMOS_READING</div>
          <div className="font-heading text-cyan" style={{ fontSize: 28, fontWeight: 700, lineHeight: 1 }}>
            {(1013 + Math.random() * 2).toFixed(1)}
          </div>
          <div className="font-mono text-dim" style={{ fontSize: 8 }}>MBAR // SURFACE_AVG</div>
        </div>
        <div className="strat-stat-item card">
          <div className="font-mono text-dim" style={{ fontSize: 9 }}>SIGNAL_STRENGTH</div>
          <div style={{ display: 'flex', alignItems: 'flex-end', gap: 3, margin: '8px 0' }}>
            {[20, 40, 60, 80, 100].map((h, i) => (
              <div key={i} style={{
                width: 5, height: h * 0.3, borderRadius: 1,
                background: i < 4 ? 'var(--cyan-400)' : 'var(--bg-tertiary)',
                boxShadow: i < 4 ? '0 0 4px rgba(0,229,255,0.3)' : 'none',
              }} />
            ))}
          </div>
          <div className="font-mono text-cyan" style={{ fontSize: 9 }}>SECURE_SAT_LINK</div>
        </div>
        <div className="strat-stat-item card">
          <div className="font-mono text-dim" style={{ fontSize: 9 }}>MISSION_CLOCK</div>
          <div className="font-heading" style={{ fontSize: 28, fontWeight: 700, lineHeight: 1, color: 'var(--text-primary)' }}>
            {missionClock}
          </div>
          <div className="font-mono text-dim" style={{ fontSize: 8 }}>T_MINUS // TARGET_INTER</div>
        </div>
        <div className="strat-stat-item card">
          <div className="font-mono text-dim" style={{ fontSize: 9 }}>THREAT_VECTOR</div>
          <div className={`font-heading ${criticalCount > 0 ? 'text-red' : 'text-cyan'}`}
            style={{ fontSize: 24, fontWeight: 700, lineHeight: 1.2 }}>
            {criticalCount > 0 ? `${criticalCount} ACTIVE` : 'CLEAR'}
          </div>
          <div className="font-mono text-dim" style={{ fontSize: 8 }}>
            {criticalCount > 0 ? 'HOSTILE_CON_DETECT' : 'NO_HOSTILE_CONTACT'}
          </div>
        </div>
      </div>

      {/* Honeypots & Policies */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginTop: 16 }}>
        {/* Honeypot Deployments */}
        <div className="card">
          <div className="card-header">
            <span className="card-title">🍯 HONEYPOT_DEPLOYMENTS</span>
          </div>
          <div className="card-body">
            {state.backendStatus?.honeypots?.honeypots?.length > 0 ? (
              <div>
                <div className="font-mono" style={{ marginBottom: 8 }}>
                  <span className="text-cyan">{state.backendStatus.honeypots.active_count}</span>
                  <span className="text-dim"> active honeypots deployed</span>
                </div>
                <div style={{ maxHeight: 150, overflowY: 'auto' }}>
                  {state.backendStatus.honeypots.honeypots.map((hp, idx) => (
                    <div key={idx} className="font-mono" style={{ padding: 4, borderBottom: '1px solid rgba(0,229,255,0.1)', fontSize: 10 }}>
                      <div className="text-cyan">{hp.ip || hp.target || 'Unknown'}</div>
                      <div className="text-dim">{hp.type || hp.honeypot_type || 'generic'}</div>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="text-dim font-mono">No active honeypots</div>
            )}
          </div>
        </div>

        {/* Security Policies */}
        <div className="card">
          <div className="card-header">
            <span className="card-title">🛡️ SECURITY_POLICIES</span>
          </div>
          <div className="card-body">
            {state.backendStatus?.security_policies?.total_policies > 0 ? (
              <div>
                <div className="font-mono" style={{ marginBottom: 8 }}>
                  <span className="text-green">{state.backendStatus.security_policies.total_policies}</span>
                  <span className="text-dim"> active policies</span>
                </div>
                <div style={{ maxHeight: 150, overflowY: 'auto' }}>
                  {Object.entries(state.backendStatus.security_policies.policies || {}).slice(0, 8).map(([key, policy], idx) => (
                    <div key={idx} className="font-mono" style={{ padding: 4, borderBottom: '1px solid rgba(0,255,0,0.1)', fontSize: 10 }}>
                      <div className="text-green">{key}</div>
                      <div className="text-dim">{typeof policy === 'string' ? policy.substring(0, 40) : 'Policy active'}</div>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="text-dim font-mono">No policies configured</div>
            )}
          </div>
        </div>
      </div>

      {/* Device Detail Modal */}
      {selectedDevice && (
        <div className="strat-modal-overlay" onClick={() => setSelectedDevice(null)}>
          <div className="strat-modal card" onClick={e => e.stopPropagation()}>
            <div className="card-header">
              <span className="card-title">DEVICE_INTEL // {selectedDevice.id}</span>
              <button className="btn btn-ghost" style={{ padding: '2px 8px', fontSize: 9 }}
                onClick={() => setSelectedDevice(null)}>✕</button>
            </div>
            <div className="card-body font-mono" style={{ fontSize: 11 }}>
              <div className="strat-modal-row"><span className="text-dim">HOSTNAME</span><span>{selectedDevice.hostname}</span></div>
              <div className="strat-modal-row"><span className="text-dim">IP</span><span className="text-cyan">{selectedDevice.ip}</span></div>
              <div className="strat-modal-row"><span className="text-dim">MAC</span><span>{selectedDevice.mac}</span></div>
              <div className="strat-modal-row"><span className="text-dim">TYPE</span><span>{selectedDevice.device_type}</span></div>
              <div className="strat-modal-row"><span className="text-dim">VENDOR</span><span>{selectedDevice.vendor}</span></div>
              <div className="strat-modal-row"><span className="text-dim">OS</span><span>{selectedDevice.os_fingerprint}</span></div>
              <div className="strat-modal-row"><span className="text-dim">RISK</span>
                <span className={selectedDevice.risk_level === 'critical' ? 'text-red' : selectedDevice.risk_level === 'high' ? 'text-amber' : 'text-green'}>
                  {selectedDevice.risk_score} ({selectedDevice.risk_level?.toUpperCase()})
                </span>
              </div>
              <div className="strat-modal-row"><span className="text-dim">STATUS</span>
                <span className={selectedDevice.status === 'isolated' ? 'text-red' : 'text-cyan'}>
                  {selectedDevice.status?.toUpperCase()}
                </span>
              </div>
              <div className="strat-modal-row"><span className="text-dim">SEGMENT</span><span>{selectedDevice.segment_label}</span></div>
              <div className="strat-modal-row"><span className="text-dim">PORTS</span><span>{selectedDevice.ports?.join(', ')}</span></div>
              <div style={{ display: 'flex', gap: 8, marginTop: 16 }}>
                {selectedDevice.isolation_status === 'normal' ? (
                  <>
                    <button className="btn btn-danger" style={{ flex: 1 }}
                      onClick={() => { actions.isolateDevice(selectedDevice.mac); setSelectedDevice(null); }}>
                      ISOLATE_DEVICE
                    </button>
                    <button className="btn btn-ghost" style={{ flex: 1 }}
                      onClick={() => { actions.deployHoneypot(selectedDevice.ip); setSelectedDevice(null); }}>
                      DEPLOY_HONEYPOT
                    </button>
                  </>
                ) : (
                  <button className="btn btn-primary" style={{ flex: 1 }}
                    onClick={() => { actions.releaseDevice(selectedDevice.mac); setSelectedDevice(null); }}>
                    RELEASE_DEVICE
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
