import React, { useEffect, useState } from "react";

export default function Dashboard() {
  const [data, setData] = useState({ devices: {}, alerts: [] });

  useEffect(() => {
    const ws = new WebSocket("ws://localhost:8000/ws");

    ws.onmessage = (event) => {
      setData(JSON.parse(event.data));
    };
  }, []);

  return (
    <div>
      <h1>NEMESIS SOC</h1>

      <h2>Devices</h2>
      <pre>{JSON.stringify(data.devices, null, 2)}</pre>

      <h2>Alerts</h2>
      <pre>{JSON.stringify(data.alerts, null, 2)}</pre>
    </div>
  );
}