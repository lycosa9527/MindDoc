from flask import Blueprint, request, jsonify, current_app
from app.services.debug_logger import DebugLogger
from datetime import datetime

bp = Blueprint('api', __name__)

@bp.route('/api/update-paragraph', methods=['POST'])
def update_paragraph():
    """Update paragraph content in real-time"""
    
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
        
        data = request.get_json()
        if not data:
            DebugLogger.log_warning("Invalid JSON data in paragraph update", {
                "ip": request.remote_addr,
                "content_type": request.content_type
            })
            return jsonify({'error': 'Invalid JSON data'}), 400
            
        paragraph_id = data.get('paragraph_id')
        new_text = data.get('new_text')
        job_id = data.get('job_id')
        
        # Validate input
        if not all([paragraph_id is not None, new_text, job_id]):
            DebugLogger.log_warning("Missing required fields in paragraph update", {
                "ip": request.remote_addr,
                "provided_fields": list(data.keys()),
                "required_fields": ["paragraph_id", "new_text", "job_id"]
            })
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Convert paragraph_id to int
        try:
            paragraph_id = int(paragraph_id)
        except (ValueError, TypeError):
            DebugLogger.log_warning("Invalid paragraph ID format", {
                "ip": request.remote_addr,
                "paragraph_id": data.get('paragraph_id'),
                "job_id": job_id
            })
            return jsonify({'error': 'Invalid paragraph ID format'}), 400
        
        # Get current analysis results
        results = current_app.analysis_results.get(job_id)
        if not results:
            DebugLogger.log_warning("Analysis results not found for paragraph update", {
                "ip": request.remote_addr,
                "job_id": job_id,
                "available_jobs": list(current_app.analysis_results.keys())
            })
            return jsonify({'error': 'Analysis results not found'}), 404
        
        # Update paragraph
        if paragraph_id < len(results['paragraph_analyses']):
            old_text = results['paragraph_analyses'][paragraph_id]['text']
            results['paragraph_analyses'][paragraph_id]['text'] = new_text
            
            # Re-analyze the updated paragraph
            from app.services.document_processor import DocumentProcessor
            processor = DocumentProcessor(current_app)
            updated_analysis = processor._analyze_single_paragraph(new_text, paragraph_id)
            results['paragraph_analyses'][paragraph_id].update(updated_analysis)
            
            duration = (datetime.now() - start_time).total_seconds()
            
            DebugLogger.log_info("Paragraph updated successfully", {
                "job_id": job_id,
                "paragraph_id": paragraph_id,
                "old_text_length": len(old_text),
                "new_text_length": len(new_text),
                "duration": duration,
                "ip": request.remote_addr
            })
            
            # Log successful request
            DebugLogger.log_request(
                method=request.method,
                path=request.path,
                status_code=200,
                duration=duration,
                user_agent=request.headers.get('User-Agent')
            )
            
            return jsonify({
                'success': True,
                'updated_analysis': updated_analysis
            }), 200
        else:
            DebugLogger.log_warning("Invalid paragraph ID for update", {
                "ip": request.remote_addr,
                "job_id": job_id,
                "paragraph_id": paragraph_id,
                "total_paragraphs": len(results['paragraph_analyses'])
            })
            return jsonify({'error': 'Invalid paragraph ID'}), 400
            
    except Exception as e:
        duration = (datetime.now() - start_time).total_seconds()
        
        DebugLogger.log_error("Error updating paragraph", e, {
            "ip": request.remote_addr,
            "user_agent": request.headers.get('User-Agent'),
            "duration": duration,
            "job_id": data.get('job_id') if 'data' in locals() else None
        })
        
        # Log failed request
        DebugLogger.log_request(
            method=request.method,
            path=request.path,
            status_code=500,
            duration=duration,
            user_agent=request.headers.get('User-Agent')
        )
        
        return jsonify({'error': 'Internal server error'}), 500 