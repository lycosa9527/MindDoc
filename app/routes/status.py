from flask import Blueprint, jsonify, current_app
from app.services.event_manager import EventManager

bp = Blueprint('status', __name__)

@bp.route('/status/<job_id>', methods=['GET'])
def get_processing_status(job_id):
    """Get current processing status"""
    
    try:
        event_manager = EventManager(current_app)
        status = event_manager.get_status(job_id)
        
        return jsonify(status), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get status: {str(e)}'}), 500

@bp.route('/analysis/<job_id>', methods=['GET'])
def get_analysis_results(job_id):
    """Get analysis results for a specific job"""
    
    try:
        event_manager = EventManager(current_app)
        results = event_manager.get_results(job_id)
        
        if not results:
            return jsonify({'error': 'Analysis results not found'}), 404
        
        return jsonify(results), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve results: {str(e)}'}), 500 