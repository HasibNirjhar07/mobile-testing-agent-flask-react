from flask import Flask
from flask_cors import CORS
from .core.config import config
from .core.logging import setup_logging
from .extensions import socketio

def create_app():
    setup_logging()
    
    app = Flask(__name__)
    app.config.from_object(config)
    
    # Configure CORS
    CORS(app, resources={r"/*": {"origins": "*"}})
    
    # Initialize SocketIO
    socketio.init_app(app, cors_allowed_origins="*", async_mode='threading')
    
    # Register Blueprints
    from .api.routes import api_bp
    app.register_blueprint(api_bp)
    
    # Initialize Sockets
    from .api.sockets import init_sockets
    init_sockets(socketio)
    
    return app
