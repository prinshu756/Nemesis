import { useEffect, useCallback, useRef } from 'react';
import API from '../services/api.js';

/**
 * Hook for periodic data fetching and database persistence
 */
export function useDataPersistence(dispatch, state) {
  const intervalRef = useRef(null);
  const lastSyncRef = useRef(0);
  const SYNC_INTERVAL = 30000; // Sync every 30 seconds

  const syncToDatabase = useCallback(async () => {
    const now = Date.now();
    if (now - lastSyncRef.current < SYNC_INTERVAL) return;
    
    lastSyncRef.current = now;

    try {
      // Save devices to database
      if (Object.keys(state.devices).length > 0) {
        await API.saveDevicesToDatabase();
        console.log('✓ Devices synced to database');
      }

      // Save alerts to database
      if (state.alerts.length > 0) {
        await API.saveAlertsToDatabase();
        console.log('✓ Alerts synced to database');
      }
    } catch (error) {
      console.error('Error syncing to database:', error);
    }
  }, [state.devices, state.alerts]);

  const fetchFromApi = useCallback(async () => {
    try {
      // Check API health
      const healthCheck = await API.healthCheck();
      if (!healthCheck.status) return;

      // Fetch current devices
      const devicesResponse = await API.getDevices();
      if (devicesResponse.devices) {
        dispatch({
          type: 'BULK_UPDATE_DEVICES',
          payload: devicesResponse.devices
        });
      }

      // Fetch current alerts
      const alertsResponse = await API.getAlerts(50);
      if (alertsResponse.alerts) {
        dispatch({
          type: 'BULK_UPDATE_ALERTS',
          payload: alertsResponse.alerts
        });
      }

      // Fetch traffic logs
      const trafficResponse = await API.getTrafficLogs(100);
      if (trafficResponse.traffic_logs) {
        dispatch({
          type: 'BULK_UPDATE_TRAFFIC_LOGS',
          payload: trafficResponse.traffic_logs
        });
      }

      // Fetch anomalies
      const anomaliesResponse = await API.getAnomalies(100);
      if (anomaliesResponse.anomalies) {
        dispatch({
          type: 'BULK_UPDATE_ANOMALIES',
          payload: anomaliesResponse.anomalies
        });
      }

      // Fetch honeypot detections
      const honeypotResponse = await API.getHoneypotDetections(100);
      if (honeypotResponse.honeypot_detections) {
        dispatch({
          type: 'BULK_UPDATE_HONEYPOT_DETECTIONS',
          payload: honeypotResponse.honeypot_detections
        });
      }

      // Fetch backend status (metrics)
      const backendStatus = await API.getBackendStatus();
      if (backendStatus) {
        dispatch({
          type: 'UPDATE_BACKEND_STATUS',
          payload: backendStatus
        });
      }

      // Sync to database periodically
      syncToDatabase();
    } catch (error) {
      console.warn('Error fetching from API:', error.message);
    }
  }, [dispatch, syncToDatabase]);

  useEffect(() => {
    // Initial fetch
    fetchFromApi();

    // Set up periodic fetching
    intervalRef.current = setInterval(fetchFromApi, 5000); // Fetch every 5 seconds

    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [fetchFromApi]);

  return { syncToDatabase };
}

/**
 * Hook for loading persisted data from database
 */
export async function loadPersistedData(dispatch) {
  try {
    const [devicesRes, alertsRes, trafficRes] = await Promise.allSettled([
      API.getPersistedDevices(50),
      API.getPersistedAlerts(50),
      API.getPersistedTraffic(100)
    ]);

    if (devicesRes.status === 'fulfilled' && devicesRes.value.devices) {
      dispatch({
        type: 'BULK_UPDATE_DEVICES',
        payload: devicesRes.value.devices
      });
    }

    if (alertsRes.status === 'fulfilled' && alertsRes.value.alerts) {
      dispatch({
        type: 'BULK_UPDATE_ALERTS',
        payload: alertsRes.value.alerts
      });
    }

    console.log('✓ Persisted data loaded from database');
  } catch (error) {
    console.warn('Could not load persisted data:', error.message);
  }
}
