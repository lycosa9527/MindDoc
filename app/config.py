import os

class Config:
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))
    UPLOAD_FOLDER = 'app/static/uploads'
    ALLOWED_EXTENSIONS = {'docx'}
    
    # API settings
    DIFY_API_KEY = os.environ.get('DIFY_API_KEY')
    DIFY_API_URL = os.environ.get('DIFY_API_URL', 'https://api.dify.ai/v1')
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    
    # File processing
    MAX_PARAGRAPHS = 1000
    MAX_WORDS_PER_PARAGRAPH = 1000
    PROCESSING_TIMEOUT = 300
    
    @classmethod
    def validate_config(cls):
        """Validate configuration settings"""
        if not cls.SECRET_KEY or cls.SECRET_KEY == 'dev-secret-key-change-in-production':
            print("WARNING: Using default SECRET_KEY. Change this in production!")
        
        if not cls.DIFY_API_KEY:
            print("WARNING: DIFY_API_KEY not set. Dify API features will be disabled.")
        
        return True 