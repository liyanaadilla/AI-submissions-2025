from flask import render_template, jsonify
from flask_socketio import emit
import threading
import time
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Global variables for auto-run control
auto_run_enabled = False
auto_run_thread = None

def auto_run_worker(ai_engine, socketio):
    """Background worker for auto-running AI simulation"""
    global auto_run_enabled
    logger.info(f"Auto-run worker started. Enabled: {auto_run_enabled}")
    
    while auto_run_enabled:
        try:
            logger.info("Executing auto-run step...")
            state = ai_engine.execute_step()
            metrics = ai_engine.calculate_metrics()
            system_overview = ai_engine.calculate_system_overview()
            
            logger.info(f"Step completed. Active tasks: {system_overview['active_tasks']}")
            
            # Emit real-time updates to all connected clients
            socketio.emit('state_update', {
                'state': state,
                'metrics': metrics,
                'system_overview': system_overview
            })
            
            logger.info("State update emitted to clients")
            time.sleep(2)  # Execute step every 2 seconds
            
        except Exception as e:
            logger.error(f"Auto-run error: {e}")
            break
    
    logger.info("Auto-run worker stopped")

def register_routes(app, socketio, ai_engine):
    """Register all Flask routes"""
    global auto_run_enabled, auto_run_thread
    
    @app.route('/')
    def index():
        """Main dashboard page"""
        logger.info("GET / - Serving main dashboard")
        return render_template('index.html')
    
    @app.route('/api/state')
    def get_state():
        """Get current system state"""
        logger.info("GET /api/state called")
        state = ai_engine.get_state_dict()
        metrics = ai_engine.calculate_metrics()
        system_overview = ai_engine.calculate_system_overview()
        
        logger.info(f"State - Active tasks: {system_overview['active_tasks']}, Available workers: {system_overview['available_workers']}")
        
        return jsonify({
            'state': state,
            'metrics': metrics,
            'system_overview': system_overview,
            'is_running': auto_run_enabled
        })
    
    @app.route('/api/step', methods=['POST'])
    def execute_step():
        """Execute a single AI step"""
        logger.info("POST /api/step called")
        state = ai_engine.execute_step()
        metrics = ai_engine.calculate_metrics()
        system_overview = ai_engine.calculate_system_overview()
        
        logger.info(f"Step executed - Active tasks: {system_overview['active_tasks']}")
        
        # Emit update to all clients
        socketio.emit('state_update', {
            'state': state,
            'metrics': metrics,
            'system_overview': system_overview
        })
        
        return jsonify({
            'state': state,
            'metrics': metrics,
            'system_overview': system_overview
        })
    
    @app.route('/api/toggle-auto-run', methods=['POST'])
    def toggle_auto_run():
        """Toggle automatic execution"""
        global auto_run_enabled, auto_run_thread
        
        logger.info(f"POST /api/toggle-auto-run called")
        
        auto_run_enabled = not auto_run_enabled
        
        if auto_run_enabled:
            logger.info("Starting auto-run thread")
            if auto_run_thread is None or not auto_run_thread.is_alive():
                auto_run_thread = threading.Thread(
                    target=auto_run_worker, 
                    args=(ai_engine, socketio),
                    daemon=True
                )
                auto_run_thread.start()
        else:
            logger.info("Stopping auto-run")
        
        return jsonify({
            'is_running': auto_run_enabled,
            'message': 'Auto-run started' if auto_run_enabled else 'Auto-run stopped'
        })
    
    @app.route('/api/reset', methods=['POST'])
    def reset_system():
        """Reset system to initial state"""
        global auto_run_enabled
        
        logger.info("POST /api/reset called")
        
        auto_run_enabled = False
        ai_engine.reset()
        
        state = ai_engine.get_state_dict()
        metrics = ai_engine.calculate_metrics()
        system_overview = ai_engine.calculate_system_overview()
        
        # Emit update to all clients
        socketio.emit('state_update', {
            'state': state,
            'metrics': metrics,
            'system_overview': system_overview
        })
        
        return jsonify({
            'state': state,
            'metrics': metrics,
            'system_overview': system_overview,
            'is_running': False
        })
    
    @app.route('/tasks')
    def tasks():
        """Tasks page"""
        logger.info("GET /tasks - Serving tasks page")
        state = ai_engine.get_state_dict()
        return render_template('tasks.html', state=state)
    
    @app.route('/operations')
    def operations():
        """Operations page"""
        logger.info("GET /operations - Serving operations page")
        state = ai_engine.get_state_dict()
        return render_template('operations.html', state=state)
    
    @app.route('/resources')
    def resources():
        """Resources page"""
        logger.info("GET /resources - Serving resources page")
        state = ai_engine.get_state_dict()
        return render_template('resources.html', state=state)
    
    @socketio.on('connect')
    def handle_connect():
        """Handle client connection"""
        logger.info('Client connected')
        emit('connected', {'data': 'Connected to AI Task Automation System'})
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection"""
        logger.info('Client disconnected')
    
    @socketio.on('message')
    def handle_message(message):
        """Handle incoming Socket.IO messages"""
        logger.info(f'Received message: {message}')
        emit('response', {'data': 'Message received'})
