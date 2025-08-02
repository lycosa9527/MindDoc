import requests
from typing import Dict, Any
from app.services.debug_logger import DebugLogger
from datetime import datetime

class DifyService:
    def __init__(self, app):
        self.app = app
        self.api_key = app.config.get('DIFY_API_KEY')
        self.api_url = app.config.get('DIFY_API_URL', 'https://api.dify.ai/v1')
        
        if not self.api_key:
            DebugLogger.log_warning("Dify API key not configured", {
                "service": "Dify",
                "status": "disabled",
                "api_url": self.api_url
            })
            self.headers = None
        else:
            self.headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            DebugLogger.log_info("✅ Dify service initialized", {
                "service": "Dify",
                "status": "enabled",
                "api_url": self.api_url
            })
    
    def analyze_document_with_dify(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send document analysis request to Dify API"""
        
        if not self.headers:
            DebugLogger.log_warning("Cannot analyze with Dify: API key not configured", {
                "service": "Dify",
                "action": "analyze_document",
                "status": "skipped"
            })
            return {
                'error': 'Dify API key not configured',
                'suggestions': []
            }
        
        start_time = datetime.now()
        
        try:
            DebugLogger.log_api_call("Dify", "/chat-messages", "started")
            
            # Prepare payload
            paragraphs = document_data.get('paragraph_analyses', [])
            text_content = "\n\n".join([p['text'] for p in paragraphs])
            
            prompt = f"""
            Analyze the following document and provide improvement suggestions:
            
            Document Content:
            {text_content}
            
            Please provide:
            1. Overall document assessment
            2. Specific improvement suggestions for each paragraph
            3. Writing style recommendations
            4. Content structure suggestions
            5. Grammar and clarity improvements
            """
            
            payload = {
                'inputs': {},
                'query': prompt,
                'response_mode': 'blocking',
                'conversation_id': '',
                'user': 'minddoc_user'
            }
            
            DebugLogger.log_debug("Sending request to Dify API", {
                "service": "Dify",
                "endpoint": "/chat-messages",
                "payload_size": len(str(payload)),
                "text_length": len(text_content),
                "paragraphs": len(paragraphs)
            })
            
            # Make API call
            response = requests.post(
                f"{self.api_url}/chat-messages",
                headers=self.headers,
                json=payload,
                timeout=60
            )
            
            duration = (datetime.now() - start_time).total_seconds()
            
            if response.status_code == 200:
                result = self._process_dify_response(response.json())
                DebugLogger.log_api_call("Dify", "/chat-messages", "success", duration)
                DebugLogger.log_info("✅ Dify API analysis completed successfully", {
                    "duration": duration,
                    "suggestions_count": len(result.get('suggestions', [])),
                    "response_size": len(str(response.json()))
                })
                return result
            else:
                raise Exception(f"Dify API error: {response.status_code} - {response.text}")
                
        except requests.exceptions.Timeout:
            DebugLogger.log_error("Dify API request timed out", context={
                "service": "Dify",
                "timeout": 60,
                "duration": (datetime.now() - start_time).total_seconds()
            })
            return {
                'error': 'API request timed out',
                'suggestions': []
            }
        except requests.exceptions.RequestException as e:
            DebugLogger.log_error(f"Dify API network error", e, {
                "service": "Dify",
                "api_url": self.api_url,
                "duration": (datetime.now() - start_time).total_seconds()
            })
            return {
                'error': f'Network error: {str(e)}',
                'suggestions': []
            }
        except Exception as e:
            DebugLogger.log_error("Dify API analysis failed", e, {
                "service": "Dify",
                "duration": (datetime.now() - start_time).total_seconds()
            })
            return {
                'error': str(e),
                'suggestions': []
            }
    
    def _process_dify_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Process Dify API response"""
        
        try:
            answer = response.get('answer', '')
            
            # Parse suggestions (simplified)
            suggestions = []
            lines = answer.split('\n')
            
            for line in lines:
                line = line.strip()
                if line.startswith('-') or line.startswith('•'):
                    suggestion = line[1:].strip()
                    if suggestion:
                        suggestions.append(suggestion)
            
            DebugLogger.log_debug("Dify response processed", {
                "raw_response_length": len(answer),
                "suggestions_extracted": len(suggestions),
                "response_lines": len(lines)
            })
            
            return {
                'suggestions': suggestions,
                'raw_response': answer
            }
        except Exception as e:
            DebugLogger.log_error(f"Error processing Dify response", e, {
                "response_keys": list(response.keys()) if response else [],
                "response_type": type(response).__name__
            })
            return {
                'suggestions': [],
                'raw_response': 'Error processing response'
            } 