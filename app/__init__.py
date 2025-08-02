from flask import Flask
from flask_cors import CORS
from app.services.debug_logger import DebugLogger
from app.config import Config

def create_app():
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(Config)
    
    # Setup enhanced logging system
    log_level = app.config.get('LOG_LEVEL', 'INFO')
    DebugLogger.setup_logger(log_level=log_level)
    
    # Validate configuration
    Config.validate_config()
    
    # Initialize CORS
    CORS(app)
    
    # Initialize in-memory state
    app.document_queue = {}
    app.processing_status = {}
    app.analysis_results = {}
    
    # Register blueprints
    from app.routes import upload, analysis, status, api
    app.register_blueprint(upload.bp)
    app.register_blueprint(analysis.bp)
    app.register_blueprint(status.bp)
    app.register_blueprint(api.bp)
    
    # Log successful initialization
    DebugLogger.log_info("Application initialized successfully")
    DebugLogger.log_system_health("Flask App", "Running", {
        "debug_mode": app.debug,
        "log_level": log_level,
        "upload_folder": app.config.get('UPLOAD_FOLDER'),
        "max_content_length": app.config.get('MAX_CONTENT_LENGTH')
    })
    
    return app 