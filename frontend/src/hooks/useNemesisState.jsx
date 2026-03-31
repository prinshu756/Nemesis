import React, { createContext, useContext, useReducer, useCallback, useRef } from 'react';
import useWebSocket from './useWebSocket.jsx';

const MAX_LOGS = 200;
const MAX_ALERTS = 100;

const initialState = {
  devices: {},
  alerts: [],
  logs: [],
  threats: [],
  honeypots: {},
  metrics: {},
  networkMap: { devices: [], connections: [] },
  agents: { alpha: {}, beta: {}, gamma: {} },
  systemState: 'MONITORING',
  connected: false,
};

function reducer(state, action) {
  switch (action.type) {
    case 'INITIAL_STATE': {
      const d = action.payload;
      const devMap = {};
      if (d.devices) d.devices.forEach(dev => { devMap[dev.mac] = dev; });
      return {
        ...state,
        devices: devMap,
        systemState: d.system_state || d.status?.system_state || state.systemState,
      };
    }

    case 'DEVICE_DISCOVERED':
    case 'device_discovered': {
      const dev = action.payload?.device;
      if (!dev) return state;
      return { ...state, devices: { ...state.devices, [dev.mac]: dev } };
    }

    case 'DEVICE_UPDATED':
    case 'device_updated': {
      const dev = action.payload?.device;
      if (!dev) return state;
      return { ...state, devices: { ...state.devices, [dev.mac]: { ...state.devices[dev.mac], ...dev } } };
    }

    case 'DEVICE_ISOLATED':
    case 'device_isolated': {
      const { mac } = action.payload;
      if (!mac || !state.devices[mac]) return state;
      return {
        ...state,
        devices: {
          ...state.devices,
          [mac]: { ...state.devices[mac], status: 'isolated', isolation_status: action.payload.policy || 'full_isolation' }
        }
      };
    }

    case 'DEVICE_RELEASED':
    case 'device_released': {
      const { mac } = action.payload;
      if (!mac || !state.devices[mac]) return state;
      return {
        ...state,
        devices: {
          ...state.devices,
          [mac]: { ...state.devices[mac], status: 'online', isolation_status: 'normal' }
        }
      };
    }

    case 'ALERT_CREATED':
    case 'alert_created': {
      const alert = {
        id: action.id || Date.now(),
        timestamp: action.timestamp || Date.now() / 1000,
        ...action.payload,
      };
      return { ...state, alerts: [alert, ...state.alerts].slice(0, MAX_ALERTS) };
    }

    case 'LOG_ENTRY':
    case 'log_entry': {
      const log = {
        id: action.id || Date.now(),
        timestamp: action.timestamp || Date.now() / 1000,
        ...action.payload,
      };
      return { ...state, logs: [log, ...state.logs].slice(0, MAX_LOGS) };
    }

    case 'THREAT_DETECTED':
    case 'threat_detected': {
      const threat = {
        id: action.id || Date.now(),
        timestamp: action.timestamp || Date.now() / 1000,
        ...action.payload,
      };
      return { ...state, threats: [threat, ...state.threats].slice(0, 50) };
    }

    case 'HONEYPOT_DEPLOYED':
    case 'honeypot_deployed': {
      const hp = action.payload?.honeypot;
      if (!hp) return state;
      return { ...state, honeypots: { ...state.honeypots, [hp.id]: hp } };
    }

    case 'METRIC_UPDATE':
    case 'metric_update': {
      return { ...state, metrics: { ...state.metrics, ...action.payload } };
    }

    case 'NETWORK_MAP_UPDATE':
    case 'network_map_update': {
      return { ...state, networkMap: action.payload };
    }

    case 'SYSTEM_STATE_CHANGE':
    case 'system_state_change': {
      return { ...state, systemState: action.payload.new_state };
    }

    case 'AGENT_ACTION':
    case 'agent_action': {
      return state;
    }

    case 'ATTACK_STARTED':
    case 'attack_started': {
      return state; // threats handles display
    }

    case 'ATTACK_BLOCKED':
    case 'attack_blocked': {
      return state;
    }

    case 'SET_CONNECTED': {
      return { ...state, connected: action.payload };
    }

    default:
      return state;
  }
}

const NemesisContext = createContext(null);

export function NemesisProvider({ children }) {
  const [state, dispatch] = useReducer(reducer, initialState);
  const stateRef = useRef(state);
  stateRef.current = state;

  const handleEvent = useCallback((data) => {
    if (!data) return;

    // Initial state snapshot
    if (data.type === 'initial_state') {
      dispatch({ type: 'INITIAL_STATE', payload: data.payload });
      return;
    }

    // Heartbeat
    if (data.type === 'heartbeat' || data.type === 'pong') return;

    // Command result
    if (data.type === 'command_result') return;

    // Standard events from event bus
    if (data.type && data.payload) {
      dispatch({
        type: data.type,
        payload: data.payload,
        id: data.id,
        timestamp: data.timestamp,
      });
    }
  }, []);

  const { connected, sendCommand } = useWebSocket(handleEvent);

  // Sync connected state
  React.useEffect(() => {
    dispatch({ type: 'SET_CONNECTED', payload: connected });
  }, [connected]);

  const actions = React.useMemo(() => ({
    isolateDevice: (mac) => sendCommand('isolate', { mac }),
    releaseDevice: (mac) => sendCommand('release', { mac }),
    deployHoneypot: (target_ip, pot_type = 'generic') => sendCommand('honeypot', { target_ip, pot_type }),
    setSystemState: (newState) => sendCommand('set_state', { state: newState }),
    setSpeed: (mode, custom_value) => sendCommand('set_speed', { mode, custom_value }),
  }), [sendCommand]);

  return (
    <NemesisContext.Provider value={{ state, dispatch, actions }}>
      {children}
    </NemesisContext.Provider>
  );
}

export function useNemesis() {
  const ctx = useContext(NemesisContext);
  if (!ctx) throw new Error('useNemesis must be inside NemesisProvider');
  return ctx;
}
