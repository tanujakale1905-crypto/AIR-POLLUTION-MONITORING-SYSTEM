"""
Routes and REST API Module
Air Pollution Monitoring System
"""
import io
import csv
from datetime import datetime, timezone, timedelta
from flask import Blueprint, render_template, request, jsonify, Response, current_app
from models import db, AirQualityReading
from simulator import simulator

main_bp = Blueprint('main', __name__)
api_bp = Blueprint('api', __name__, url_prefix='/api')

# =======================================================
# FRONTEND TEMPLATE ROUTES
# =======================================================

@main_bp.route('/')
def dashboard():
    """Renders the main real-time Air Pollution Monitoring Dashboard."""
    return render_template('index.html')

@main_bp.route('/history')
def history():
    """Renders the Historical Data Explorer page."""
    return render_template('history.html')

@main_bp.route('/analytics')
def analytics():
    """Renders the Analytics & Statistical Analysis page."""
    return render_template('analytics.html')

@main_bp.route('/api-docs')
def api_docs():
    """Renders the Interactive REST API Documentation page."""
    return render_template('api_docs.html')


# =======================================================
# REST API ENDPOINTS
# =======================================================

@api_bp.route('/readings/latest', methods=['GET'])
def get_latest_reading():
    """
    GET /api/readings/latest
    Returns the single most recent sensor reading with status and alerts.
    """
    latest = AirQualityReading.query.order_by(AirQualityReading.timestamp.desc(), AirQualityReading.id.desc()).first()
    
    if not latest:
        # If no reading exists, generate one automatically
        latest = simulator.record_reading_to_db()

    return jsonify({
        'status': 'success',
        'data': latest.to_dict(),
        'simulator_active': simulator.is_running
    }), 200

@api_bp.route('/readings/history', methods=['GET'])
def get_history():
    """
    GET /api/readings/history
    Query params:
      - start_date (YYYY-MM-DD or ISO)
      - end_date (YYYY-MM-DD or ISO)
      - status ('Good', 'Moderate', 'Poor', or 'all')
      - limit (integer, default 50, max 500)
      - page (integer, default 1)
      - per_page (integer, default 15)
      - sort ('desc' or 'asc', default 'desc')
    """
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    status_filter = request.args.get('status')
    sort_order = request.args.get('sort', 'desc').lower()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 15, type=int)
    limit = request.args.get('limit', type=int)

    # Base query
    query = AirQualityReading.query

    # Date filtering
    if start_date_str:
        try:
            start_date = datetime.fromisoformat(start_date_str.replace('Z', ''))
            query = query.filter(AirQualityReading.timestamp >= start_date)
        except ValueError:
            return jsonify({'status': 'error', 'message': 'Invalid start_date format. Use YYYY-MM-DD or ISO.'}), 400

    if end_date_str:
        try:
            end_date = datetime.fromisoformat(end_date_str.replace('Z', ''))
            # If date only, make it end of the day
            if len(end_date_str) <= 10:
                end_date = end_date.replace(hour=23, minute=59, second=59)
            query = query.filter(AirQualityReading.timestamp <= end_date)
        except ValueError:
            return jsonify({'status': 'error', 'message': 'Invalid end_date format. Use YYYY-MM-DD or ISO.'}), 400

    # Status filtering
    if status_filter and status_filter.lower() != 'all':
        query = query.filter(AirQualityReading.air_quality_status.ilike(status_filter.strip()))

    # Sort
    if sort_order == 'asc':
        query = query.order_by(AirQualityReading.timestamp.asc(), AirQualityReading.id.asc())
    else:
        query = query.order_by(AirQualityReading.timestamp.desc(), AirQualityReading.id.desc())

    # Limit or Pagination
    if limit:
        readings = query.limit(min(limit, 500)).all()
        return jsonify({
            'status': 'success',
            'count': len(readings),
            'data': [r.to_dict() for r in readings]
        }), 200

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'status': 'success',
        'data': [r.to_dict() for r in pagination.items],
        'pagination': {
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total_items': pagination.total,
            'total_pages': pagination.pages,
            'has_prev': pagination.has_prev,
            'has_next': pagination.has_next
        }
    }), 200

@api_bp.route('/readings', methods=['POST'])
def add_reading():
    """
    POST /api/readings
    Allows adding manual or hardware-submitted sensor readings.
    Payload:
    {
        "pm25": 35.5,
        "co2": 620.0,
        "temperature": 26.5,
        "humidity": 55.0,
        "timestamp": "optional ISO string"
    }
    """
    data = request.get_json()
    if not data:
        return jsonify({'status': 'error', 'message': 'Request body must be valid JSON'}), 400

    required_fields = ['pm25', 'co2', 'temperature', 'humidity']
    for field in required_fields:
        if field not in data:
            return jsonify({'status': 'error', 'message': f"Missing required field: '{field}'"}), 400

    try:
        pm25 = float(data['pm25'])
        co2 = float(data['co2'])
        temperature = float(data['temperature'])
        humidity = float(data['humidity'])
    except (ValueError, TypeError):
        return jsonify({'status': 'error', 'message': 'All sensor readings must be numeric numbers.'}), 400

    # Range sanity validations
    if not (0.0 <= pm25 <= 1000.0):
        return jsonify({'status': 'error', 'message': 'PM2.5 value must be between 0 and 1000 µg/m³.'}), 400
    if not (0.0 <= co2 <= 10000.0):
        return jsonify({'status': 'error', 'message': 'CO2 value must be between 0 and 10000 ppm.'}), 400
    if not (-40.0 <= temperature <= 80.0):
        return jsonify({'status': 'error', 'message': 'Temperature must be between -40°C and 80°C.'}), 400
    if not (0.0 <= humidity <= 100.0):
        return jsonify({'status': 'error', 'message': 'Humidity must be between 0% and 100%.'}), 400

    # Timestamp handling
    reading_time = datetime.now(timezone.utc)
    if 'timestamp' in data and data['timestamp']:
        try:
            reading_time = datetime.fromisoformat(data['timestamp'].replace('Z', ''))
        except ValueError:
            return jsonify({'status': 'error', 'message': 'Invalid timestamp format. Use ISO format.'}), 400

    status = AirQualityReading.classify_status(pm25, co2)

    new_reading = AirQualityReading(
        pm25=round(pm25, 2),
        co2=round(co2, 2),
        temperature=round(temperature, 2),
        humidity=round(humidity, 2),
        air_quality_status=status,
        timestamp=reading_time
    )

    db.session.add(new_reading)
    db.session.commit()

    return jsonify({
        'status': 'success',
        'message': 'Sensor reading saved successfully.',
        'data': new_reading.to_dict()
    }), 201

@api_bp.route('/stats', methods=['GET'])
def get_stats():
    """
    GET /api/stats
    Returns aggregated statistical analysis across all historical records:
    - Min, max, average for PM2.5, CO2, temperature, humidity
    - Air quality status counts and percentages
    - Total readings count
    """
    total = AirQualityReading.query.count()
    if total == 0:
        return jsonify({
            'status': 'success',
            'data': {
                'total_readings': 0,
                'pm25': {'min': 0, 'max': 0, 'avg': 0},
                'co2': {'min': 0, 'max': 0, 'avg': 0},
                'temperature': {'min': 0, 'max': 0, 'avg': 0},
                'humidity': {'min': 0, 'max': 0, 'avg': 0},
                'status_distribution': {'Good': 0, 'Moderate': 0, 'Poor': 0}
            }
        }), 200

    from sqlalchemy import func
    stats_query = db.session.query(
        func.min(AirQualityReading.pm25).label('min_pm25'),
        func.max(AirQualityReading.pm25).label('max_pm25'),
        func.avg(AirQualityReading.pm25).label('avg_pm25'),
        func.min(AirQualityReading.co2).label('min_co2'),
        func.max(AirQualityReading.co2).label('max_co2'),
        func.avg(AirQualityReading.co2).label('avg_co2'),
        func.min(AirQualityReading.temperature).label('min_temp'),
        func.max(AirQualityReading.temperature).label('max_temp'),
        func.avg(AirQualityReading.temperature).label('avg_temp'),
        func.min(AirQualityReading.humidity).label('min_hum'),
        func.max(AirQualityReading.humidity).label('max_hum'),
        func.avg(AirQualityReading.humidity).label('avg_hum')
    ).first()

    status_counts = db.session.query(
        AirQualityReading.air_quality_status,
        func.count(AirQualityReading.id)
    ).group_by(AirQualityReading.air_quality_status).all()

    dist = {'Good': 0, 'Moderate': 0, 'Poor': 0}
    for status, count in status_counts:
        dist[status] = count

    return jsonify({
        'status': 'success',
        'data': {
            'total_readings': total,
            'pm25': {
                'min': round(stats_query.min_pm25 or 0, 2),
                'max': round(stats_query.max_pm25 or 0, 2),
                'avg': round(stats_query.avg_pm25 or 0, 2)
            },
            'co2': {
                'min': round(stats_query.min_co2 or 0, 2),
                'max': round(stats_query.max_co2 or 0, 2),
                'avg': round(stats_query.avg_co2 or 0, 2)
            },
            'temperature': {
                'min': round(stats_query.min_temp or 0, 2),
                'max': round(stats_query.max_temp or 0, 2),
                'avg': round(stats_query.avg_temp or 0, 2)
            },
            'humidity': {
                'min': round(stats_query.min_hum or 0, 2),
                'max': round(stats_query.max_hum or 0, 2),
                'avg': round(stats_query.avg_hum or 0, 2)
            },
            'status_distribution': dist
        }
    }), 200

@api_bp.route('/alerts', methods=['GET'])
def get_alerts():
    """
    GET /api/alerts
    Returns recent alerts generated when readings exceeded thresholds.
    """
    # Fetch recent readings with status 'Poor' or 'Moderate'
    elevated_readings = AirQualityReading.query.filter(
        (AirQualityReading.air_quality_status == 'Poor') | 
        (AirQualityReading.air_quality_status == 'Moderate') |
        (AirQualityReading.temperature > 38.0) |
        (AirQualityReading.temperature < 10.0) |
        (AirQualityReading.humidity > 80.0) |
        (AirQualityReading.humidity < 20.0)
    ).order_by(AirQualityReading.timestamp.desc()).limit(20).all()

    alerts_list = []
    for r in elevated_readings:
        for alert in r.get_alerts():
            alerts_list.append({
                'id': r.id,
                'timestamp': r.timestamp.isoformat(),
                'formatted_time': r.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'type': alert['type'],
                'pollutant': alert['pollutant'],
                'message': alert['message'],
                'air_quality_status': r.air_quality_status
            })

    return jsonify({
        'status': 'success',
        'count': len(alerts_list),
        'data': alerts_list
    }), 200

@api_bp.route('/simulate', methods=['POST'])
def trigger_simulation():
    """
    POST /api/simulate
    Generates and records 1 simulated reading immediately.
    Optionally accepts {"spike": true} to generate a high pollution alert reading.
    """
    data = request.get_json(silent=True) or {}
    force_spike = bool(data.get('spike', False))

    reading = simulator.record_reading_to_db(force_spike=force_spike)
    return jsonify({
        'status': 'success',
        'message': 'Simulated reading generated and recorded.',
        'data': reading.to_dict()
    }), 201

@api_bp.route('/simulator/toggle', methods=['POST'])
def toggle_simulator():
    """
    POST /api/simulator/toggle
    Toggles the continuous background sensor generator.
    """
    is_now_running = simulator.toggle()
    return jsonify({
        'status': 'success',
        'is_running': is_now_running,
        'message': 'Simulation running' if is_now_running else 'Simulation paused'
    }), 200

@api_bp.route('/simulator/status', methods=['GET'])
def get_simulator_status():
    """
    GET /api/simulator/status
    Returns current simulator execution state.
    """
    return jsonify({
        'status': 'success',
        'is_running': simulator.is_running,
        'interval_seconds': simulator.interval
    }), 200

@api_bp.route('/seed', methods=['POST'])
def seed_data():
    """
    POST /api/seed
    Seeds sample historical readings (default 40).
    """
    data = request.get_json(silent=True) or {}
    count = data.get('count', 40)
    try:
        count = int(count)
    except ValueError:
        count = 40

    seeded = simulator.seed_historical_data(count=min(count, 200))
    return jsonify({
        'status': 'success',
        'message': f'Successfully seeded {seeded} sample historical records.'
    }), 200

@api_bp.route('/export/csv', methods=['GET'])
def export_csv():
    """
    GET /api/export/csv
    Exports all or filtered sensor records as a downloadable CSV file.
    """
    readings = AirQualityReading.query.order_by(AirQualityReading.timestamp.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'PM2.5 (ug/m3)', 'CO2 (ppm)', 'Temperature (C)', 'Humidity (%)', 'Air Quality Status', 'Timestamp (UTC)'])

    for r in readings:
        writer.writerow([
            r.id,
            r.pm25,
            r.co2,
            r.temperature,
            r.humidity,
            r.air_quality_status,
            r.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        ])

    csv_data = output.getvalue()
    output.close()

    filename = f"air_pollution_readings_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.csv"
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-disposition": f"attachment; filename={filename}"}
    )
