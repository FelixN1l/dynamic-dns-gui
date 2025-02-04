# backend/app.py
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from models import Domain, ManagedIP

@app.route('/api/domains', methods=['GET'])
def list_domains():
    domains = Domain.query.all()
    result = []
    for d in domains:
        result.append({
            "id": d.id,
            "domain_name": d.domain_name,
            "zone_id": d.zone_id,
            "ips": [{"id": ip.id, "ip_address": ip.ip_address, "port": ip.port} for ip in d.ips]
        })
    return jsonify(result), 200

@app.route('/api/domains', methods=['POST'])
def add_domain():
    data = request.json
    required = ['domain_name', 'zone_id', 'cf_api_token']
    if not data or not all(field in data for field in required):
        return jsonify({"error": "Missing required fields"}), 400
    domain = Domain(
        domain_name=data['domain_name'],
        zone_id=data['zone_id'],
        cf_api_token=data['cf_api_token']
    )
    db.session.add(domain)
    db.session.commit()
    return jsonify({"message": "Domain added", "id": domain.id}), 201

@app.route('/api/domains/<int:domain_id>', methods=['DELETE'])
def delete_domain(domain_id):
    domain = Domain.query.get(domain_id)
    if not domain:
        return jsonify({"error": "Domain not found"}), 404
    db.session.delete(domain)
    db.session.commit()
    return jsonify({"message": "Domain deleted"}), 200

@app.route('/api/domains/<int:domain_id>/ips', methods=['GET'])
def list_ips(domain_id):
    domain = Domain.query.get(domain_id)
    if not domain:
        return jsonify({"error": "Domain not found"}), 404
    ips = [{"id": ip.id, "ip_address": ip.ip_address, "port": ip.port} for ip in domain.ips]
    return jsonify(ips), 200

@app.route('/api/domains/<int:domain_id>/ips', methods=['POST'])
def add_ip(domain_id):
    domain = Domain.query.get(domain_id)
    if not domain:
        return jsonify({"error": "Domain not found"}), 404
    data = request.json
    if not data or 'ip_address' not in data:
        return jsonify({"error": "Missing IP address"}), 400
    ip = ManagedIP(
        domain_id=domain.id,
        ip_address=data['ip_address'],
        port=data.get('port', 80)
    )
    db.session.add(ip)
    db.session.commit()
    return jsonify({"message": "IP added", "id": ip.id}), 201

@app.route('/api/domains/<int:domain_id>/ips/<int:ip_id>', methods=['DELETE'])
def delete_ip(domain_id, ip_id):
    domain = Domain.query.get(domain_id)
    if not domain:
        return jsonify({"error": "Domain not found"}), 404
    ip = ManagedIP.query.filter_by(domain_id=domain.id, id=ip_id).first()
    if not ip:
        return jsonify({"error": "IP not found"}), 404
    db.session.delete(ip)
    db.session.commit()
    return jsonify({"message": "IP deleted"}), 200

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
