"""
Application Configuration Module
Air Pollution Monitoring System
"""
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    """Base application configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'air-pollution-monitor-secret-key-2026')
    
    # Database Configuration: SQLite is used as the default zero-config database.
    # To use MySQL instead, set the DATABASE_URL environment variable, e.g.:
    # mysql+pymysql://username:password@localhost/air_pollution_db
    DB_PATH = os.path.join(BASE_DIR, 'database', 'air_pollution.db')
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', 
        f'sqlite:///{DB_PATH}'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Air Quality Thresholds (Standard WHO / EPA / NAAQS aligned)
    # PM2.5 in micrograms per cubic meter (µg/m³)
    PM25_GOOD_MAX = 30.0        # 0.0 - 30.0 µg/m³ = Good
    PM25_MODERATE_MAX = 60.0    # 30.1 - 60.0 µg/m³ = Moderate, > 60.0 = Poor

    # CO2 in parts per million (ppm)
    CO2_GOOD_MAX = 800.0        # 400 - 800 ppm = Good / Normal
    CO2_MODERATE_MAX = 1200.0   # 801 - 1200 ppm = Moderate, > 1200 = Poor

    # Environmental Comfort Thresholds
    TEMP_MIN = 10.0             # °C Low alert
    TEMP_MAX = 38.0             # °C High alert
    HUMIDITY_MIN = 20.0         # % Low alert
    HUMIDITY_MAX = 80.0         # % High alert

    # Simulated Sensor Settings
    SIMULATION_INTERVAL = 3     # Interval in seconds for simulated ticks
    SIMULATION_AUTO_START = True # Whether simulator runs automatically in background

    # Pagination
    ITEMS_PER_PAGE = 15

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SIMULATION_AUTO_START = False

config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
