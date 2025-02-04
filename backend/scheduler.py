# backend/scheduler.py
import time
import socket
import logging
import requests
from config import Config
from app import app, db
from models import Domain, ManagedIP

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

def check_health(ip, port, sample_interval=5, total_duration=60, threshold=1000):
    """
    Perform a TCP health check on ip:port by taking multiple samples.
    Returns True if all connection attempts succeed and average latency <= threshold,
    otherwise returns False.
    """
    samples = total_duration // sample_interval
    latencies = []
    for i in range(samples):
        try:
            start = time.perf_counter()
            sock = socket.create_connection((ip, port), timeout=Config.HEALTH_CHECK_TIMEOUT)
            sock.close()
            end = time.perf_counter()
            latency_ms = (end - start) * 1000
            latencies.append(latency_ms)
            logging.info(f"{ip}:{port} sample {i+1}/{samples} latency: {latency_ms:.2f} ms")
        except Exception as e:
            logging.error(f"Connection failed for {ip}:{port} at sample {i+1}/{samples}: {e}")
            return False
        time.sleep(sample_interval)
    avg_latency = sum(latencies) / len(latencies)
    logging.info(f"Average latency for {ip}:{port}: {avg_latency:.2f} ms")
    if avg_latency > threshold:
        logging.error(f"Average latency {avg_latency:.2f} ms exceeds threshold {threshold} ms")
        return False
    return True

def update_dns_for_domain(domain):
    """
    For a given domain, update its DNS records in Cloudflare based on the health of its ManagedIP entries.
    """
    cf_token = domain.cf_api_token
    zone_id = domain.zone_id
    dns_record_name = Config.DNS_RECORD_NAME  # For simplicity; in production, you may store per-domain DNS names.
    
    # Retrieve current DNS records from Cloudflare
    headers = {
        "Authorization": f"Bearer {cf_token}",
        "Content-Type": "application/json"
    }
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records?name={dns_record_name}&type=A"
    response = requests.get(url, headers=headers)
    records = response.json().get("result", [])
    current_records = {rec["content"]: rec["id"] for rec in records}
    
    healthy_ips = []
    for ip_entry in domain.ips:
        ip = ip_entry.ip_address
        port = ip_entry.port
        if check_health(ip, port):
            healthy_ips.append(ip)
        else:
            logging.warning(f"Health check failed for {ip}:{port}")
    
    # Delete records for unhealthy IPs
    for ip, record_id in current_records.items():
        if ip not in healthy_ips:
            del_url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}"
            del_response = requests.delete(del_url, headers=headers)
            if del_response.json().get("success"):
                logging.info(f"Deleted DNS record for {ip}")
            else:
                logging.error(f"Failed to delete DNS record for {ip}: {del_response.text}")
    # Create DNS records for healthy IPs not in Cloudflare
    for ip in healthy_ips:
        if ip not in current_records:
            data = {
                "type": "A",
                "name": dns_record_name,
                "content": ip,
                "ttl": 60,
                "proxied": False
            }
            create_url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records"
            create_response = requests.post(create_url, headers=headers, json=data)
            if create_response.json().get("success"):
                logging.info(f"Created DNS record for {ip}")
            else:
                logging.error(f"Failed to create DNS record for {ip}: {create_response.text}")

def update_all_domains():
    """
    Iterate over all managed domains and update DNS records based on health checks.
    """
    with app.app_context():
        domains = Domain.query.all()
        for domain in domains:
            logging.info(f"Updating DNS records for domain: {domain.domain_name}")
            update_dns_for_domain(domain)

if __name__ == "__main__":
    while True:
        logging.info("Starting health check cycle for all domains...")
        update_all_domains()
        logging.info("Cycle complete. Waiting for next cycle...")
        time.sleep(Config.HEALTH_CHECK_INTERVAL)
