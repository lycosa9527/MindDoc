import logging
import os
import sys
from datetime import datetime
from typing import Optional

class ColoredFormatter(logging.Formatter):
    """Custom formatter with colored output for different log levels"""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record):
        # Add color to the level name
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"
        
        # Format the message
        formatted = super().format(record)
        
        # Add emoji for different log levels
        emoji_map = {
            'DEBUG': '🔍',
            'INFO': 'ℹ️',
            'WARNING': '⚠️',
            'ERROR': '❌',
            'CRITICAL': '🚨'
        }
        
        emoji = emoji_map.get(levelname, '')
        if emoji:
            formatted = f"{emoji} {formatted}"
        
        return formatted

class DebugLogger:
    """Enhanced logging system for MindDoc application"""
    
    _logger = None
    _initialized = False
    
    @classmethod
    def setup_logger(cls, log_level: str = 'INFO', log_file: str = 'logs/app.log'):
        """Setup the logger with enhanced configuration"""
        
        if cls._initialized:
            return
        
        # Create logs directory
        os.makedirs('logs', exist_ok=True)
        
        # Create logger
        cls._logger = logging.getLogger('MindDoc')
        cls._logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
        
        # Clear existing handlers
        cls._logger.handlers.clear()
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s | %(name)s | %(levelname)s | %(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        simple_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s',
            datefmt='%H:%M:%S'
        )
        
        # File handler (detailed logging)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        
        # Console handler (colored, simple)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, log_level.upper(), logging.INFO))
        console_handler.setFormatter(ColoredFormatter('%(levelname)s | %(message)s'))
        
        # Fix Windows encoding issues
        if hasattr(sys.stdout, 'reconfigure'):
            try:
                sys.stdout.reconfigure(encoding='utf-8')
            except:
                pass
        
        # Add handlers
        cls._logger.addHandler(file_handler)
        cls._logger.addHandler(console_handler)
        
        cls._initialized = True
        
        # Log startup message
        cls.log_info("MindDoc logging system initialized")
        cls.log_info(f"Log file: {os.path.abspath(log_file)}")
        cls.log_info(f"Log level: {log_level.upper()}")
    
    @classmethod
    def log_debug(cls, message: str, context: Optional[dict] = None):
        """Log debug message with optional context"""
        if context:
            message = f"{message} | Context: {context}"
        cls._logger.debug(message)
    
    @classmethod
    def log_info(cls, message: str, context: Optional[dict] = None):
        """Log info message with optional context"""
        if context:
            message = f"{message} | Context: {context}"
        cls._logger.info(message)
    
    @classmethod
    def log_warning(cls, message: str, context: Optional[dict] = None):
        """Log warning message with optional context"""
        if context:
            message = f"{message} | Context: {context}"
        cls._logger.warning(message)
    
    @classmethod
    def log_error(cls, message: str, exception: Optional[Exception] = None, context: Optional[dict] = None):
        """Log error message with optional exception and context"""
        if exception:
            message = f"{message} | Exception: {type(exception).__name__}: {str(exception)}"
        if context:
            message = f"{message} | Context: {context}"
        cls._logger.error(message, exc_info=bool(exception))
    
    @classmethod
    def log_critical(cls, message: str, exception: Optional[Exception] = None, context: Optional[dict] = None):
        """Log critical message with optional exception and context"""
        if exception:
            message = f"{message} | Exception: {type(exception).__name__}: {str(exception)}"
        if context:
            message = f"{message} | Context: {context}"
        cls._logger.critical(message, exc_info=bool(exception))
    
    @classmethod
    def log_performance(cls, operation: str, duration: float, context: Optional[dict] = None):
        """Log performance metrics"""
        message = f"Performance | {operation}: {duration:.3f}s"
        if context:
            message = f"{message} | Context: {context}"
        cls._logger.info(message)
    
    @classmethod
    def log_request(cls, method: str, path: str, status_code: int, duration: float, user_agent: str = None):
        """Log HTTP request details"""
        message = f"Request | {method} {path} | Status: {status_code} | Duration: {duration:.3f}s"
        if user_agent:
            message = f"{message} | User-Agent: {user_agent}"
        cls._logger.info(message)
    
    @classmethod
    def log_document_processing(cls, job_id: str, action: str, details: Optional[dict] = None):
        """Log document processing events"""
        message = f"Document Processing | Job: {job_id} | Action: {action}"
        if details:
            message = f"{message} | Details: {details}"
        cls._logger.info(message)
    
    @classmethod
    def log_api_call(cls, service: str, endpoint: str, status: str, duration: float = None):
        """Log API calls"""
        message = f"API Call | {service} | {endpoint} | Status: {status}"
        if duration:
            message = f"{message} | Duration: {duration:.3f}s"
        cls._logger.info(message)
    
    @classmethod
    def log_security(cls, event: str, details: Optional[dict] = None):
        """Log security-related events"""
        message = f"Security | {event}"
        if details:
            message = f"{message} | Details: {details}"
        cls._logger.warning(message)
    
    @classmethod
    def log_user_action(cls, user_id: str, action: str, details: Optional[dict] = None):
        """Log user actions"""
        message = f"User Action | User: {user_id} | Action: {action}"
        if details:
            message = f"{message} | Details: {details}"
        cls._logger.info(message)
    
    @classmethod
    def log_system_health(cls, component: str, status: str, details: Optional[dict] = None):
        """Log system health information"""
        message = f"System Health | {component} | Status: {status}"
        if details:
            message = f"{message} | Details: {details}"
        cls._logger.info(message)
    
    @classmethod
    def get_log_file_path(cls) -> str:
        """Get the current log file path"""
        return os.path.abspath('logs/app.log')
    
    @classmethod
    def get_recent_logs(cls, lines: int = 50) -> list:
        """Get recent log entries"""
        try:
            with open(cls.get_log_file_path(), 'r') as f:
                return f.readlines()[-lines:]
        except FileNotFoundError:
            return []
    
    @classmethod
    def clear_logs(cls):
        """Clear all log files"""
        try:
            with open(cls.get_log_file_path(), 'w') as f:
                f.write('')
            cls.log_info("📝 Log files cleared")
        except Exception as e:
            cls.log_error("Failed to clear log files", e) 