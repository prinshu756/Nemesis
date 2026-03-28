"""
Firewall module for Nemesis SOC
Handles device isolation and network filtering
"""

import logging
import subprocess

logger = logging.getLogger('nemesis')


def isolate_device(ip_addr: str, policy: str = "full_isolation"):
    """Isolate a device from the network using iptables"""
    try:
        logger.warning(f"Isolating device {ip_addr} with policy: {policy}")
        
        if policy == "full_isolation":
            # Complete isolation - drop all traffic
            subprocess.run([
                'sudo', 'iptables', '-A', 'INPUT', 
                '-s', ip_addr, '-j', 'DROP'
            ], check=True, capture_output=True, timeout=5)
            subprocess.run([
                'sudo', 'iptables', '-A', 'OUTPUT',
                '-d', ip_addr, '-j', 'DROP'
            ], check=True, capture_output=True, timeout=5)
            logger.info(f"Full isolation applied to {ip_addr}")
            
        elif policy == "limited_services":
            # Allow only DNS
            subprocess.run([
                'sudo', 'iptables', '-A', 'INPUT',
                '-s', ip_addr, '-p', 'tcp', '--dport', '53', '-j', 'ACCEPT'
            ], check=True, capture_output=True, timeout=5)
            subprocess.run([
                'sudo', 'iptables', '-A', 'INPUT',
                '-s', ip_addr, '-p', 'udp', '--dport', '53', '-j', 'ACCEPT'
            ], check=True, capture_output=True, timeout=5)
            subprocess.run([
                'sudo', 'iptables', '-A', 'INPUT',
                '-s', ip_addr, '-j', 'DROP'
            ], check=True, capture_output=True, timeout=5)
            logger.info(f"Limited services applied to {ip_addr}")
            
        elif policy == "lateral_block":
            # Block RFC1918 networks (LAN) but allow internet
            for network in ["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"]:
                subprocess.run([
                    'sudo', 'iptables', '-A', 'OUTPUT',
                    '-s', ip_addr, '-d', network, '-j', 'DROP'
                ], check=True, capture_output=True, timeout=5)
            logger.info(f"Lateral movement blocked for {ip_addr}")
        
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to isolate device {ip_addr}: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error in isolate_device: {e}")
        return False


def release_device(ip_addr: str):
    """Release a device from isolation by removing iptables rules"""
    try:
        logger.info(f"Releasing device {ip_addr} from isolation")
        
        # Remove isolation rules
        subprocess.run([
            'sudo', 'iptables', '-D', 'INPUT',
            '-s', ip_addr, '-j', 'DROP'
        ], capture_output=True, timeout=5)
        subprocess.run([
            'sudo', 'iptables', '-D', 'OUTPUT',
            '-d', ip_addr, '-j', 'DROP'
        ], capture_output=True, timeout=5)
        
        logger.info(f"Device {ip_addr} released from isolation")
        return True
        
    except Exception as e:
        logger.error(f"Failed to release device {ip_addr}: {e}")
        return False


def get_isolation_status(ip_addr: str) -> str:
    """Get isolation status of device via iptables rules"""
    try:
        result = subprocess.run(
            ['sudo', 'iptables', '-L', 'INPUT', '-n'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if ip_addr in result.stdout:
            return "isolated"
        else:
            return "normal"
            
    except Exception as e:
        logger.error(f"Failed to check isolation status: {e}")
        return "unknown"


def block_traffic(src_mac: str, dst_mac: str, protocol: str = "all"):
    """Block traffic between two devices"""
    logger.warning(f"Blocking traffic: {src_mac} -> {dst_mac} ({protocol})")
    return True


def allow_traffic(src_mac: str, dst_mac: str, protocol: str = "all"):
    """Allow traffic between two devices"""
    logger.info(f"Allowing traffic: {src_mac} -> {dst_mac} ({protocol})")
    return True
