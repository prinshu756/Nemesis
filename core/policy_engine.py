"""
Policy Engine for Nemesis SOC
Handles network policies and enforcement
"""

from typing import Dict, List, Any
from core.logging_config import logger


class PolicyEngine:
    """Manages network policies and enforcement"""
    
    def __init__(self):
        self.policies: Dict[str, Dict[str, Any]] = {}
        self.active_policies: List[str] = []
        self.policy_history: List[Dict[str, Any]] = []
    
    def create_policy(self, policy_name: str, policy_config: Dict[str, Any]) -> bool:
        """Create a new network policy"""
        try:
            self.policies[policy_name] = policy_config
            logger.info(f"Policy created: {policy_name}")
            return True
        except Exception as e:
            logger.error(f"Error creating policy {policy_name}: {e}")
            return False
    
    def activate_policy(self, policy_name: str) -> bool:
        """Activate a policy"""
        try:
            if policy_name in self.policies:
                self.active_policies.append(policy_name)
                logger.info(f"Policy activated: {policy_name}")
                return True
            else:
                logger.warning(f"Policy not found: {policy_name}")
                return False
        except Exception as e:
            logger.error(f"Error activating policy {policy_name}: {e}")
            return False
    
    def deactivate_policy(self, policy_name: str) -> bool:
        """Deactivate a policy"""
        try:
            if policy_name in self.active_policies:
                self.active_policies.remove(policy_name)
                logger.info(f"Policy deactivated: {policy_name}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deactivating policy {policy_name}: {e}")
            return False
    
    def get_policy(self, policy_name: str) -> Dict[str, Any]:
        """Get policy configuration"""
        return self.policies.get(policy_name, {})
    
    def get_active_policies(self) -> List[str]:
        """Get list of active policies"""
        return self.active_policies.copy()
    
    def evaluate_device(self, device_info: Dict[str, Any]) -> List[str]:
        """Evaluate which policies apply to a device"""
        applicable = []
        
        for policy_name, policy in self.policies.items():
            # Evaluate policy conditions
            if self._matches_policy(device_info, policy):
                applicable.append(policy_name)
        
        return applicable
    
    def _matches_policy(self, device_info: Dict[str, Any], policy: Dict[str, Any]) -> bool:
        """Check if device matches policy criteria"""
        # Simple matching logic - can be enhanced
        conditions = policy.get('conditions', {})
        
        for key, expected_value in conditions.items():
            actual_value = device_info.get(key)
            if actual_value != expected_value:
                return False
        
        return True
    
    def record_policy_action(self, policy_name: str, device_mac: str, action: str):
        """Record a policy enforcement action"""
        self.policy_history.append({
            'policy': policy_name,
            'device': device_mac,
            'action': action,
            'timestamp': __import__('datetime').datetime.utcnow().isoformat()
        })
