# backend/models.py
from app import db
from datetime import datetime

class Domain(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    domain_name = db.Column(db.String(128), unique=True, nullable=False)
    zone_id = db.Column(db.String(64), nullable=False)
    cf_api_token = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class DNSEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    domain_id = db.Column(db.Integer, db.ForeignKey('domain.id'), nullable=False)
    record_type = db.Column(db.String(10), nullable=False)
    name = db.Column(db.String(128), nullable=False)
    content = db.Column(db.String(128), nullable=False)
    ttl = db.Column(db.Integer, default=60)
    proxied = db.Column(db.Boolean, default=False)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Run migrations using Flask-Migrate:
# flask db init
# flask db migrate -m "Initial migration"
# flask db upgrade
