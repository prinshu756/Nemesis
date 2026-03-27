import React, { useEffect, useState } from "react";
import "./Dashboard.css";

export default function Dashboard() {
  const [data, setData] = useState({
    devices: [],
    alerts: [],
    status: {},
    timestamp: 0
  });
  const [wsConnected, setWsConnected] = useState(false);
  const [selectedDevice, setSelectedDevice] = useState(null);

  useEffect(() => {
    const ws = new WebSocket("ws://localhost:8001/ws");

    ws.onopen = () => {
      setWsConnected(true);
    };

    ws.onclose = () => {
      setWsConnected(false);
    };

    ws.onmessage = (event) => {
      try {
        const newData = JSON.parse(event.data);
        setData(newData);
      } catch (e) {
        console.error("Failed to parse WebSocket data:", e);
      }
    };

    ws.onerror = (error) => {
      console.error("WebSocket error:", error);
      setWsConnected(false);
    };

    return () => {
      ws.close();
    };
  }, []);

  const getRiskColor = (level) => {
    switch (level) {
      case "critical": return "#dc2626";
      case "high": return "#ea580c";
      case "medium": return "#ca8a04";
      case "low": return "#16a34a";
      default: return "#6b7280";
    }
  };

  const getRiskBadge = (level) => {
    const colors = {
      critical: "bg-red-500",
      high: "bg-orange-500",
      medium: "bg-yellow-500",
      low: "bg-green-500"
    };
    return colors[level] || "bg-gray-500";
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp * 1000).toLocaleTimeString();
  };

  return (
    <div className="dashboard">
      {/* Header */}
      <header className="header">
        <div className="header-content">
          <h1 className="title">NEMESIS SOC</h1>
          <div className="status-indicator">
            <div className={`status-dot ${wsConnected ? 'connected' : 'disconnected'}`}></div>
            <span>{wsConnected ? 'Connected' : 'Disconnected'}</span>
          </div>
        </div>
        <div className="last-update">
          Last Update: {formatTimestamp(data.timestamp)}
        </div>
      </header>

      {/* Stats Cards */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">🖥️</div>
          <div className="stat-content">
            <div className="stat-number">{data.devices.length}</div>
            <div className="stat-label">Devices</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">🚨</div>
          <div className="stat-content">
            <div className="stat-number">{data.alerts.length}</div>
            <div className="stat-label">Active Alerts</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">🛡️</div>
          <div className="stat-content">
            <div className="stat-number">{data.status.beta_honeypots || 0}</div>
            <div className="stat-label">Honeypots</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">⚡</div>
          <div className="stat-content">
            <div className="stat-number">{data.status.gamma_policies?.policies ? Object.keys(data.status.gamma_policies.policies).length : 0}</div>
            <div className="stat-label">Policies</div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="main-content">
        {/* Devices Section */}
        <div className="section">
          <h2 className="section-title">Network Devices</h2>
          <div className="devices-grid">
            {data.devices.map((device) => (
              <div
                key={device.mac}
                className={`device-card ${selectedDevice === device.mac ? 'selected' : ''}`}
                onClick={() => setSelectedDevice(device.mac === selectedDevice ? null : device.mac)}
              >
                <div className="device-header">
                  <div className="device-mac">{device.mac}</div>
                  <div
                    className={`risk-badge ${getRiskBadge(device.risk_level)}`}
                  >
                    {device.risk_level?.toUpperCase() || 'UNKNOWN'}
                  </div>
                </div>

                <div className="device-details">
                  <div className="device-ip">IP: {device.ip || 'Unknown'}</div>
                  <div className="device-type">Type: {device.device_type || 'Unknown'}</div>
                  <div className="device-risk">Risk Score: {device.risk_score?.toFixed(2) || 'N/A'}</div>
                  <div className="device-packets">Packets: {device.packet_count || 0}</div>
                </div>

                {selectedDevice === device.mac && (
                  <div className="device-actions">
                    <button className="action-btn isolate">Isolate Device</button>
                    <button className="action-btn honeypot">Deploy Honeypot</button>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Alerts Section */}
        <div className="section">
          <h2 className="section-title">Recent Alerts</h2>
          <div className="alerts-list">
            {data.alerts.slice(0, 10).map((alert, index) => (
              <div key={index} className="alert-item">
                <div className="alert-time">{new Date(alert.timestamp).toLocaleString()}</div>
                <div className="alert-message">{alert.message || JSON.stringify(alert)}</div>
                <div className="alert-level" style={{ color: getRiskColor(alert.level) }}>
                  {alert.level?.toUpperCase() || 'INFO'}
                </div>
              </div>
            ))}
            {data.alerts.length === 0 && (
              <div className="no-alerts">No active alerts</div>
            )}
          </div>
        </div>

        {/* System Status */}
        <div className="section">
          <h2 className="section-title">System Status</h2>
          <div className="status-grid">
            <div className="status-item">
              <span className="status-label">Alpha Agent:</span>
              <span className={`status-value ${data.status.alpha ? 'active' : 'inactive'}`}>
                {data.status.alpha ? 'Active' : 'Inactive'}
              </span>
            </div>
            <div className="status-item">
              <span className="status-label">Beta Agent:</span>
              <span className={`status-value ${data.status.beta ? 'active' : 'inactive'}`}>
                {data.status.beta ? 'Active' : 'Inactive'}
              </span>
            </div>
            <div className="status-item">
              <span className="status-label">Gamma Agent:</span>
              <span className={`status-value ${data.status.gamma ? 'active' : 'inactive'}`}>
                {data.status.gamma ? 'Active' : 'Inactive'}
              </span>
            </div>
            <div className="status-item">
              <span className="status-label">eBPF Status:</span>
              <span className={`status-value ${data.status.gamma_policies?.ebpf_attached ? 'active' : 'inactive'}`}>
                {data.status.gamma_policies?.ebpf_attached ? 'Attached' : 'Detached'}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}