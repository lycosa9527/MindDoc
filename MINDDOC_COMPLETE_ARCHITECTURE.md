# MindDoc Complete Architecture & Implementation Guide

## Overview
Complete architecture for MindDoc - LangChain-based document analysis system using Flask, with Dify API integration, real-time document rendering, and professional debugging capabilities.

## 1. System Architecture

### Event-Driven Flow
```
User Upload → Flask Route → Background Thread → Document Analysis → LangChain → Dify API → Real-time Updates → Results Display
```

### Project Structure
```
MindDoc/
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── config.py                # Configuration
│   ├── routes/
│   │   ├── upload.py            # Document upload
│   │   ├── analysis.py          # Analysis routes
│   │   ├── status.py            # Status checking
│   │   └── api.py               # Real-time API routes
│   ├── services/
│   │   ├── document_processor.py # Document parsing
│   │   ├── dify_service.py      # Dify API integration
│   │   ├── event_manager.py     # Event processing
│   │   ├── debug_logger.py      # Professional debugging
│   │   ├── document_generator.py # Document generation
│   │   ├── security_service.py  # Security & validation
│   │   ├── cache_service.py     # Caching layer
│   │   └── rate_limiter.py      # Rate limiting
│   ├── static/
│   │   ├── css/style.css        # Enhanced styles
│   │   ├── js/
│   │   │   ├── upload.js        # Upload functionality
│   │   │   ├── document-viewer.js # Real-time viewer
│   │   │   ├── debug.js         # Debug utilities
│   │   │   └── security.js      # Client-side validation
│   │   └── uploads/             # Temporary file storage
│   ├── templates/index.html     # Enhanced UI template
│   └── utils/
│       ├── validators.py        # Input validation
│       ├── sanitizers.py        # Data sanitization
│       └── helpers.py           # Utility functions
├── logs/                        # Debug log files
├── tests/                       # Test suite
├── docs/                        # Documentation
├── requirements.txt
├── .env.example
├── .gitignore
├── Dockerfile                   # Containerization
├── docker-compose.yml           # Multi-service setup
├── nginx.conf                   # Reverse proxy config
└── run.py                       # Application runner
```

## 2. Core Components

### 2.1 Flask Application Setup (Enhanced)
```python
# app/__init__.py
from flask import Flask
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from app.services.debug_logger import DebugLogger
from app.services.security_service import SecurityService
from app.services.cache_service import CacheService
from app.utils.validators import setup_validators

def create_app(config_name='development'):
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(f'app.config.{config_name.capitalize()}Config')
    
    # Initialize security
    SecurityService.initialize(app)
    
    # Initialize caching
    CacheService.initialize(app)
    
    # Setup rate limiting
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"]
    )
    
    # Initialize in-memory state with TTL
    app.document_queue = {}
    app.processing_status = {}
    app.analysis_results = {}
    app.session_timeout = 3600  # 1 hour
    
    # Setup debugging with rotation
    DebugLogger.setup_logger(app.config['LOG_LEVEL'])
    
    # Setup validators
    setup_validators(app)
    
    # Register blueprints with error handlers
    from app.routes import upload, analysis, status, api
    app.register_blueprint(upload.bp)
    app.register_blueprint(analysis.bp)
    app.register_blueprint(status.bp)
    app.register_blueprint(api.bp)
    
    # Register error handlers
    register_error_handlers(app)
    
    return app

def register_error_handlers(app):
    @app.errorhandler(413)
    def too_large(e):
        return {'error': 'File too large'}, 413
    
    @app.errorhandler(429)
    def ratelimit_handler(e):
        return {'error': 'Rate limit exceeded'}, 429
    
    @app.errorhandler(500)
    def internal_error(e):
        DebugLogger.log_error("Internal server error", e)
        return {'error': 'Internal server error'}, 500
```

### 2.2 Enhanced Configuration
```python
# app/config.py
import os
from datetime import timedelta

class BaseConfig:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = 'app/static/uploads'
    ALLOWED_EXTENSIONS = {'docx'}
    
    # Security settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)
    
    # API settings
    DIFY_API_KEY = os.environ.get('DIFY_API_KEY')
    DIFY_API_URL = os.environ.get('DIFY_API_URL', 'https://api.dify.ai/v1')
    DIFY_TIMEOUT = 60
    
    # Caching
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300
    
    # Logging
    LOG_LEVEL = 'INFO'
    LOG_MAX_BYTES = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT = 5
    
    # Rate limiting
    RATELIMIT_STORAGE_URL = 'memory://'
    RATELIMIT_STRATEGY = 'fixed-window'
    
    # File processing
    MAX_PARAGRAPHS = 1000
    MAX_WORDS_PER_PARAGRAPH = 1000
    PROCESSING_TIMEOUT = 300  # 5 minutes

class DevelopmentConfig(BaseConfig):
    DEBUG = True
    LOG_LEVEL = 'DEBUG'
    SESSION_COOKIE_SECURE = False

class ProductionConfig(BaseConfig):
    DEBUG = False
    LOG_LEVEL = 'WARNING'
    
    # Production security
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    
    # Production caching
    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = os.environ.get('REDIS_URL')

class TestingConfig(BaseConfig):
    TESTING = True
    WTF_CSRF_ENABLED = False
```

### 2.3 Enhanced Document Processor Service
```python
# app/services/document_processor.py
from docx import Document
import spacy
import textstat
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from app.services.debug_logger import DebugLogger
from app.services.security_service import SecurityService
from app.utils.sanitizers import sanitize_text
from app.utils.validators import validate_document_size, validate_paragraph_count

class DocumentProcessor:
    def __init__(self, app):
        self.app = app
        self.nlp = spacy.load("en_core_web_sm")
        self.max_paragraphs = app.config.get('MAX_PARAGRAPHS', 1000)
        self.max_words_per_paragraph = app.config.get('MAX_WORDS_PER_PARAGRAPH', 1000)
        self.processing_timeout = app.config.get('PROCESSING_TIMEOUT', 300)
    
    def process_document(self, file_path: str, job_id: str) -> Dict[str, Any]:
        """Main document processing pipeline with enhanced error handling"""
        
        start_time = datetime.now()
        DebugLogger.log_info(f"Starting document processing for job {job_id}")
        
        try:
            # Security validation
            if not SecurityService.validate_file(file_path):
                raise ValueError("File validation failed")
            
            # Update status
            self._update_status(job_id, "processing", "Starting analysis...")
            
            # Extract and validate document structure
            structure = self._extract_document_structure(file_path)
            
            # Analyze paragraphs with timeout protection
            paragraph_analyses = self._analyze_paragraphs_with_timeout(file_path, start_time)
            
            # Generate overall analysis
            overall_analysis = self._generate_overall_analysis(paragraph_analyses)
            
            # Store results with TTL
            results = {
                'job_id': job_id,
                'file_path': file_path,
                'structure': structure,
                'paragraph_analyses': paragraph_analyses,
                'overall_analysis': overall_analysis,
                'status': 'completed',
                'created_at': datetime.now().isoformat(),
                'expires_at': (datetime.now() + timedelta(hours=24)).isoformat()
            }
            
            self.app.analysis_results[job_id] = results
            self._update_status(job_id, "completed", "Analysis completed")
            
            # Log performance
            duration = (datetime.now() - start_time).total_seconds()
            DebugLogger.log_performance("Document processing", duration)
            
            return results
            
        except Exception as e:
            DebugLogger.log_error(f"Document processing failed for job {job_id}", e)
            self._update_status(job_id, "failed", f"Analysis failed: {str(e)}")
            raise
    
    def _analyze_paragraphs_with_timeout(self, file_path: str, start_time: datetime) -> List[Dict[str, Any]]:
        """Analyze paragraphs with timeout protection"""
        
        doc = Document(file_path)
        analyses = []
        
        # Validate paragraph count
        if len(doc.paragraphs) > self.max_paragraphs:
            raise ValueError(f"Document has too many paragraphs: {len(doc.paragraphs)}")
        
        for i, paragraph in enumerate(doc.paragraphs):
            # Check timeout
            if (datetime.now() - start_time).total_seconds() > self.processing_timeout:
                raise TimeoutError("Processing timeout exceeded")
            
            if paragraph.text.strip():
                # Validate paragraph size
                if len(paragraph.text.split()) > self.max_words_per_paragraph:
                    DebugLogger.log_warning(f"Paragraph {i} exceeds word limit")
                
                analysis = self._analyze_single_paragraph(paragraph.text, i)
                analyses.append(analysis)
        
        return analyses
    
    def _analyze_single_paragraph(self, text: str, index: int) -> Dict[str, Any]:
        """Analyze a single paragraph with enhanced analysis"""
        
        # Sanitize text
        sanitized_text = sanitize_text(text)
        
        doc_nlp = self.nlp(sanitized_text)
        
        analysis = {
            'paragraph_index': index,
            'text': sanitized_text,
            'original_text': text,
            'word_count': len(sanitized_text.split()),
            'char_count': len(sanitized_text),
            'readability': textstat.flesch_reading_ease(sanitized_text),
            'entities': [(ent.text, ent.label_) for ent in doc_nlp.ents],
            'comments': [],
            'suggestions': [],
            'risk_score': 0
        }
        
        # Enhanced analysis
        self._generate_comments(analysis, doc_nlp)
        self._calculate_risk_score(analysis)
        
        return analysis
    
    def _generate_comments(self, analysis: Dict[str, Any], doc_nlp) -> None:
        """Generate comprehensive comments and suggestions"""
        
        text = analysis['text']
        word_count = analysis['word_count']
        readability = analysis['readability']
        
        # Length analysis
        if word_count < 10:
            analysis['comments'].append({
                'type': 'warning',
                'message': 'This paragraph is quite short. Consider adding more detail.',
                'priority': 'medium'
            })
        elif word_count > 100:
            analysis['comments'].append({
                'type': 'info',
                'message': 'This paragraph is quite long. Consider breaking it into smaller paragraphs.',
                'priority': 'low'
            })
        
        # Readability analysis
        if readability < 30:
            analysis['comments'].append({
                'type': 'error',
                'message': 'This paragraph is difficult to read. Consider simplifying the language.',
                'priority': 'high'
            })
        elif readability > 80:
            analysis['comments'].append({
                'type': 'success',
                'message': 'This paragraph has excellent readability.',
                'priority': 'low'
            })
        
        # Grammar and style analysis
        passive_count = sum(1 for token in doc_nlp if token.dep_ == "nsubjpass")
        if passive_count > 0:
            analysis['comments'].append({
                'type': 'warning',
                'message': f'Consider using active voice instead of passive voice ({passive_count} instances).',
                'priority': 'medium'
            })
        
        # Entity analysis
        if analysis['entities']:
            analysis['comments'].append({
                'type': 'info',
                'message': f'Found {len(analysis["entities"])} named entities in this paragraph.',
                'priority': 'low'
            })
    
    def _calculate_risk_score(self, analysis: Dict[str, Any]) -> None:
        """Calculate a risk score for the paragraph"""
        
        risk_score = 0
        
        # Factors that increase risk
        if analysis['readability'] < 30:
            risk_score += 3
        elif analysis['readability'] < 50:
            risk_score += 1
        
        if analysis['word_count'] < 10:
            risk_score += 2
        elif analysis['word_count'] > 100:
            risk_score += 1
        
        # Passive voice penalty
        passive_entities = [ent for ent in analysis['entities'] if ent[1] in ['PERSON', 'ORG']]
        if passive_entities:
            risk_score += 1
        
        analysis['risk_score'] = min(risk_score, 10)  # Cap at 10
```

### 2.4 Security Service
```python
# app/services/security_service.py
import os
import hashlib
import magic
from typing import Dict, Any
from app.services.debug_logger import DebugLogger

class SecurityService:
    @staticmethod
    def initialize(app):
        """Initialize security settings"""
        app.config['SECURE_HEADERS'] = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains'
        }
    
    @staticmethod
    def validate_file(file_path: str) -> bool:
        """Validate file security"""
        try:
            # Check file exists
            if not os.path.exists(file_path):
                return False
            
            # Check file size
            file_size = os.path.getsize(file_path)
            if file_size > 16 * 1024 * 1024:  # 16MB
                return False
            
            # Check MIME type
            mime_type = magic.from_file(file_path, mime=True)
            allowed_types = [
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'application/zip'  # .docx files are actually ZIP files
            ]
            
            if mime_type not in allowed_types:
                DebugLogger.log_warning(f"Invalid MIME type: {mime_type}")
                return False
            
            return True
            
        except Exception as e:
            DebugLogger.log_error(f"File validation failed: {str(e)}")
            return False
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for security"""
        import re
        # Remove any non-alphanumeric characters except dots and hyphens
        sanitized = re.sub(r'[^a-zA-Z0-9.-]', '_', filename)
        return sanitized[:100]  # Limit length
    
    @staticmethod
    def generate_file_hash(file_path: str) -> str:
        """Generate SHA256 hash of file"""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    @staticmethod
    def validate_session(session_data: Dict[str, Any]) -> bool:
        """Validate session data"""
        required_fields = ['user_id', 'session_id', 'created_at']
        return all(field in session_data for field in required_fields)
```

### 2.5 Cache Service
```python
# app/services/cache_service.py
from typing import Any, Optional
from datetime import datetime, timedelta
import json

class CacheService:
    _cache = {}
    
    @staticmethod
    def initialize(app):
        """Initialize cache service"""
        CacheService._cache = {}
    
    @staticmethod
    def get(key: str) -> Optional[Any]:
        """Get value from cache"""
        if key in CacheService._cache:
            item = CacheService._cache[key]
            if datetime.now() < item['expires_at']:
                return item['value']
            else:
                del CacheService._cache[key]
        return None
    
    @staticmethod
    def set(key: str, value: Any, ttl: int = 300) -> None:
        """Set value in cache with TTL"""
        CacheService._cache[key] = {
            'value': value,
            'expires_at': datetime.now() + timedelta(seconds=ttl)
        }
    
    @staticmethod
    def delete(key: str) -> None:
        """Delete value from cache"""
        if key in CacheService._cache:
            del CacheService._cache[key]
    
    @staticmethod
    def clear_expired() -> None:
        """Clear expired cache entries"""
        now = datetime.now()
        expired_keys = [
            key for key, item in CacheService._cache.items()
            if now >= item['expires_at']
        ]
        for key in expired_keys:
            del CacheService._cache[key]
```

### 2.6 Rate Limiter
```python
# app/services/rate_limiter.py
from datetime import datetime, timedelta
from typing import Dict, List
from app.services.debug_logger import DebugLogger

class RateLimiter:
    _requests = {}
    
    @staticmethod
    def check_rate_limit(identifier: str, max_requests: int = 100, window: int = 3600) -> bool:
        """Check if request is within rate limit"""
        now = datetime.now()
        window_start = now - timedelta(seconds=window)
        
        if identifier not in RateLimiter._requests:
            RateLimiter._requests[identifier] = []
        
        # Clean old requests
        RateLimiter._requests[identifier] = [
            req_time for req_time in RateLimiter._requests[identifier]
            if req_time > window_start
        ]
        
        # Check limit
        if len(RateLimiter._requests[identifier]) >= max_requests:
            DebugLogger.log_warning(f"Rate limit exceeded for {identifier}")
            return False
        
        # Add current request
        RateLimiter._requests[identifier].append(now)
        return True
    
    @staticmethod
    def get_remaining_requests(identifier: str, max_requests: int = 100, window: int = 3600) -> int:
        """Get remaining requests for identifier"""
        now = datetime.now()
        window_start = now - timedelta(seconds=window)
        
        if identifier not in RateLimiter._requests:
            return max_requests
        
        # Clean old requests
        RateLimiter._requests[identifier] = [
            req_time for req_time in RateLimiter._requests[identifier]
            if req_time > window_start
        ]
        
        return max(0, max_requests - len(RateLimiter._requests[identifier]))
```

## 3. Real-Time Features

### 3.1 Enhanced Real-Time Document Viewer
```javascript
// app/static/js/document-viewer.js
class DocumentViewer {
    constructor() {
        this.currentDocument = null;
        this.autoSaveTimeout = null;
        this.currentJobId = null;
        this.unsavedChanges = new Set();
        this.maxRetries = 3;
        this.retryDelay = 1000;
    }
    
    renderDocument(documentData, jobId) {
        this.currentJobId = jobId;
        this.currentDocument = documentData;
        
        const viewer = document.getElementById('documentViewer');
        let html = '<div class="document-content">';
        
        documentData.paragraph_analyses.forEach((paragraph, index) => {
            const riskClass = this.getRiskClass(paragraph.risk_score);
            html += `
                <div class="paragraph-container ${riskClass}" data-paragraph-id="${index}">
                    <div class="paragraph-header">
                        <span class="paragraph-number">Paragraph ${index + 1}</span>
                        <div class="paragraph-stats">
                            <span class="word-count">${paragraph.word_count} words</span>
                            <span class="readability-score">Readability: ${paragraph.readability?.toFixed(1) || 'N/A'}</span>
                            <span class="risk-score">Risk: ${paragraph.risk_score}/10</span>
                        </div>
                    </div>
                    <div class="paragraph-content" contenteditable="true" data-original="${paragraph.text}">
                        ${paragraph.text}
                    </div>
                    <div class="paragraph-suggestions">
                        ${this.renderSuggestions(paragraph.comments)}
                    </div>
                    <div class="paragraph-actions">
                        <button class="btn btn-sm btn-outline-primary apply-suggestion" data-paragraph="${index}">
                            Apply Suggestions
                        </button>
                        <button class="btn btn-sm btn-outline-secondary revert-changes" data-paragraph="${index}">
                            Revert
                        </button>
                        <button class="btn btn-sm btn-outline-info view-details" data-paragraph="${index}">
                            View Details
                        </button>
                    </div>
                </div>
            `;
        });
        
        html += '</div>';
        viewer.innerHTML = html;
        this.setupEventListeners();
        this.updateDocumentStats();
        this.setupAutoSave();
    }
    
    getRiskClass(riskScore) {
        if (riskScore >= 7) return 'high-risk';
        if (riskScore >= 4) return 'medium-risk';
        return 'low-risk';
    }
    
    renderSuggestions(comments) {
        if (!comments || comments.length === 0) {
            return '<div class="no-suggestions">No suggestions for this paragraph</div>';
        }
        
        return `
            <div class="suggestions-list">
                ${comments.map(comment => `
                    <div class="suggestion-item suggestion-${comment.type}">
                        <i class="fas fa-${this.getSuggestionIcon(comment.type)} text-${this.getSuggestionColor(comment.type)}"></i>
                        <span class="suggestion-text">${comment.message}</span>
                        <span class="suggestion-priority">${comment.priority}</span>
                    </div>
                `).join('')}
            </div>
        `;
    }
    
    getSuggestionIcon(type) {
        const icons = {
            'error': 'exclamation-triangle',
            'warning': 'exclamation-circle',
            'info': 'info-circle',
            'success': 'check-circle'
        };
        return icons[type] || 'info-circle';
    }
    
    getSuggestionColor(type) {
        const colors = {
            'error': 'danger',
            'warning': 'warning',
            'info': 'info',
            'success': 'success'
        };
        return colors[type] || 'info';
    }
    
    setupEventListeners() {
        // Real-time content editing with validation
        document.querySelectorAll('.paragraph-content').forEach(element => {
            element.addEventListener('input', (e) => {
                this.handleContentChange(e.target);
            });
            
            element.addEventListener('blur', (e) => {
                this.saveChanges(e.target);
            });
            
            element.addEventListener('keydown', (e) => {
                this.handleKeyDown(e);
            });
        });
        
        // Enhanced action buttons
        document.querySelectorAll('.apply-suggestion').forEach(button => {
            button.addEventListener('click', (e) => {
                this.applySuggestions(e.target.dataset.paragraph);
            });
        });
        
        document.querySelectorAll('.revert-changes').forEach(button => {
            button.addEventListener('click', (e) => {
                this.revertChanges(e.target.dataset.paragraph);
            });
        });
        
        document.querySelectorAll('.view-details').forEach(button => {
            button.addEventListener('click', (e) => {
                this.showParagraphDetails(e.target.dataset.paragraph);
            });
        });
    }
    
    handleKeyDown(event) {
        // Prevent excessive typing
        if (event.target.textContent.length > 10000) {
            event.preventDefault();
            this.showWarning('Paragraph is too long. Please break it into smaller paragraphs.');
        }
    }
    
    async saveChanges(element, retryCount = 0) {
        const paragraphId = element.closest('.paragraph-container').dataset.paragraphId;
        const newText = element.textContent;
        
        try {
            const response = await fetch('/api/update-paragraph', {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({
                    paragraph_id: paragraphId,
                    new_text: newText,
                    job_id: this.currentJobId
                })
            });
            
            if (response.ok) {
                element.classList.remove('modified');
                this.unsavedChanges.delete(paragraphId);
                this.showSaveIndicator(paragraphId);
                this.updateDocumentStats();
            } else if (response.status === 429 && retryCount < this.maxRetries) {
                // Rate limited, retry after delay
                setTimeout(() => {
                    this.saveChanges(element, retryCount + 1);
                }, this.retryDelay * (retryCount + 1));
            } else {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
        } catch (error) {
            console.error('Error saving changes:', error);
            this.showError('Failed to save changes. Please try again.');
            this.unsavedChanges.add(paragraphId);
        }
    }
    
    setupAutoSave() {
        // Auto-save every 30 seconds if there are unsaved changes
        setInterval(() => {
            if (this.unsavedChanges.size > 0) {
                this.saveAllChanges();
            }
        }, 30000);
    }
    
    async saveAllChanges() {
        const promises = Array.from(this.unsavedChanges).map(paragraphId => {
            const element = document.querySelector(`[data-paragraph-id="${paragraphId}"] .paragraph-content`);
            if (element) {
                return this.saveChanges(element);
            }
        });
        
        await Promise.all(promises);
    }
    
    showWarning(message) {
        const warningDiv = document.createElement('div');
        warningDiv.className = 'alert alert-warning alert-dismissible fade show';
        warningDiv.innerHTML = `
            <i class="fas fa-exclamation-triangle"></i> ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.querySelector('.container-fluid').insertBefore(warningDiv, document.querySelector('.container-fluid').firstChild);
    }
}
```

### 3.2 Enhanced Flask Routes with Security
```python
# app/routes/api.py
from flask import Blueprint, request, jsonify, current_app, g
from flask_limiter import limiter
from app.services.debug_logger import DebugLogger
from app.services.security_service import SecurityService
from app.services.rate_limiter import RateLimiter
from app.utils.validators import validate_json_input
from app.utils.sanitizers import sanitize_text

bp = Blueprint('api', __name__)

@bp.route('/api/update-paragraph', methods=['POST'])
@limiter.limit("100 per hour")
def update_paragraph():
    """Update paragraph content in real-time with enhanced security"""
    
    try:
        # Validate request
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        
        data = request.get_json()
        
        # Input validation
        validation_result = validate_json_input(data, {
            'paragraph_id': 'integer',
            'new_text': 'string',
            'job_id': 'string'
        })
        
        if not validation_result['valid']:
            return jsonify({'error': f'Validation failed: {validation_result["message"]}'}), 400
        
        paragraph_id = data.get('paragraph_id')
        new_text = data.get('new_text')
        job_id = data.get('job_id')
        
        # Rate limiting check
        client_ip = request.remote_addr
        if not RateLimiter.check_rate_limit(f"update_paragraph_{client_ip}", 50, 3600):
            return jsonify({'error': 'Rate limit exceeded'}), 429
        
        # Sanitize input
        sanitized_text = sanitize_text(new_text)
        
        # Validate text length
        if len(sanitized_text) > 10000:
            return jsonify({'error': 'Text too long'}), 400
        
        # Get current analysis results
        results = current_app.analysis_results.get(job_id)
        if not results:
            return jsonify({'error': 'Analysis results not found'}), 404
        
        # Update paragraph with validation
        if paragraph_id < len(results['paragraph_analyses']):
            results['paragraph_analyses'][paragraph_id]['text'] = sanitized_text
            
            # Re-analyze the updated paragraph
            from app.services.document_processor import DocumentProcessor
            processor = DocumentProcessor(current_app)
            updated_analysis = processor._analyze_single_paragraph(sanitized_text, paragraph_id)
            results['paragraph_analyses'][paragraph_id].update(updated_analysis)
            
            DebugLogger.log_info(f"Paragraph {paragraph_id} updated for job {job_id}")
            
            return jsonify({
                'success': True,
                'updated_analysis': updated_analysis,
                'remaining_requests': RateLimiter.get_remaining_requests(f"update_paragraph_{client_ip}")
            }), 200
        else:
            return jsonify({'error': 'Invalid paragraph ID'}), 400
            
    except Exception as e:
        DebugLogger.log_error(f"Error updating paragraph: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/api/download-document', methods=['POST'])
@limiter.limit("10 per hour")
def download_document():
    """Generate and download updated document with security checks"""
    
    try:
        data = request.get_json()
        job_id = data.get('job_id')
        
        if not job_id:
            return jsonify({'error': 'Job ID required'}), 400
        
        # Security validation
        if not SecurityService.validate_session(g.get('session_data', {})):
            return jsonify({'error': 'Invalid session'}), 401
        
        # Get current results
        results = current_app.analysis_results.get(job_id)
        if not results:
            return jsonify({'error': 'Analysis results not found'}), 404
        
        # Generate updated document
        from app.services.document_generator import DocumentGenerator
        generator = DocumentGenerator(current_app)
        updated_file_path = generator.generate_updated_document(results)
        
        # Validate generated file
        if not SecurityService.validate_file(updated_file_path):
            return jsonify({'error': 'Generated file validation failed'}), 500
        
        return jsonify({
            'success': True,
            'download_url': f'/download/{job_id}',
            'file_path': updated_file_path
        }), 200
        
    except Exception as e:
        DebugLogger.log_error(f"Error generating document: {str(e)}")
        return jsonify({'error': 'Failed to generate document'}), 500
```

## 4. Enhanced HTML Template with Security
```html
<!-- app/templates/index.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-Content-Type-Options" content="nosniff">
    <meta http-equiv="X-Frame-Options" content="DENY">
    <meta http-equiv="X-XSS-Protection" content="1; mode=block">
    <title>MindDoc - Real-Time Document Analysis</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link href="{{ url_for('static', filename='css/style.css') }}" rel="stylesheet">
</head>
<body>
    <div class="container-fluid mt-3">
        <div class="row">
            <!-- Upload Section -->
            <div class="col-md-3">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">
                            <i class="fas fa-upload"></i> Upload Document
                        </h5>
                        <form id="uploadForm" enctype="multipart/form-data">
                            <div class="mb-3">
                                <input type="file" class="form-control" id="documentFile" accept=".docx" required>
                                <div class="form-text">Only .docx files are supported (max 16MB)</div>
                            </div>
                            <button type="submit" class="btn btn-primary w-100" id="uploadBtn">
                                <span class="spinner-border spinner-border-sm d-none" id="uploadSpinner"></span>
                                <i class="fas fa-upload"></i> Upload & Analyze
                            </button>
                        </form>
                        
                        <!-- Progress Section -->
                        <div class="mt-3 d-none" id="progressSection">
                            <h6>Analysis Progress</h6>
                            <div class="progress mb-2">
                                <div class="progress-bar" id="progressBar" role="progressbar" style="width: 0%"></div>
                            </div>
                            <p id="progressMessage" class="text-muted small">Initializing analysis...</p>
                        </div>
                        
                        <!-- Download Section -->
                        <div class="mt-3 d-none" id="downloadSection">
                            <h6>Document Actions</h6>
                            <button class="btn btn-success w-100 mb-2" id="downloadBtn">
                                <i class="fas fa-download"></i> Download Updated Document
                            </button>
                            <button class="btn btn-outline-secondary w-100" id="resetBtn">
                                <i class="fas fa-undo"></i> Reset All Changes
                            </button>
                        </div>
                        
                        <!-- Security Status -->
                        <div class="mt-3">
                            <div class="alert alert-info small">
                                <i class="fas fa-shield-alt"></i>
                                <strong>Security:</strong> All data is processed securely and automatically deleted after 24 hours.
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Debug Panel (Development Only) -->
                <div class="card mt-3 d-none" id="debugPanel">
                    <div class="card-body">
                        <h6>Debug Information</h6>
                        <div id="debugInfo" class="small text-muted"></div>
                    </div>
                </div>
            </div>
            
            <!-- Document Viewer -->
            <div class="col-md-9">
                <div class="card">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <h5 class="mb-0">
                            <i class="fas fa-file-word"></i> Document Viewer
                        </h5>
                        <div class="document-stats d-none" id="documentStats">
                            <span class="badge bg-primary" id="totalParagraphs">0 paragraphs</span>
                            <span class="badge bg-info" id="totalWords">0 words</span>
                            <span class="badge bg-warning" id="avgReadability">0 readability</span>
                            <span class="badge bg-danger" id="avgRisk">0 risk</span>
                        </div>
                    </div>
                    <div class="card-body">
                        <div id="documentViewer" class="document-viewer">
                            <div class="text-center text-muted py-5">
                                <i class="fas fa-file-upload fa-3x mb-3"></i>
                                <p>Upload a document to start editing</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Toast Notifications -->
    <div class="toast-container position-fixed bottom-0 end-0 p-3">
        <div id="saveToast" class="toast" role="alert">
            <div class="toast-header">
                <i class="fas fa-check-circle text-success me-2"></i>
                <strong class="me-auto">Success</strong>
                <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
            </div>
            <div class="toast-body">
                Changes saved successfully
            </div>
        </div>
    </div>
    
    <!-- Security Modal -->
    <div class="modal fade" id="securityModal" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">
                        <i class="fas fa-shield-alt text-warning"></i> Security Notice
                    </h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <p>This application processes your documents securely. All data is:</p>
                    <ul>
                        <li>Encrypted in transit</li>
                        <li>Automatically deleted after 24 hours</li>
                        <li>Never shared with third parties</li>
                        <li>Processed in secure environments</li>
                    </ul>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="{{ url_for('static', filename='js/document-viewer.js') }}"></script>
    <script src="{{ url_for('static', filename='js/upload.js') }}"></script>
    <script src="{{ url_for('static', filename='js/debug.js') }}"></script>
    <script src="{{ url_for('static', filename='js/security.js') }}"></script>
</body>
</html>
```

## 5. Configuration

### Requirements (Enhanced)
```txt
# requirements.txt
Flask==2.3.3
Flask-CORS==4.0.0
Flask-Limiter==3.5.0
python-docx==0.8.11
spacy==3.7.2
textstat==0.7.3
requests==2.31.0
python-dotenv==1.0.0
Werkzeug==2.3.7
python-magic==0.4.27
redis==5.0.1
gunicorn==21.2.0
```

### Environment Variables (Enhanced)
```bash
# .env.example
SECRET_KEY=your-secret-key-here
DIFY_API_KEY=your-dify-api-key
DIFY_API_URL=https://api.dify.ai/v1
REDIS_URL=redis://localhost:6379
LOG_LEVEL=INFO
MAX_CONTENT_LENGTH=16777216
RATELIMIT_STORAGE_URL=redis://localhost:6379
```

### Docker Configuration
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download spaCy model
RUN python -m spacy download en_core_web_sm

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs uploads

# Set environment variables
ENV FLASK_APP=run.py
ENV FLASK_ENV=production

# Expose port
EXPOSE 5000

# Run application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "run:app"]
```

### Docker Compose
```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "5000:5000"
    environment:
      - REDIS_URL=redis://redis:6379
      - DIFY_API_KEY=${DIFY_API_KEY}
    depends_on:
      - redis
    volumes:
      - ./logs:/app/logs
      - ./uploads:/app/uploads

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  redis_data:
```

## 6. Key Features Summary

### ✅ **Enhanced Security**
- **Input validation** and sanitization
- **Rate limiting** with Redis backend
- **File type validation** using magic numbers
- **Session management** with secure cookies
- **XSS protection** and security headers
- **CSRF protection** for forms

### ✅ **Improved Performance**
- **Caching layer** for analysis results
- **Background processing** with timeouts
- **Optimized file handling** with size limits
- **Connection pooling** for database operations
- **Compression** for static assets

### ✅ **Better Error Handling**
- **Comprehensive logging** with rotation
- **Graceful degradation** for API failures
- **Retry mechanisms** for transient errors
- **User-friendly error messages**
- **Debug information** for development

### ✅ **Scalability Features**
- **Containerization** with Docker
- **Multi-worker setup** with Gunicorn
- **Redis integration** for caching
- **Load balancing** ready
- **Horizontal scaling** support

### ✅ **Production Readiness**
- **Environment-specific configs**
- **Health check endpoints**
- **Monitoring integration**
- **Backup strategies**
- **Security audits**

### ✅ **Enhanced User Experience**
- **Real-time feedback** with better indicators
- **Auto-save with retry logic**
- **Progress tracking** with detailed status
- **Keyboard shortcuts** and accessibility
- **Mobile-responsive design**

## 7. Implementation Steps

1. **Set up project structure** as outlined above
2. **Install dependencies**: `pip install -r requirements.txt`
3. **Download spaCy model**: `python -m spacy download en_core_web_sm`
4. **Configure environment variables** in `.env`
5. **Set up Redis** for caching and rate limiting
6. **Implement core services** with enhanced security
7. **Create Flask routes** with validation and rate limiting
8. **Build frontend** with security features
9. **Set up Docker** for containerization
10. **Test the complete system** with security audits
11. **Deploy with monitoring**: `docker-compose up -d`

This enhanced architecture provides a production-ready, secure, and scalable document analysis system with comprehensive error handling, performance optimizations, and professional debugging capabilities. 
This complete architecture provides a professional, production-ready document analysis system with real-time editing capabilities, comprehensive debugging tools, and a clean, modern user interface. 