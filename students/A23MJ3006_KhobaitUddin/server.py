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
from dataclasses import asdict

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from controller_enhanced import EnhancedSimulationController
from firebase_integration import get_firebase_manager
from session_manager import get_session_manager

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Global controller, Firebase, and SessionManager instances
ctrl = None
firebase_mgr = None
session_mgr = None


def init_controller():
    """Initialize the enhanced simulation controller with 6-state FSM."""
    global ctrl, session_mgr
    ctrl = EnhancedSimulationController(
        initial_temp=60.0,
        warmup_duration=5.0,
        drift_rate=0.5,
        update_interval_sec=0.5,
    )
    session_mgr = get_session_manager()


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
        
        # Check if we should create a checkpoint
        if session_mgr:
            # should_checkpoint takes: current_tick and optional trigger_event
            trigger_event = "severity_change" if result.get('state_changed') else None
            should_checkpoint = session_mgr.should_checkpoint(
                result.get('tick_count', 0),
                trigger_event
            )
            
            if should_checkpoint:
                decision_stats = ctrl.decision_tracker.get_stats()
                checkpoint = session_mgr.create_checkpoint(
                    current_tick=result.get('tick_count', 0),
                    simulation_time=result.get('simulation_time', 0.0),
                    sensor_data=result,
                    decision_stats=decision_stats,
                    trigger_reason="auto"
                )
                
                # Log checkpoint to Firebase if available
                if firebase_mgr and firebase_mgr.is_enabled():
                    firebase_mgr.log_checkpoint(checkpoint.to_dict())
                
                result['checkpoint_created'] = {
                    'checkpoint_id': checkpoint.checkpoint_id,
                    'reason': 'auto',
                    'tick_count': checkpoint.tick_count,
                }
        
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
    """Reset simulation - clears all decisions and starts fresh."""
    global ctrl
    if ctrl is None:
        return jsonify({'error': 'Controller not initialized'}), 500
    
    try:
        ctrl.reset_simulation()
        return jsonify({
            'status': 'reset successful',
            'message': 'All data cleared - simulation restarted fresh',
            'state': {
                'tick_count': ctrl.tick_count,
                'simulation_time': ctrl.simulation_time,
                'agent_state': 'IDLE',
                'active_dtcs': [],
                'decisions_cleared': True,
            }
        }), 200
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


# ============================================================================
# Session Management Endpoints
# ============================================================================

@app.route('/sessions/current', methods=['GET'])
def get_current_session():
    """Get the current active session with all checkpoints."""
    if session_mgr is None:
        return jsonify({'error': 'Session manager not initialized'}), 500
    
    try:
        status = session_mgr.get_session_status()
        checkpoints = session_mgr.get_all_checkpoints(session_mgr.current_session_id)
        
        return jsonify({
            'session_id': status['session_id'],
            'elapsed_seconds': status['elapsed_seconds'],
            'checkpoint_count': status['checkpoint_count'],
            'checkpoints': checkpoints,
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/sessions/history', methods=['GET'])
def get_sessions_history():
    """Get list of past sessions."""
    if session_mgr is None:
        return jsonify({'error': 'Session manager not initialized'}), 500
    
    try:
        limit = request.args.get('limit', 10, type=int)
        sessions_data = session_mgr.get_session_history(limit)
        
        return jsonify({'sessions': sessions_data}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/sessions/checkpoint', methods=['POST'])
def create_manual_checkpoint():
    """Manually create a checkpoint for the current session."""
    if ctrl is None or session_mgr is None:
        return jsonify({'error': 'Controller or Session manager not initialized'}), 500
    
    try:
        # Get current state
        result = ctrl.get_state()
        decision_stats = ctrl.decision_tracker.get_stats()
        
        # Create checkpoint with correct parameters
        checkpoint = session_mgr.create_checkpoint(
            current_tick=result.get('tick_count', 0),
            simulation_time=result.get('simulation_time', 0.0),
            sensor_data=result,
            decision_stats=decision_stats,
            trigger_reason="manual"
        )
        
        # Log to Firebase if available
        if firebase_mgr and firebase_mgr.is_enabled():
            firebase_mgr.log_checkpoint(checkpoint.to_dict())
        
        return jsonify({
            'status': 'checkpoint created',
            'checkpoint_id': checkpoint.checkpoint_id,
            'session_id': checkpoint.session_id,
            'tick_count': checkpoint.tick_count,
        }), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/sessions/end', methods=['POST'])
def end_session():
    """End current session and start a new one."""
    if ctrl is None or session_mgr is None:
        return jsonify({'error': 'Controller or Session manager not initialized'}), 500
    
    try:
        # Get current state for final checkpoint
        result = ctrl.get_state()
        current_tick = result.get('tick_count', 0)
        
        # End the session
        summary = session_mgr.end_session(
            current_tick=current_tick,
            decision_tracker=ctrl.decision_tracker,
            trigger_reason="manual"
        )
        
        # Save to Firebase if available
        if firebase_mgr and firebase_mgr.is_enabled():
            firebase_mgr.save_session(summary.to_dict())
        
        # Start new session
        session_mgr.start_new_session(current_tick)
        new_status = session_mgr.get_session_status()
        
        return jsonify({
            'status': 'session ended',
            'session_id': summary.session_id,
            'duration_seconds': summary.duration_seconds,
            'checkpoint_count': summary.checkpoint_count,
            'total_decisions': summary.total_decisions,
            'temp_min': summary.temp_min,
            'temp_max': summary.temp_max,
            'temp_avg': summary.temp_avg,
            'new_session_id': new_status['session_id'],
        }), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/sessions/<session_id>/checkpoints', methods=['GET'])
def get_session_checkpoints(session_id):
    """Get all checkpoints for a specific session."""
    if session_mgr is None:
        return jsonify({'error': 'Session manager not initialized'}), 500
    
    try:
        checkpoints = session_mgr.get_all_checkpoints(session_id)
        
        return jsonify({
            'session_id': session_id,
            'checkpoints': checkpoints,
            'checkpoint_count': len(checkpoints),
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/sessions/<session_id>/summary', methods=['GET'])
def get_session_summary(session_id):
    """Get summary for a specific session."""
    if session_mgr is None:
        return jsonify({'error': 'Session manager not initialized'}), 500
    
    try:
        # Find summary in history
        summaries = [s for s in session_mgr.session_history if s.session_id == session_id]
        
        if not summaries:
            return jsonify({'error': 'Session not found'}), 404
        
        return jsonify(summaries[0].to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/sessions/<session_id>/decisions', methods=['GET'])
def get_session_decisions(session_id):
    """Get decisions made during a specific session."""
    if ctrl is None or session_mgr is None:
        return jsonify({'error': 'Controller or Session manager not initialized'}), 500
    
    try:
        # Find summary in history
        summaries = [s for s in session_mgr.session_history if s.session_id == session_id]
        
        if not summaries:
            return jsonify({'error': 'Session not found'}), 404
        
        summary = summaries[0]
        
        # Get all decisions
        all_decisions = ctrl.decision_tracker.get_decisions()
        stats = ctrl.decision_tracker.get_stats()
        
        return jsonify({
            'session_id': session_id,
            'decisions': all_decisions[:50],  # Last 50 decisions
            'decision_count': len(all_decisions),
            'stats_snapshot': stats,
            'session_summary': summary.to_dict(),
        }), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/sessions/compare', methods=['POST'])
def compare_sessions():
    """Compare multiple sessions for patterns."""
    if session_mgr is None:
        return jsonify({'error': 'Session manager not initialized'}), 500
    
    try:
        data = request.json or {}
        session_ids = data.get('session_ids', [])
        
        if not session_ids:
            return jsonify({'error': 'session_ids list is required'}), 400
        
        comparison = session_mgr.compare_sessions(session_ids)
        
        return jsonify(comparison), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/test/scenario', methods=['POST'])
def test_scenario():
    """
    Test scenario with fault injection for demonstration.
    Compares normal engine vs faulty engine side-by-side.
    
    Body: {
        "fault_type": "temperature|pressure|vibration|voltage",
        "magnitude": 50,  # Change magnitude (degrees, PSI, mm/s, or volts)
        "duration_ticks": 100  # How many ticks to apply fault
    }
    """
    if ctrl is None:
        return jsonify({'error': 'Controller not initialized'}), 500
    
    try:
        data = request.json or {}
        fault_type = data.get('fault_type', 'temperature')
        magnitude = float(data.get('magnitude', 30))
        duration_ticks = int(data.get('duration_ticks', 100))
        
        if fault_type not in ['temperature', 'pressure', 'vibration', 'voltage']:
            return jsonify({'error': 'Invalid fault_type. Must be: temperature, pressure, vibration, voltage'}), 400
        
        # Capture baseline (current state before fault)
        baseline_tick = ctrl.tick()  # Get current state
        baseline_metrics = {
            'temperature': baseline_tick.get('temperature', 0),
            'rpm': baseline_tick.get('rpm', 0),
            'oil_pressure_psi': baseline_tick.get('oil_pressure_psi', 0),
            'vibration_mms': baseline_tick.get('vibration_mms', 0),
            'voltage_v': baseline_tick.get('voltage_v', 0),
            'state': baseline_tick.get('state', 'UNKNOWN'),
            'active_dtcs': baseline_tick.get('active_dtcs', []),
            'ml_insights': baseline_tick.get('ml_insights', {}),
            'scheduled_tasks': baseline_tick.get('scheduled_tasks', []),
        }
        baseline_decisions = len(ctrl.decision_tracker.get_decisions())
        
        # Store current fault injection state
        original_fault_enabled = ctrl.fault_injection_enabled
        original_fault_magnitude = ctrl.fault_magnitude
        
        # Apply fault using the set_fault_injection method
        ctrl.set_fault_injection(True, magnitude)
        
        # Run ticks with fault applied and collect responses
        faulty_responses = []
        for i in range(min(duration_ticks, 50)):  # Cap at 50 to avoid long responses
            tick = ctrl.tick()
            faulty_responses.append({
                'tick': i,
                'temperature': tick.get('temperature', 0),
                'rpm': tick.get('rpm', 0),
                'oil_pressure_psi': tick.get('oil_pressure_psi', 0),
                'vibration_mms': tick.get('vibration_mms', 0),
                'voltage_v': tick.get('voltage_v', 0),
                'state': tick.get('state', 'UNKNOWN'),
                'active_dtcs': tick.get('active_dtcs', []),
                'ml_insights': tick.get('ml_insights', {}),
            })
        
        # Capture final faulty state
        final_faulty_tick = faulty_responses[-1] if faulty_responses else {
            'temperature': baseline_metrics['temperature'],
            'oil_pressure_psi': baseline_metrics['oil_pressure_psi'],
            'vibration_mms': baseline_metrics['vibration_mms'],
            'voltage_v': baseline_metrics['voltage_v'],
            'active_dtcs': [],
        }
        faulty_decisions = len(ctrl.decision_tracker.get_decisions()) - baseline_decisions
        
        # Restore original fault injection state
        ctrl.set_fault_injection(original_fault_enabled, original_fault_magnitude)
        
        # Get a few more ticks to show recovery (if fault is removed)
        recovery_responses = []
        ctrl.set_fault_injection(False, 0)
        for i in range(min(20, 20)):  # 20 ticks recovery
            tick = ctrl.tick()
            recovery_responses.append({
                'tick': len(faulty_responses) + i,
                'temperature': tick.get('temperature', 0),
                'state': tick.get('state', 'UNKNOWN'),
                'active_dtcs': tick.get('active_dtcs', []),
            })
        
        # Prepare comparison
        response = {
            'scenario': {
                'fault_type': fault_type,
                'magnitude': magnitude,
                'duration_ticks': duration_ticks,
            },
            'baseline': baseline_metrics,
            'faulty': {
                'peak_values': final_faulty_tick,
                'all_ticks': faulty_responses,
                'new_decisions': faulty_decisions,
                'duration_actual': len(faulty_responses),
            },
            'recovery': {
                'ticks': recovery_responses,
                'duration': len(recovery_responses),
            },
            'comparison': {
                'temperature_change': final_faulty_tick.get('temperature', 0) - baseline_metrics.get('temperature', 0),
                'pressure_change': final_faulty_tick.get('oil_pressure_psi', 0) - baseline_metrics.get('oil_pressure_psi', 0),
                'vibration_change': final_faulty_tick.get('vibration_mms', 0) - baseline_metrics.get('vibration_mms', 0),
                'voltage_change': final_faulty_tick.get('voltage_v', 0) - baseline_metrics.get('voltage_v', 0),
                'dtcs_generated': final_faulty_tick.get('active_dtcs', []),
                'fault_detected_at_tick': next((i for i, r in enumerate(faulty_responses) if r.get('active_dtcs')), -1),
            },
            'success': True,
        }
        
        return jsonify(response), 200
        
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
            'POST /test/scenario': 'Test with fault injection for demonstration (body: {fault_type, magnitude, duration_ticks})',
            'SESSION_ENDPOINTS': {
                'GET /sessions/current': 'Get current active session with checkpoints',
                'GET /sessions/history': 'Get list of past sessions (params: limit)',
                'POST /sessions/checkpoint': 'Manually create checkpoint for current session',
                'POST /sessions/end': 'End current session and start new one',
                'GET /sessions/<id>/checkpoints': 'Get all checkpoints for session',
                'GET /sessions/<id>/summary': 'Get summary for session',
                'GET /sessions/<id>/decisions': 'Get decisions made during session',
                'POST /sessions/compare': 'Compare multiple sessions (body: {session_ids: [...]})',
            },
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
