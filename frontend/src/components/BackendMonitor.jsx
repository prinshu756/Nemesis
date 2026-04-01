import React, { useState, useEffect } from 'react';
import API from '../services/api.js';
import '../css/BackendMonitor.css';

export default function BackendMonitor() {
  const [backendStatus, setBackendStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [expandedSection, setExpandedSection] = useState('overview');

  useEffect(() => {
    const fetchBackendStatus = async () => {
      try {
        setLoading(true);
        const response = await fetch('http://localhost:8000/backend/status');
        if (!response.ok) throw new Error('Failed to fetch backend status');
        const data = await response.json();
        setBackendStatus(data);
        setError(null);
      } catch (err) {
        setError(err.message);
        console.error('Backend status error:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchBackendStatus();
    const interval = setInterval(fetchBackendStatus, 2000);
    return () => clearInterval(interval);
  }, []);

  if (loading) return <div className="backend-monitor loading">Loading backend status...</div>;
  if (error) return <div className="backend-monitor error">Error: {error}</div>;
  if (!backendStatus) return <div className="backend-monitor error">No backend data available</div>;

  return (
    <div className="backend-monitor">
      <h1>🎛️ Backend System Monitor</h1>
      
      {/* System Overview */}
      <div className="monitor-section overview-section">
        <h2 onClick={() => setExpandedSection(expandedSection === 'overview' ? null : 'overview')}>
          📊 System Overview {expandedSection === 'overview' ? '▼' : '▶'}
        </h2>
        {expandedSection === 'overview' && (
          <div className="section-content">
            <div className="metrics-grid">
              <div className="metric-card cpu">
                <div className="metric-label">CPU Usage</div>
                <div className="metric-value">{backendStatus.system.cpu_usage_percent.toFixed(1)}%</div>
                <div className="metric-bar">
                  <div 
                    className="metric-bar-fill" 
                    style={{width: `${backendStatus.system.cpu_usage_percent}%`}}
                  ></div>
                </div>
              </div>

              <div className="metric-card memory">
                <div className="metric-label">Memory Usage</div>
                <div className="metric-value">{backendStatus.system.memory_usage_mb}MB</div>
                <div className="metric-bar">
                  <div 
                    className="metric-bar-fill" 
                    style={{width: `${Math.min(backendStatus.system.memory_usage_mb / 10, 100)}%`}}
                  ></div>
                </div>
              </div>

              <div className="metric-card status">
                <div className="metric-label">System Status</div>
                <div className="metric-value status-running">🟢 RUNNING</div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Network Monitoring */}
      <div className="monitor-section network-section">
        <h2 onClick={() => setExpandedSection(expandedSection === 'network' ? null : 'network')}>
          📱 Network Monitoring {expandedSection === 'network' ? '▼' : '▶'}
        </h2>
        {expandedSection === 'network' && (
          <div className="section-content">
            <div className="stats-grid">
              <div className="stat-box">
                <div className="stat-number">{backendStatus.network_monitoring.total_devices}</div>
                <div className="stat-label">Total Devices</div>
              </div>
              <div className="stat-box">
                <div className="stat-number">{backendStatus.network_monitoring.active_devices}</div>
                <div className="stat-label">Active Devices</div>
              </div>
              <div className="stat-box danger">
                <div className="stat-number">{backendStatus.network_monitoring.high_risk_devices}</div>
                <div className="stat-label">High Risk Devices</div>
              </div>
              <div className="stat-box warning">
                <div className="stat-number">{backendStatus.network_monitoring.devices_isolated}</div>
                <div className="stat-label">Isolated Devices</div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Alerts Dashboard */}
      <div className="monitor-section alerts-section">
        <h2 onClick={() => setExpandedSection(expandedSection === 'alerts' ? null : 'alerts')}>
          🚨 Alerts Dashboard {expandedSection === 'alerts' ? '▼' : '▶'}
        </h2>
        {expandedSection === 'alerts' && (
          <div className="section-content">
            <div className="stats-grid">
              <div className="stat-box">
                <div className="stat-number">{backendStatus.alerts.total_alerts}</div>
                <div className="stat-label">Total Alerts</div>
              </div>
              <div className="stat-box critical">
                <div className="stat-number">{backendStatus.alerts.critical}</div>
                <div className="stat-label">🔴 Critical</div>
              </div>
              <div className="stat-box danger">
                <div className="stat-number">{backendStatus.alerts.high}</div>
                <div className="stat-label">🟠 High</div>
              </div>
              <div className="stat-box warning">
                <div className="stat-number">{backendStatus.alerts.medium}</div>
                <div className="stat-label">🟡 Medium</div>
              </div>
              <div className="stat-box">
                <div className="stat-number">{backendStatus.alerts.low}</div>
                <div className="stat-label">🟢 Low</div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Honeypots */}
      <div className="monitor-section honeypots-section">
        <h2 onClick={() => setExpandedSection(expandedSection === 'honeypots' ? null : 'honeypots')}>
          🍯 Honeypot Deployments {expandedSection === 'honeypots' ? '▼' : '▶'}
        </h2>
        {expandedSection === 'honeypots' && (
          <div className="section-content">
            <div className="stat-box">
              <div className="stat-number">{backendStatus.honeypots.active_count}</div>
              <div className="stat-label">Active Honeypots</div>
            </div>
            {backendStatus.honeypots.honeypots && backendStatus.honeypots.honeypots.length > 0 && (
              <div className="honeypot-list">
                {backendStatus.honeypots.honeypots.map((hp, idx) => (
                  <div key={idx} className="honeypot-item">
                    <span className="honeypot-ip">{hp.ip || hp.target || 'N/A'}</span>
                    <span className="honeypot-type">{hp.type || hp.honeypot_type || 'generic'}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Security Policies */}
      <div className="monitor-section policies-section">
        <h2 onClick={() => setExpandedSection(expandedSection === 'policies' ? null : 'policies')}>
          🛡️ Security Policies {expandedSection === 'policies' ? '▼' : '▶'}
        </h2>
        {expandedSection === 'policies' && (
          <div className="section-content">
            <div className="stat-box">
              <div className="stat-number">{backendStatus.security_policies.total_policies}</div>
              <div className="stat-label">Active Policies</div>
            </div>
            {Object.entries(backendStatus.security_policies.policies || {}).length > 0 && (
              <div className="policies-list">
                {Object.entries(backendStatus.security_policies.policies).map(([key, policy], idx) => (
                  <div key={idx} className="policy-item">
                    <span className="policy-name">{key}</span>
                    <span className="policy-status">
                      {JSON.stringify(policy).substring(0, 50)}...
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Agent Status */}
      <div className="monitor-section agents-section">
        <h2 onClick={() => setExpandedSection(expandedSection === 'agents' ? null : 'agents')}>
          🤖 AI Agents Status {expandedSection === 'agents' ? '▼' : '▶'}
        </h2>
        {expandedSection === 'agents' && (
          <div className="section-content">
            <div className="agents-grid">
              {Object.entries(backendStatus.agents).map(([key, agent]) => (
                <div key={key} className={`agent-card ${agent.status}`}>
                  <div className="agent-header">
                    <span className="agent-name">{agent.name.toUpperCase()}</span>
                    <span className={`agent-status ${agent.status}`}>
                      {agent.status === 'active' ? '🟢' : '🔴'} {agent.status.toUpperCase()}
                    </span>
                  </div>
                  <div className="agent-function">{agent.function}</div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Database Status */}
      <div className="monitor-section database-section">
        <h2 onClick={() => setExpandedSection(expandedSection === 'database' ? null : 'database')}>
          💾 Database Status {expandedSection === 'database' ? '▼' : '▶'}
        </h2>
        {expandedSection === 'database' && (
          <div className="section-content">
            <div className="database-info">
              <div className="db-section">
                <h3>📁 Local SQLite Database</h3>
                <div className="db-stats">
                  <div className="db-stat">
                    <span>Devices:</span>
                    <strong>{backendStatus.database.local.devices}</strong>
                  </div>
                  <div className="db-stat">
                    <span>Alerts:</span>
                    <strong>{backendStatus.database.local.alerts}</strong>
                  </div>
                  <div className="db-stat">
                    <span>Traffic Logs:</span>
                    <strong>{backendStatus.database.local.traffic_logs}</strong>
                  </div>
                  <div className="db-stat">
                    <span>Honeypot Interactions:</span>
                    <strong>{backendStatus.database.local.honeypot_interactions}</strong>
                  </div>
                  <div className="db-stat total">
                    <span>TOTAL RECORDS:</span>
                    <strong>{backendStatus.database.local.total_records}</strong>
                  </div>
                </div>
              </div>

              <div className="db-section">
                <h3>☁️ Neon PostgreSQL Database</h3>
                <div className="db-status">
                  <span className="status-label">Status:</span>
                  <span className={`status-value ${backendStatus.database.neon.status}`}>
                    {backendStatus.database.neon.status === 'connected' ? '🟢' : '🔴'} 
                    {backendStatus.database.neon.status.toUpperCase()}
                  </span>
                </div>
                <div className="db-type">Cloud PostgreSQL - Production Ready</div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Recent Events */}
      <div className="monitor-section events-section">
        <h2 onClick={() => setExpandedSection(expandedSection === 'events' ? null : 'events')}>
          📋 Recent Events {expandedSection === 'events' ? '▼' : '▶'}
        </h2>
        {expandedSection === 'events' && (
          <div className="section-content">
            <div className="events-grid">
              <div className="events-column">
                <h3>Latest Devices Discovered</h3>
                {backendStatus.recent_events.latest_devices && backendStatus.recent_events.latest_devices.length > 0 ? (
                  <div className="event-list">
                    {backendStatus.recent_events.latest_devices.map((device, idx) => (
                      <div key={idx} className="event-item">
                        <span className="event-ip">{device.ip || 'N/A'}</span>
                        <span className="event-type">{device.device_type || 'unknown'}</span>
                        <span className={`event-risk risk-${device.risk_level || 'low'}`}>
                          {device.risk_score ? device.risk_score.toFixed(1) : 'N/A'}
                        </span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="no-data">No devices discovered</div>
                )}
              </div>

              <div className="events-column">
                <h3>Latest Alerts</h3>
                {backendStatus.recent_events.latest_alerts && backendStatus.recent_events.latest_alerts.length > 0 ? (
                  <div className="event-list">
                    {backendStatus.recent_events.latest_alerts.map((alert, idx) => (
                      <div key={idx} className={`event-item alert-${alert.severity || 'low'}`}>
                        <span className="event-message">{alert.message || 'Alert'}</span>
                        <span className={`event-severity severity-${alert.severity || 'low'}`}>
                          {alert.severity ? alert.severity.toUpperCase() : 'LOW'}
                        </span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="no-data">No alerts</div>
                )}
              </div>
            </div>

            <div className="total-threats">
              <strong>🎯 Total Threats Detected: {backendStatus.recent_events.total_threats_detected}</strong>
            </div>
          </div>
        )}
      </div>

      {/* Auto-refresh indicator */}
      <div className="refresh-indicator">
        ⟳ Auto-refreshing every 2 seconds
      </div>
    </div>
  );
}
