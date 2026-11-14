"""
Database Models Module
Defines the schema for the Air Pollution Monitoring System.
"""
from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def utc_now():
    """Returns timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)

class AirQualityReading(db.Model):
    """
    Model representing an environmental sensor reading.
    Table: air_quality_readings
    """
    __tablename__ = 'air_quality_readings'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pm25 = db.Column(db.Float, nullable=False, comment='PM2.5 concentration in µg/m³')
    co2 = db.Column(db.Float, nullable=False, comment='Carbon Dioxide in ppm')
    temperature = db.Column(db.Float, nullable=False, comment='Ambient temperature in °C')
    humidity = db.Column(db.Float, nullable=False, comment='Relative humidity in %')
    air_quality_status = db.Column(db.String(20), nullable=False, default='Good', comment='Good, Moderate, or Poor')
    timestamp = db.Column(db.DateTime, nullable=False, default=utc_now, index=True)

    @staticmethod
    def classify_status(pm25: float, co2: float) -> str:
        """
        Classifies air quality into 'Good', 'Moderate', or 'Poor'
        based on PM2.5 and CO2 concentrations.
        
        Threshold rules:
          - PM2.5 > 60.0 µg/m³ OR CO2 > 1200.0 ppm  => Poor
          - PM2.5 > 30.0 µg/m³ OR CO2 > 800.0 ppm   => Moderate
          - Otherwise                               => Good
        """
        if pm25 > 60.0 or co2 > 1200.0:
            return "Poor"
        elif pm25 > 30.0 or co2 > 800.0:
            return "Moderate"
        else:
            return "Good"

    def get_alerts(self) -> list:
        """
        Generates contextual alert messages when thresholds are exceeded.
        Returns a list of dicts: [{'type': 'danger'|'warning', 'pollutant': str, 'message': str}]
        """
        alerts = []
        
        # PM2.5 Alerts
        if self.pm25 > 60.0:
            alerts.append({
                'type': 'danger',
                'pollutant': 'PM2.5',
                'message': f'CRITICAL: PM2.5 level is {self.pm25:.1f} µg/m³ (Poor Air Quality! Hazardous fine particulates).'
            })
        elif self.pm25 > 30.0:
            alerts.append({
                'type': 'warning',
                'pollutant': 'PM2.5',
                'message': f'WARNING: PM2.5 level is elevated at {self.pm25:.1f} µg/m³ (Moderate Air Quality).'
            })

        # CO2 Alerts
        if self.co2 > 1200.0:
            alerts.append({
                'type': 'danger',
                'pollutant': 'CO2',
                'message': f'CRITICAL: CO2 concentration reached {self.co2:.0f} ppm (Poor ventilation, high greenhouse concentration).'
            })
        elif self.co2 > 800.0:
            alerts.append({
                'type': 'warning',
                'pollutant': 'CO2',
                'message': f'WARNING: CO2 concentration is {self.co2:.0f} ppm (Moderate level).'
            })

        # Temperature Alerts
        if self.temperature > 38.0:
            alerts.append({
                'type': 'warning',
                'pollutant': 'Temperature',
                'message': f'High Temperature Alert: Ambient temperature reached {self.temperature:.1f} °C.'
            })
        elif self.temperature < 10.0:
            alerts.append({
                'type': 'warning',
                'pollutant': 'Temperature',
                'message': f'Low Temperature Alert: Ambient temperature dropped to {self.temperature:.1f} °C.'
            })

        # Humidity Alerts
        if self.humidity > 80.0:
            alerts.append({
                'type': 'warning',
                'pollutant': 'Humidity',
                'message': f'High Humidity Alert: Relative humidity reached {self.humidity:.1f} %.'
            })
        elif self.humidity < 20.0:
            alerts.append({
                'type': 'warning',
                'pollutant': 'Humidity',
                'message': f'Low Humidity Alert: Relative humidity dropped to {self.humidity:.1f} % (Dry air).'
            })

        return alerts

    def to_dict(self) -> dict:
        """Converts model instance to JSON-serializable dictionary."""
        return {
            'id': self.id,
            'pm25': round(self.pm25, 2),
            'co2': round(self.co2, 2),
            'temperature': round(self.temperature, 2),
            'humidity': round(self.humidity, 2),
            'air_quality_status': self.air_quality_status,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'formatted_time': self.timestamp.strftime('%Y-%m-%d %H:%M:%S') if self.timestamp else '',
            'alerts': self.get_alerts()
        }

    def __repr__(self):
        return f"<AirQualityReading id={self.id} PM2.5={self.pm25} CO2={self.co2} Status={self.air_quality_status}>"
