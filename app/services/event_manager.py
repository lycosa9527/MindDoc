import threading
from datetime import datetime
from typing import Dict, Any
from app.services.debug_logger import DebugLogger

class EventManager:
    def __init__(self, app):
        self.app = app
        self.processing_threads = {}
    
    def start_document_processing(self, file_path: str, job_id: str) -> None:
        """Start document processing in background thread"""
        
        def process_document():
            try:
                from app.services.document_processor import DocumentProcessor
                from app.services.dify_service import DifyService
                
                processor = DocumentProcessor(self.app)
                dify_service = DifyService(self.app)
                
                # Process document
                results = processor.process_document(file_path, job_id)
                
                # Send to Dify for additional analysis
                dify_results = dify_service.analyze_document_with_dify(results)
                
                # Combine results
                combined_results = {
                    **results,
                    'dify_analysis': dify_results
                }
                
                # Store final results
                self.app.analysis_results[job_id] = combined_results
                
                DebugLogger.log_info(f"Document processing completed for job {job_id}")
                
            except Exception as e:
                DebugLogger.log_error(f"Document processing failed for job {job_id}", e)
                self._update_status(job_id, "failed", f"Processing failed: {str(e)}")
        
        # Start processing in background thread
        thread = threading.Thread(target=process_document)
        thread.daemon = True
        thread.start()
        
        self.processing_threads[job_id] = thread
    
    def _update_status(self, job_id: str, status: str, message: str) -> None:
        """Update processing status"""
        
        self.app.processing_status[job_id] = {
            'status': status,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_status(self, job_id: str) -> Dict[str, Any]:
        """Get current processing status"""
        
        return self.app.processing_status.get(job_id, {
            'status': 'unknown',
            'message': 'Job not found'
        })
    
    def get_results(self, job_id: str) -> Dict[str, Any]:
        """Get analysis results"""
        
        return self.app.analysis_results.get(job_id, {}) 