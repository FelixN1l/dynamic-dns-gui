# backend/config.py
import os

class Config:
    SECRET_KEY = os.environ.get('APP_SECRET_KEY', 'default-secret-key')
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{os.environ.get('DB_USER')}:{os.environ.get('DB_PASSWORD')}"
        f"@{os.environ.get('DB_HOST', 'db')}/{os.environ.get('DB_NAME')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CF_API_TOKEN = os.environ.get('CF_API_TOKEN')
    CF_ZONE_ID = os.environ.get('CF_ZONE_ID')
    HEALTH_CHECK_INTERVAL = int(os.environ.get('HEALTH_CHECK_INTERVAL', 60))
    HEALTH_CHECK_TIMEOUT = int(os.environ.get('HEALTH_CHECK_TIMEOUT', 3))
