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

# Example model (expand as needed)
class Domain(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    domain_name = db.Column(db.String(128), unique=True, nullable=False)
    zone_id = db.Column(db.String(64), nullable=False)
    cf_api_token = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@app.route('/api/domains', methods=['GET'])
def list_domains():
    domains = Domain.query.all()
    result = [{"id": d.id, "domain_name": d.domain_name, "zone_id": d.zone_id} for d in domains]
    return jsonify(result), 200

@app.route('/api/domains', methods=['POST'])
def add_domain():
    data = request.json
    if not data or 'domain_name' not in data or 'zone_id' not in data or 'cf_api_token' not in data:
        return jsonify({"error": "Missing required fields"}), 400
    domain = Domain(
        domain_name=data['domain_name'],
        zone_id=data['zone_id'],
        cf_api_token=data['cf_api_token']
    )
    db.session.add(domain)
    db.session.commit()
    return jsonify({"message": "Domain added", "id": domain.id}), 201

# Additional API endpoints for DNS pools, server monitoring logs, etc.
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
