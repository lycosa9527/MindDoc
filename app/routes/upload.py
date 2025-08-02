import os
import uuid
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from app.services.event_manager import EventManager
from app.services.debug_logger import DebugLogger
from datetime import datetime

bp = Blueprint('upload', __name__)

ALLOWED_EXTENSIONS = {'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/upload', methods=['POST'])
def upload_document():
    """Handle document upload and start processing"""
    
    start_time = datetime.now()
    
    try:
        # Log request
        DebugLogger.log_request(
            method=request.method,
            path=request.path,
            status_code=200,
            duration=0,
            user_agent=request.headers.get('User-Agent')
        )
        
        if 'file' not in request.files:
            DebugLogger.log_warning("Upload attempt with no file", {
                "ip": request.remote_addr,
                "user_agent": request.headers.get('User-Agent')
            })
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            DebugLogger.log_warning("Upload attempt with empty filename", {
                "ip": request.remote_addr
            })
            return jsonify({'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            # Generate unique job ID
            job_id = str(uuid.uuid4())
            
            # Secure filename and save
            filename = secure_filename(file.filename)
            upload_folder = current_app.config['UPLOAD_FOLDER']
            file_path = os.path.join(upload_folder, f"{job_id}_{filename}")
            
            # Ensure upload directory exists
            os.makedirs(upload_folder, exist_ok=True)
            
            # Save file
            file.save(file_path)
            
            # Get file size
            file_size = os.path.getsize(file_path)
            
            DebugLogger.log_info("Document uploaded successfully", {
                "job_id": job_id,
                "filename": filename,
                "file_size": file_size,
                "file_path": file_path,
                "ip": request.remote_addr
            })
            
            # Start processing
            event_manager = EventManager(current_app)
            event_manager.start_document_processing(file_path, job_id)
            
            duration = (datetime.now() - start_time).total_seconds()
            
            # Log successful upload
            DebugLogger.log_request(
                method=request.method,
                path=request.path,
                status_code=200,
                duration=duration,
                user_agent=request.headers.get('User-Agent')
            )
            
            return jsonify({
                'job_id': job_id,
                'message': 'Document uploaded and processing started',
                'status': 'processing'
            }), 200
        
        DebugLogger.log_warning("Invalid file type uploaded", {
            "filename": file.filename if file else "None",
            "ip": request.remote_addr,
            "allowed_extensions": list(ALLOWED_EXTENSIONS)
        })
        return jsonify({'error': 'Invalid file type. Only .docx files are allowed.'}), 400
        
    except Exception as e:
        duration = (datetime.now() - start_time).total_seconds()
        
        DebugLogger.log_error("Upload failed", e, {
            "ip": request.remote_addr,
            "user_agent": request.headers.get('User-Agent'),
            "duration": duration
        })
        
        # Log failed request
        DebugLogger.log_request(
            method=request.method,
            path=request.path,
            status_code=500,
            duration=duration,
            user_agent=request.headers.get('User-Agent')
        )
        
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500 