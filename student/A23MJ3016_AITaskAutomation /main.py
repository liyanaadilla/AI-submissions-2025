from flask import Flask
from flask_socketio import SocketIO
from routes import register_routes
from ai_engine import AIEngine

# Initialize Flask app
app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['SECRET_KEY'] = 'ai-automation-secret-key'

# Initialize SocketIO for real-time updates
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize AI engine
ai_engine = AIEngine()

# Now import and register routes
try:
    register_routes(app, socketio, ai_engine)
    print("Routes registered successfully")
except ImportError as e:
    print(f"Failed to import routes: {e}")
    exit(1)
except Exception as e:
    print(f"Failed to register routes: {e}")
    exit(1)

if __name__ == '__main__':
    print("=" * 60)
    print("AI Task Automation System")
    print("=" * 60)
    print("\nStarting server...")
    print("Access the dashboard at: http://localhost:5000")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 60)
    
    # Run the Flask app with SocketIO
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
