#!/usr/bin/env python3
"""
YSMAI Backend HTTP Server
Wraps SimulationController as REST API for React frontend

Run: python3 server.py
Port: 8000
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from controller_enhanced import EnhancedSimulationController
from firebase_integration import get_firebase_manager

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Global controller and Firebase instances
ctrl = None
firebase_mgr = None


def init_controller():
    """Initialize the enhanced simulation controller with 6-state FSM."""
    global ctrl
    ctrl = EnhancedSimulationController(
        initial_temp=60.0,
        warmup_duration=5.0,
        drift_rate=0.5,
        update_interval_sec=0.5,
    )


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({'status': 'ok', 'service': 'YSMAI Backend'}), 200


@app.route('/tick', methods=['GET'])
def tick():
    """Get next simulation tick."""
    if ctrl is None:
        return jsonify({'error': 'Controller not initialized'}), 500
    
    try:
        result = ctrl.tick()
        
        # Log to Firebase if available
        if firebase_mgr and firebase_mgr.is_enabled():
            firebase_mgr.log_sensor_data(result)
            
            # Log alert if state changed (with DTC codes)
            if result.get('state_changed') and result.get('alert_message'):
                # Extract DTC codes from result
                dtc_codes = [d.get('code') for d in result.get('dtcs', [])]
                firebase_mgr.log_alert({
                    'type': 'state_transition',
                    'severity': result.get('severity', 'INFO'),
                    'message': result.get('alert_message'),
                    'trigger_value': result.get('temperature'),
                    'tick_count': result.get('tick_count'),
                    'dtc_codes': dtc_codes,
                    'state': result.get('state'),
                })
        
        return jsonify(result), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/reset', methods=['POST'])
def reset():
    """Reset simulation."""
    global ctrl
    if ctrl is None:
        return jsonify({'error': 'Controller not initialized'}), 500
    
    try:
        ctrl.reset_simulation()
        return jsonify({'status': 'reset successful'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/fault', methods=['POST'])
def fault():
    """Set fault injection parameters."""
    if ctrl is None:
        return jsonify({'error': 'Controller not initialized'}), 500
    
    try:
        data = request.json or {}
        enabled = data.get('enabled', False)
        magnitude = data.get('magnitude', 0.0)
        
        ctrl.set_fault_injection(enabled, float(magnitude))
        return jsonify({'status': 'fault injection set', 'enabled': enabled, 'magnitude': magnitude}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/audit', methods=['GET'])
def audit():
    """Get audit log from Firebase."""
    if not firebase_mgr or not firebase_mgr.is_enabled():
        return jsonify({'error': 'Firebase not enabled', 'data': []}), 200
    
    try:
        limit = request.args.get('limit', 20, type=int)
        readings = firebase_mgr.get_latest_readings(limit)
        return jsonify({'firebase_enabled': True, 'data': readings}), 200
    except Exception as e:
        return jsonify({'error': str(e), 'data': []}), 500


@app.route('/alerts', methods=['GET'])
def alerts():
    """Get recent alerts from Firebase."""
    if not firebase_mgr or not firebase_mgr.is_enabled():
        return jsonify({'error': 'Firebase not enabled', 'data': []}), 200
    
    try:
        limit = request.args.get('limit', 20, type=int)
        alerts_data = firebase_mgr.get_recent_alerts(limit)
        return jsonify({'firebase_enabled': True, 'data': alerts_data}), 200
    except Exception as e:
        return jsonify({'error': str(e), 'data': []}), 500


@app.route('/decisions', methods=['GET'])
def decisions():
    """Get recent decisions made by the agent."""
    if ctrl is None:
        return jsonify({'error': 'Controller not initialized'}), 500
    
    try:
        limit = request.args.get('limit', 50, type=int)
        decision_type = request.args.get('type')
        category = request.args.get('category')
        severity = request.args.get('severity')
        
        decisions_data = ctrl.get_decisions(
            limit=limit,
            decision_type=decision_type,
            category=category,
            severity=severity,
        )
        
        stats = ctrl.decision_tracker.get_stats()
        
        return jsonify({
            'decisions': decisions_data,
            'stats': stats,
            'filters': {
                'type': decision_type,
                'category': category,
                'severity': severity,
            }
        }), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/report', methods=['GET'])
def report():
    """Generate a comprehensive report of all decisions and system state."""
    if ctrl is None:
        return jsonify({'error': 'Controller not initialized'}), 500
    
    try:
        report_data = ctrl.generate_report()
        return jsonify(report_data), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/report/download', methods=['GET'])
def download_report():
    """Download the report as a JSON file."""
    if ctrl is None:
        return jsonify({'error': 'Controller not initialized'}), 500
    
    try:
        from flask import Response
        from datetime import datetime
        
        report_data = ctrl.generate_report()
        
        # Format as pretty JSON
        json_str = json.dumps(report_data, indent=2, default=str)
        
        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ysmai_report_{timestamp}.json"
        
        return Response(
            json_str,
            mimetype='application/json',
            headers={'Content-Disposition': f'attachment; filename={filename}'}
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/', methods=['GET'])
def root():
    """Root endpoint with API docs."""
    firebase_status = "🟢 Connected" if (firebase_mgr and firebase_mgr.is_enabled()) else "⚪ Disabled (optional)"
    
    return jsonify({
        'service': 'YSMAI HVAC Monitoring Backend',
        'version': '2.0',
        'firebase': firebase_status,
        'endpoints': {
            'GET /health': 'Health check',
            'GET /tick': 'Get next simulation tick',
            'GET /audit': 'Get audit log from Firebase',
            'GET /alerts': 'Get recent alerts from Firebase',
            'GET /decisions': 'Get agent decisions (params: limit, type, category, severity)',
            'GET /report': 'Generate comprehensive report',
            'GET /report/download': 'Download report as JSON file',
            'POST /reset': 'Reset simulation',
            'POST /fault': 'Set fault injection (body: {enabled, magnitude})',
        },
        'docs': 'See students/Frontend/INTEGRATION_GUIDE.md'
    }), 200


if __name__ == '__main__':
    print("=" * 80)
    print("YSMAI Backend HTTP Server")
    print("=" * 80)
    print()
    
    # Initialize Firebase
    print("Initializing Firebase...")
    firebase_mgr = get_firebase_manager()
    if firebase_mgr.is_enabled():
        print("✅ Firebase Firestore connected")
    else:
        print("ℹ️  Firebase disabled (optional - system works without it)")
    print()
    
    # Initialize controller
    print("Initializing controller...")
    init_controller()
    print("✅ Controller initialized")
    print()
    
    # Start server
    print("Starting Flask server on http://localhost:8000")
    print("React frontend will connect to: http://localhost:8000/tick")
    print()
    print("Press Ctrl+C to stop")
    print()
    
    app.run(
        host='localhost',
        port=8000,
        debug=False,
        use_reloader=False,
    )
