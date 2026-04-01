/**
 * API Service for Nemesis Frontend
 * Handles all HTTP communication with backend
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * Default fetch options with error handling
 */
const defaultOptions = {
  headers: {
    'Content-Type': 'application/json',
  },
};

/**
 * Handle API responses
 */
async function handleResponse(response) {
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || `API Error: ${response.status}`);
  }
  return response.json();
}

/**
 * API Service Object
 */
const API = {
  // ============ REAL-TIME DATA ENDPOINTS ============

  /**
   * Get all current devices from orchestrator
   */
  async getDevices() {
    try {
      const response = await fetch(`${API_BASE_URL}/devices`, defaultOptions);
      return handleResponse(response);
    } catch (error) {
      console.error('Failed to fetch devices:', error);
      throw error;
    }
  },

  /**
   * Get specific device details
   */
  async getDeviceDetail(mac) {
    try {
      const response = await fetch(`${API_BASE_URL}/devices/${mac}`, defaultOptions);
      return handleResponse(response);
    } catch (error) {
      console.error(`Failed to fetch device ${mac}:`, error);
      throw error;
    }
  },

  /**
   * Get current alerts
   */
  async getAlerts(limit = 50) {
    try {
      const response = await fetch(`${API_BASE_URL}/alerts?limit=${limit}`, defaultOptions);
      return handleResponse(response);
    } catch (error) {
      console.error('Failed to fetch alerts:', error);
      throw error;
    }
  },

  /**
   * Get system status
   */
  async getSystemStatus() {
    try {
      const response = await fetch(`${API_BASE_URL}/status`, defaultOptions);
      return handleResponse(response);
    } catch (error) {
      console.error('Failed to fetch system status:', error);
      throw error;
    }
  },

  /**
   * Get active honeypots
   */
  async getHoneypots() {
    try {
      const response = await fetch(`${API_BASE_URL}/honeypots`, defaultOptions);
      return handleResponse(response);
    } catch (error) {
      console.error('Failed to fetch honeypots:', error);
      throw error;
    }
  },

  /**
   * Get segmentation policies
   */
  async getPolicies() {
    try {
      const response = await fetch(`${API_BASE_URL}/policies`, defaultOptions);
      return handleResponse(response);
    } catch (error) {
      console.error('Failed to fetch policies:', error);
      throw error;
    }
  },

  /**
   * Get traffic logs
   */
  async getTrafficLogs(limit = 100) {
    try {
      const response = await fetch(`${API_BASE_URL}/traffic?limit=${limit}`, defaultOptions);
      return handleResponse(response);
    } catch (error) {
      console.error('Failed to fetch traffic logs:', error);
      throw error;
    }
  },

  /**
   * Get honeypot detections
   */
  async getHoneypotDetections(limit = 100) {
    try {
      const response = await fetch(`${API_BASE_URL}/honeypots/detection?limit=${limit}`, defaultOptions);
      return handleResponse(response);
    } catch (error) {
      console.error('Failed to fetch honeypot detections:', error);
      throw error;
    }
  },

  /**
   * Get detected anomalies
   */
  async getAnomalies(limit = 100) {
    try {
      const response = await fetch(`${API_BASE_URL}/anomalies?limit=${limit}`, defaultOptions);
      return handleResponse(response);
    } catch (error) {
      console.error('Failed to fetch anomalies:', error);
      throw error;
    }
  },

  // ============ DEVICE ACTIONS ============

  /**
   * Isolate a device
   */
  async isolateDevice(mac, policy = 'full_isolation') {
    try {
      const response = await fetch(`${API_BASE_URL}/devices/${mac}/isolate?policy=${policy}`, {
        ...defaultOptions,
        method: 'POST',
      });
      return handleResponse(response);
    } catch (error) {
      console.error(`Failed to isolate device ${mac}:`, error);
      throw error;
    }
  },

  /**
   * Deploy honeypot for a device
   */
  async deployHoneypot(mac) {
    try {
      const response = await fetch(`${API_BASE_URL}/devices/${mac}/honeypot`, {
        ...defaultOptions,
        method: 'POST',
      });
      return handleResponse(response);
    } catch (error) {
      console.error(`Failed to deploy honeypot for ${mac}:`, error);
      throw error;
    }
  },

  // ============ DATABASE PERSISTENCE ENDPOINTS ============

  /**
   * Save all devices to database
   */
  async saveDevicesToDatabase() {
    try {
      const response = await fetch(`${API_BASE_URL}/db/devices`, {
        ...defaultOptions,
        method: 'POST',
      });
      return handleResponse(response);
    } catch (error) {
      console.error('Failed to save devices to database:', error);
      throw error;
    }
  },

  /**
   * Save single device to database
   */
  async saveSingleDeviceToDatabase(mac) {
    try {
      const response = await fetch(`${API_BASE_URL}/db/device/${mac}`, {
        ...defaultOptions,
        method: 'POST',
      });
      return handleResponse(response);
    } catch (error) {
      console.error(`Failed to save device ${mac} to database:`, error);
      throw error;
    }
  },

  /**
   * Save all alerts to database
   */
  async saveAlertsToDatabase() {
    try {
      const response = await fetch(`${API_BASE_URL}/db/alerts`, {
        ...defaultOptions,
        method: 'POST',
      });
      return handleResponse(response);
    } catch (error) {
      console.error('Failed to save alerts to database:', error);
      throw error;
    }
  },

  /**
   * Save single alert to database
   */
  async saveAlertToDatabase(alertData) {
    try {
      const response = await fetch(`${API_BASE_URL}/db/alert`, {
        ...defaultOptions,
        method: 'POST',
        body: JSON.stringify(alertData),
      });
      return handleResponse(response);
    } catch (error) {
      console.error('Failed to save alert to database:', error);
      throw error;
    }
  },

  /**
   * Save traffic log to database
   */
  async saveTrafficToDatabase(trafficData) {
    try {
      const response = await fetch(`${API_BASE_URL}/db/traffic`, {
        ...defaultOptions,
        method: 'POST',
        body: JSON.stringify(trafficData),
      });
      return handleResponse(response);
    } catch (error) {
      console.error('Failed to save traffic to database:', error);
      throw error;
    }
  },

  /**
   * Save honeypot interaction to database
   */
  async saveHoneypotInteractionToDatabase(interactionData) {
    try {
      const response = await fetch(`${API_BASE_URL}/db/honeypot-interaction`, {
        ...defaultOptions,
        method: 'POST',
        body: JSON.stringify(interactionData),
      });
      return handleResponse(response);
    } catch (error) {
      console.error('Failed to save honeypot interaction to database:', error);
      throw error;
    }
  },

  // ============ DATABASE RETRIEVAL ENDPOINTS ============

  /**
   * Get persisted devices from database
   */
  async getPersistedDevices(limit = 100) {
    try {
      const response = await fetch(`${API_BASE_URL}/db/devices?limit=${limit}`, defaultOptions);
      return handleResponse(response);
    } catch (error) {
      console.error('Failed to fetch persisted devices:', error);
      throw error;
    }
  },

  /**
   * Get persisted alerts from database
   */
  async getPersistedAlerts(limit = 100) {
    try {
      const response = await fetch(`${API_BASE_URL}/db/alerts?limit=${limit}`, defaultOptions);
      return handleResponse(response);
    } catch (error) {
      console.error('Failed to fetch persisted alerts:', error);
      throw error;
    }
  },

  /**
   * Get persisted traffic logs from database
   */
  async getPersistedTraffic(limit = 100) {
    try {
      const response = await fetch(`${API_BASE_URL}/db/traffic?limit=${limit}`, defaultOptions);
      return handleResponse(response);
    } catch (error) {
      console.error('Failed to fetch persisted traffic logs:', error);
      throw error;
    }
  },

  /**
   * Get persisted honeypot interactions from database
   */
  async getPersistedHoneypotInteractions(limit = 100) {
    try {
      const response = await fetch(`${API_BASE_URL}/db/honeypot-interactions?limit=${limit}`, defaultOptions);
      return handleResponse(response);
    } catch (error) {
      console.error('Failed to fetch persisted honeypot interactions:', error);
      throw error;
    }
  },

  /**
   * Get database status (connection info)
   */
  async getDatabaseStatus() {
    try {
      const response = await fetch(`${API_BASE_URL}/db/status`, defaultOptions);
      return handleResponse(response);
    } catch (error) {
      console.error('Failed to fetch database status:', error);
      throw error;
    }
  },

  /**
   * Get comprehensive backend status (metrics, agents, threats)
   */
  async getBackendStatus() {
    try {
      const response = await fetch(`${API_BASE_URL}/backend/status`, defaultOptions);
      return handleResponse(response);
    } catch (error) {
      console.error('Failed to fetch backend status:', error);
      throw error;
    }
  },

  /**
   * Get API health check
   */
  async healthCheck() {
    try {
      const response = await fetch(`${API_BASE_URL}/`, defaultOptions);
      return handleResponse(response);
    } catch (error) {
      console.error('Health check failed:', error);
      throw error;
    }
  },
};

export default API;
