import os

def isolate_device(ip):
    os.system(f"iptables -A INPUT -s {ip} -j DROP")
    os.system(f"iptables -A OUTPUT -d {ip} -j DROP")