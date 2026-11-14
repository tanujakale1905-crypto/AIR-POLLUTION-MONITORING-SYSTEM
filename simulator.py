"""
Simulated Sensor Generator Module
Air Pollution Monitoring System

NOTE: This module generates SIMULATED environmental sensor data for demonstration,
testing, and educational purposes. It models realistic physical fluctuations,
diurnal trends, and allows manual injection of pollution events for testing alerts.
"""
import time
import random
import threading
from datetime import datetime, timezone, timedelta
from flask import has_app_context
from models import db, AirQualityReading

class SensorSimulator:
    """
    Manages continuous generation of simulated environmental sensor readings.
    Runs as a thread-safe background service.
    """
    def __init__(self, app=None, interval=3):
        self.app = app
        self.interval = interval
        self.is_running = False
        self._thread = None
        self._lock = threading.Lock()

        # Simulated state memory (for smooth random walk transitions)
        self.current_pm25 = 22.0
        self.current_co2 = 550.0
        self.current_temp = 25.5
        self.current_humidity = 52.0
        self.spike_mode = False

    def init_app(self, app):
        """Initializes with Flask application instance."""
        self.app = app

    def generate_single_reading(self, force_spike=False) -> dict:
        """
        Generates a single realistic simulated reading.
        Applies a bounded random-walk to previous values.
        """
        with self._lock:
            if force_spike or self.spike_mode:
                # Simulated pollution event (e.g., traffic jam, indoor emissions)
                self.current_pm25 = min(150.0, max(65.0, self.current_pm25 + random.uniform(15.0, 30.0)))
                self.current_co2 = min(2200.0, max(1250.0, self.current_co2 + random.uniform(100.0, 250.0)))
                self.current_temp += random.uniform(-0.2, 0.4)
                self.current_humidity += random.uniform(-1.0, 1.0)
                # Reset spike mode after triggering
                self.spike_mode = False
            else:
                # Normal ambient fluctuation (random walk)
                # PM2.5 tends to hover around 15 - 45 µg/m³ with occasional mild spikes
                pm25_delta = random.gauss(0, 2.5)
                # Mean-reverting pull towards 25.0
                pm25_pull = (25.0 - self.current_pm25) * 0.08
                self.current_pm25 = max(5.0, min(140.0, self.current_pm25 + pm25_delta + pm25_pull))

                # CO2 tends to hover around 450 - 900 ppm
                co2_delta = random.gauss(0, 18.0)
                co2_pull = (600.0 - self.current_co2) * 0.05
                self.current_co2 = max(380.0, min(2000.0, self.current_co2 + co2_delta + co2_pull))

                # Temperature fluctuates between 18°C and 34°C
                temp_delta = random.gauss(0, 0.25)
                temp_pull = (26.0 - self.current_temp) * 0.03
                self.current_temp = max(12.0, min(40.0, self.current_temp + temp_delta + temp_pull))

                # Humidity fluctuates between 35% and 75%
                hum_delta = random.gauss(0, 0.6)
                hum_pull = (50.0 - self.current_humidity) * 0.04
                self.current_humidity = max(20.0, min(85.0, self.current_humidity + hum_delta + hum_pull))

            pm25_val = round(self.current_pm25, 2)
            co2_val = round(self.current_co2, 2)
            temp_val = round(self.current_temp, 2)
            hum_val = round(self.current_humidity, 2)

            status = AirQualityReading.classify_status(pm25_val, co2_val)

            return {
                'pm25': pm25_val,
                'co2': co2_val,
                'temperature': temp_val,
                'humidity': hum_val,
                'air_quality_status': status,
                'timestamp': datetime.now(timezone.utc)
            }

    def trigger_spike(self):
        """Flags the next simulation tick to generate an elevated pollution spike."""
        with self._lock:
            self.spike_mode = True

    def record_reading_to_db(self, force_spike=False) -> AirQualityReading:
        """Generates a reading and writes it to the database table."""
        reading_data = self.generate_single_reading(force_spike=force_spike)

        def _save():
            reading = AirQualityReading(
                pm25=reading_data['pm25'],
                co2=reading_data['co2'],
                temperature=reading_data['temperature'],
                humidity=reading_data['humidity'],
                air_quality_status=reading_data['air_quality_status'],
                timestamp=reading_data['timestamp']
            )
            db.session.add(reading)
            db.session.commit()
            # Ensure attributes are refreshed before session potentially closes
            db.session.refresh(reading)
            return reading

        if has_app_context():
            return _save()
        elif self.app:
            with self.app.app_context():
                return _save()
        else:
            raise RuntimeError("Flask app is not registered to the simulator.")

    def _simulation_loop(self):
        """Internal daemon loop for continuous simulation."""
        while self.is_running:
            try:
                self.record_reading_to_db()
            except Exception as e:
                # Log error and continue to keep daemon resilient
                print(f"[Simulator Worker Error]: {e}")
            time.sleep(self.interval)

    def start(self):
        """Starts the background continuous sensor simulation."""
        if self.is_running:
            return False

        self.is_running = True
        self._thread = threading.Thread(target=self._simulation_loop, daemon=True)
        self._thread.start()
        print("[Simulator] Background sensor simulation started.")
        return True

    def stop(self):
        """Stops the background continuous sensor simulation."""
        self.is_running = False
        print("[Simulator] Background sensor simulation paused.")
        return True

    def toggle(self) -> bool:
        """Toggles between running and stopped."""
        if self.is_running:
            self.stop()
            return False
        else:
            self.start()
            return True

    def seed_historical_data(self, count=40):
        """
        Seeds the database with realistic historical readings across the last 24 hours
        if the database is currently empty or upon explicit request.
        """
        def _seed():
            now = datetime.now(timezone.utc)
            readings = []
            
            # Start from 'count' intervals ago
            interval_minutes = max(1, 24 * 60 // max(count, 1))

            sim_pm = 18.0
            sim_co2 = 500.0
            sim_temp = 24.0
            sim_hum = 55.0

            for i in range(count):
                past_time = now - timedelta(minutes=(count - i) * interval_minutes)
                
                # Simulate a temporary rush-hour pollution spike around 70% of the timeline
                is_rush_hour = (0.65 <= (i / count) <= 0.80)
                
                if is_rush_hour:
                    sim_pm = min(120.0, sim_pm + random.uniform(5.0, 12.0))
                    sim_co2 = min(1600.0, sim_co2 + random.uniform(60.0, 150.0))
                else:
                    sim_pm = max(8.0, min(65.0, sim_pm + random.gauss(0, 3.5) + (22.0 - sim_pm) * 0.1))
                    sim_co2 = max(410.0, min(950.0, sim_co2 + random.gauss(0, 25.0) + (550.0 - sim_co2) * 0.08))

                sim_temp = max(18.0, min(35.0, sim_temp + random.gauss(0, 0.4) + (26.0 - sim_temp) * 0.05))
                sim_hum = max(30.0, min(75.0, sim_hum + random.gauss(0, 0.8) + (50.0 - sim_hum) * 0.05))

                pm_val = round(sim_pm, 2)
                co2_val = round(sim_co2, 2)
                status = AirQualityReading.classify_status(pm_val, co2_val)

                reading = AirQualityReading(
                    pm25=pm_val,
                    co2=co2_val,
                    temperature=round(sim_temp, 2),
                    humidity=round(sim_hum, 2),
                    air_quality_status=status,
                    timestamp=past_time
                )
                readings.append(reading)

            db.session.bulk_save_objects(readings)
            db.session.commit()
            print(f"[Simulator] Seeded {len(readings)} realistic historical readings.")
            return len(readings)

        if has_app_context():
            return _seed()
        elif self.app:
            with self.app.app_context():
                return _seed()
        return 0

# Global simulator singleton
simulator = SensorSimulator()
