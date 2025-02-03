# backend/scheduler.py
import time
import socket
import logging
from config import Config

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

# Define a list of servers with their IP addresses and ports to check
SERVER_LIST = [
    {"ip": "192.0.2.10", "port": 80},
    {"ip": "192.0.2.11", "port": 80},
    {"ip": "192.0.2.12", "port": 80},
]

def check_health(ip, port, sample_interval=5, total_duration=60, threshold=1000):
    """
    Perform a TCP health check on ip:port by measuring latency.
    
    - sample_interval: seconds between samples (default: 5 seconds)
    - total_duration: total sampling duration (default: 60 seconds)
    - threshold: maximum average latency in ms allowed (default: 1000 ms)
    
    Returns True if all samples succeed and the average latency is below the threshold.
    Returns False if any sample times out or if the average latency exceeds threshold.
    """
    samples = total_duration // sample_interval
    latencies = []
    for i in range(samples):
        try:
            start_time = time.perf_counter()
            # Create a TCP connection with a timeout
            sock = socket.create_connection((ip, port), timeout=Config.HEALTH_CHECK_TIMEOUT)
            sock.close()
            end_time = time.perf_counter()
            latency_ms = (end_time - start_time) * 1000  # convert seconds to milliseconds
            latencies.append(latency_ms)
            logging.info(f"TCP check for {ip}:{port} sample {i+1}/{samples}: {latency_ms:.2f} ms")
        except Exception as e:
            logging.error(f"TCP check failed for {ip}:{port} at sample {i+1}/{samples}: {e}")
            return False  # immediate failure if a connection attempt fails
        time.sleep(sample_interval)
    avg_latency = sum(latencies) / len(latencies)
    logging.info(f"Average latency for {ip}:{port} over {total_duration} sec: {avg_latency:.2f} ms")
    if avg_latency > threshold:
        logging.error(f"Average latency {avg_latency:.2f} ms exceeds threshold of {threshold} ms")
        return False
    return True

# DNS Manager functions to interact with Cloudflare API
def get_current_dns_records(cf_token, zone_id):
    """Retrieve current A records for the domain from Cloudflare."""
    headers = {
        "Authorization": f"Bearer {cf_token}",
        "Content-Type": "application/json"
    }
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records?name={Config.DNS_RECORD_NAME}&type=A"
    response = requests.get(url, headers=headers)
    records = response.json().get("result", [])
    return {rec["content"]: rec["id"] for rec in records}

def create_dns_record(cf_token, zone_id, ip):
    headers = {
        "Authorization": f"Bearer {cf_token}",
        "Content-Type": "application/json"
    }
    data = {
        "type": "A",
        "name": Config.DNS_RECORD_NAME,
        "content": ip,
        "ttl": 60,
        "proxied": False
    }
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records"
    response = requests.post(url, headers=headers, json=data)
    if response.json().get("success"):
        logging.info(f"Created DNS record for {ip}")
    else:
        logging.error(f"Failed to create DNS record for {ip}: {response.text}")

def delete_dns_record(cf_token, zone_id, record_id, ip):
    headers = {
        "Authorization": f"Bearer {cf_token}",
        "Content-Type": "application/json"
    }
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}"
    response = requests.delete(url, headers=headers)
    if response.json().get("success"):
        logging.info(f"Deleted DNS record for {ip}")
    else:
        logging.error(f"Failed to delete DNS record for {ip}: {response.text}")

def update_dns_records():
    # For demonstration, use the first domain's Cloudflare credentials from config.
    cf_token = Config.CF_API_TOKEN
    zone_id = Config.CF_ZONE_ID
    current_records = get_current_dns_records(cf_token, zone_id)
    healthy_ips = []
    for server in SERVER_LIST:
        ip = server["ip"]
        port = server["port"]
        if check_health(ip, port):
            healthy_ips.append(ip)
        else:
            logging.warning(f"Server {ip}:{port} is unhealthy.")
    # Remove records for IPs that are unhealthy
    for ip, record_id in current_records.items():
        if ip not in healthy_ips:
            delete_dns_record(cf_token, zone_id, record_id, ip)
    # Add records for healthy IPs that are not present in DNS
    for ip in healthy_ips:
        if ip not in current_records:
            create_dns_record(cf_token, zone_id, ip)

if __name__ == "__main__":
    while True:
        logging.info("Starting health check cycle...")
        update_dns_records()
        logging.info("Cycle complete. Waiting for next check...")
        time.sleep(Config.HEALTH_CHECK_INTERVAL)
