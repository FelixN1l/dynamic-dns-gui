# backend/models.py
from app import db
from datetime import datetime

class Domain(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    domain_name = db.Column(db.String(128), unique=True, nullable=False)
    zone_id = db.Column(db.String(64), nullable=False)
    cf_api_token = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Relationship to managed IPs
    ips = db.relationship('ManagedIP', backref='domain', cascade="all, delete-orphan", lazy=True)

class ManagedIP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    domain_id = db.Column(db.Integer, db.ForeignKey('domain.id'), nullable=False)
    ip_address = db.Column(db.String(45), nullable=False)  # supports IPv4 and IPv6
    port = db.Column(db.Integer, default=80)  # port to perform health check
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
