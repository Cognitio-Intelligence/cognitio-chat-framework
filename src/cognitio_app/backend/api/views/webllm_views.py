import json
import logging
import time
import uuid
from collections import deque
from threading import Event, Lock, Timer
from typing import Dict, Any, Optional, Generator
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.http import StreamingHttpResponse

from ..models.chat import ChatSession, ChatMessage

logger = logging.getLogger(__name__)

# Configuration constants
DEFAULT_WEBLLM_TIMEOUT = 180  # 3 minutes default
MAX_CONCURRENT_REQUESTS = 10
CLEANUP_INTERVAL = 300  # 5 minutes
REQUEST_TTL = 600  # 10 minutes

@dataclass
class WebLLMRequest:
    """Represents a WebLLM request with all necessary metadata"""
    request_id: str
    request_type: str
    content: str
    system_prompt: str = "You are a helpful AI assistant."
    model: str = "Llama-3.2-1B-Instruct"
    temperature: float = 0.7
    max_tokens: int = 4096
    stream: bool = False
    timeout: int = DEFAULT_WEBLLM_TIMEOUT
    session_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    status: str = "pending"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            'request_id': self.request_id,
            'type': self.request_type,
            'data': {
                'content': self.content,
                'system_prompt': self.system_prompt,
                'model': self.model,
                'temperature': self.temperature,
                'max_tokens': self.max_tokens,
                'stream': self.stream,
                'timeout': self.timeout
            },
            'timestamp': self.created_at.timestamp(),
            'status': self.status
        }

@dataclass
class WebLLMResponse:
    """Represents a WebLLM response"""
    request_id: str
    content: str = ""
    error: Optional[str] = None
    usage: Dict[str, Any] = field(default_factory=dict)
    done: bool = False
    created_at: datetime = field(default_factory=datetime.now)

class WebLLMBridgeManager:
    """
    Centralized manager for WebLLM requests and responses.
    
    This class handles the coordination between the Django backend and the 
    frontend WebLLM service running in the browser.
    """
    
    def __init__(self):
        self._requests: Dict[str, WebLLMRequest] = {}
        self._response_queues: Dict[str, deque] = {}
        self._completion_events: Dict[str, Event] = {}
        self._lock = Lock()
        self._cleanup_timer: Optional[Timer] = None
        self._start_cleanup_timer()
    
    def _start_cleanup_timer(self):
        """Start periodic cleanup of expired requests"""
        if self._cleanup_timer:
            self._cleanup_timer.cancel()
        self._cleanup_timer = Timer(CLEANUP_INTERVAL, self._cleanup_expired_requests)
        self._cleanup_timer.daemon = True
        self._cleanup_timer.start()
    
    def _cleanup_expired_requests(self):
        """Clean up requests older than TTL"""
        try:
            with self._lock:
                now = datetime.now()
                expired_ids = [
                    req_id for req_id, req in self._requests.items()
                    if (now - req.created_at).total_seconds() > REQUEST_TTL
                ]
                
                for req_id in expired_ids:
                    self._remove_request(req_id)
                    logger.info(f"Cleaned up expired WebLLM request {req_id}")
                    
            # Restart cleanup timer
            self._start_cleanup_timer()
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
            self._start_cleanup_timer()
    
    def _remove_request(self, request_id: str):
        """Remove a request and all associated data (must be called with lock held)"""
        self._requests.pop(request_id, None)
        self._response_queues.pop(request_id, None)
        if request_id in self._completion_events:
            self._completion_events[request_id].set()  # Unblock any waiters
            self._completion_events.pop(request_id, None)
    
    def create_request(self, request_data: Dict[str, Any]) -> WebLLMRequest:
        """Create a new WebLLM request"""
        request_id = str(uuid.uuid4())
        
        webllm_request = WebLLMRequest(
            request_id=request_id,
            request_type=request_data.get('type', 'chat'),
            content=request_data.get('content', ''),
            system_prompt=request_data.get('system_prompt', 'You are a helpful AI assistant.'),
            model=request_data.get('model', 'Llama-3.2-1B-Instruct'),
            temperature=request_data.get('temperature', 0.7),
            max_tokens=request_data.get('max_tokens', 4096),
            stream=request_data.get('stream', False),
            timeout=request_data.get('timeout', DEFAULT_WEBLLM_TIMEOUT),
            session_id=request_data.get('session_id')
        )
        
        with self._lock:
            if len(self._requests) >= MAX_CONCURRENT_REQUESTS:
                # Clean up oldest requests if at capacity
                oldest_id = min(self._requests.keys(), 
                              key=lambda x: self._requests[x].created_at)
                self._remove_request(oldest_id)
                logger.warning(f"Removed oldest request {oldest_id} due to capacity limit")
            
            self._requests[request_id] = webllm_request
            self._completion_events[request_id] = Event()
            
            if webllm_request.stream:
                self._response_queues[request_id] = deque()
        
        logger.info(f"Created WebLLM request {request_id} for model {webllm_request.model}")
        return webllm_request
    
    def get_pending_requests(self) -> list[WebLLMRequest]:
        """Get all pending requests for frontend polling"""
        with self._lock:
            return [req for req in self._requests.values() if req.status == 'pending']
    
    def mark_processing(self, request_id: str) -> bool:
        """Mark a request as being processed"""
        with self._lock:
            if request_id in self._requests:
                self._requests[request_id].status = 'processing'
                return True
            return False
    
    def submit_response(self, request_id: str, response: WebLLMResponse) -> bool:
        """Submit a response for a request"""
        with self._lock:
            if request_id not in self._requests:
                logger.warning(f"Received response for unknown request {request_id}")
                return False
            
            request = self._requests[request_id]
            
            if request.stream:
                # For streaming requests, add to queue
                if request_id in self._response_queues:
                    self._response_queues[request_id].append(response)
                    # Signal completion only for final response
                    if response.done or response.error:
                        self._completion_events[request_id].set()
                        request.status = 'completed'
                else:
                    logger.error(f"No response queue for streaming request {request_id}")
                    return False
            else:
                # For non-streaming, signal completion immediately
                self._response_queues[request_id] = deque([response])
                self._completion_events[request_id].set()
                request.status = 'completed'
            
            logger.debug(f"Response submitted for request {request_id}")
            return True
    
    def wait_for_completion(self, request_id: str, timeout: Optional[int] = None) -> bool:
        """Wait for a request to complete"""
        if request_id not in self._completion_events:
            return False
        
        event = self._completion_events[request_id]
        request = self._requests.get(request_id)
        actual_timeout = timeout or (request.timeout if request else DEFAULT_WEBLLM_TIMEOUT)
        
        return event.wait(timeout=actual_timeout)
    
    def get_response(self, request_id: str) -> Optional[WebLLMResponse]:
        """Get the next response for a request (for streaming) or the final response"""
        with self._lock:
            if request_id not in self._response_queues:
                return None
            
            queue = self._response_queues[request_id]
            if queue:
                return queue.popleft()
            return None
    
    def get_final_response(self, request_id: str) -> Optional[WebLLMResponse]:
        """Get the final response for a non-streaming request"""
        with self._lock:
            if request_id not in self._response_queues:
                return None
            
            queue = self._response_queues[request_id]
            if queue:
                # For non-streaming, there should be only one response
                response = queue.popleft()
                self._remove_request(request_id)
                return response
            return None
    
    def cancel_request(self, request_id: str):
        """Cancel a request"""
        with self._lock:
            if request_id in self._requests:
                self._remove_request(request_id)
                logger.info(f"Cancelled WebLLM request {request_id}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current bridge status"""
        with self._lock:
            requests_by_status = {}
            for req in self._requests.values():
                status = req.status
                requests_by_status[status] = requests_by_status.get(status, 0) + 1
            
            return {
                'total_requests': len(self._requests),
                'requests_by_status': requests_by_status,
                'max_concurrent': MAX_CONCURRENT_REQUESTS,
                'bridge_active': True
            }


# Global bridge manager instance
bridge_manager = WebLLMBridgeManager()

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def webllm_generate(request):
    """
    Backend endpoint to generate WebLLM responses
    This is called by the backend WebLLM functions
    """
    try:
        system_role = request.data.get('system_role', '')
        question = request.data.get('question', '')
        request_type = request.data.get('type', 'generate')
        max_tokens = request.data.get('max_tokens', 4096)
        temperature = request.data.get('temperature', 0.7)
        custom_timeout = request.data.get('timeout', DEFAULT_WEBLLM_TIMEOUT)
        
        if not system_role or not question:
            return Response({
                'error': 'system_role and question are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create request using new manager
        webllm_request = bridge_manager.create_request({
            'type': request_type,
            'content': question,
            'system_prompt': system_role,
            'max_tokens': max_tokens,
            'temperature': temperature,
            'timeout': custom_timeout,
            'stream': False
        })
        
        # Wait for completion
        if bridge_manager.wait_for_completion(webllm_request.request_id, custom_timeout):
            response = bridge_manager.get_final_response(webllm_request.request_id)
            
            if response and response.error:
                return Response({
                    'error': response.error
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            return Response({
                'content': response.content if response else '',
                'usage': response.usage if response else {}
            })
        else:
            bridge_manager.cancel_request(webllm_request.request_id)
            return Response({
                'error': f'WebLLM request timeout after {custom_timeout} seconds'
            }, status=status.HTTP_408_REQUEST_TIMEOUT)
    
    except Exception as e:
        logger.error(f"Error in webllm_generate: {str(e)}")
        return Response({
            'error': f'WebLLM generation failed: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def webllm_chat(request):
    """
    Chat endpoint using WebLLM bridge
    """
    # Accept both 'content' and 'user_message' for compatibility
    content = (request.data.get('content') or request.data.get('user_message') or '').strip()
    system_prompt = request.data.get('system_prompt', 'You are a helpful AI assistant.')
    model = request.data.get('model', 'Llama-3.2-1B-Instruct')
    allowed_models = [
        'Llama-3.2-1B-Instruct',
        'Llama-3.2-3B-Instruct',
        'Phi-3.5-mini-instruct',
        'Qwen2.5-0.5B-Instruct',
        'Qwen2.5-1.5B-Instruct'
    ]
    if model not in allowed_models:
        model = 'Llama-3.2-1B-Instruct'

    if not content:
        return Response({
            'error': 'Content is required'
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        logger.info(f"WebLLM chat request: {content[:100]}..., model: {model}")
        
        # If streaming is requested, handle via streaming response
        if request.data.get('stream', False):
            # Create streaming request
            webllm_request = bridge_manager.create_request({
                'type': 'chat',
                'content': content,
                'system_prompt': system_prompt,
                'model': model,
                'temperature': request.data.get('temperature', 0.7),
                'max_tokens': request.data.get('max_tokens', 4096),
                'stream': True,
                'timeout': request.data.get('timeout', DEFAULT_WEBLLM_TIMEOUT),
                'session_id': request.data.get('session_id')
            })
            
            # Return streaming response
            response = StreamingHttpResponse(
                stream_webllm_response(webllm_request),
                content_type='text/plain'
            )
            response['Cache-Control'] = 'no-cache'
            return response
        
        # For non-streaming, use the bridge system
        webllm_request = bridge_manager.create_request({
            'type': 'chat',
            'content': content,
            'system_prompt': system_prompt,
            'model': model,
            'temperature': request.data.get('temperature', 0.7),
            'max_tokens': request.data.get('max_tokens', 4096),
            'stream': False,  # Non-streaming through bridge
            'timeout': request.data.get('timeout', DEFAULT_WEBLLM_TIMEOUT),
            'session_id': request.data.get('session_id')
        })
        
        # Non-streaming response - wait for completion
        if bridge_manager.wait_for_completion(webllm_request.request_id, webllm_request.timeout):
            response = bridge_manager.get_final_response(webllm_request.request_id)
            
            if response and response.error:
                return Response({
                    'error': response.error
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Save chat messages to session if provided
            try:
                if webllm_request.session_id:
                    save_chat_messages(webllm_request, response)
            except Exception as e:
                logger.error(f"Error saving chat message: {e}")
            
            return Response({
                'content': response.content if response else '',
                'usage': response.usage if response else {}
            })
        else:
            bridge_manager.cancel_request(webllm_request.request_id)
            return Response({
                'error': f'WebLLM request timed out after {webllm_request.timeout} seconds'
            }, status=status.HTTP_504_GATEWAY_TIMEOUT)
            
    except Exception as e:
        logger.error(f"Error in webllm_chat: {str(e)}")
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def save_chat_messages(webllm_request: WebLLMRequest, response: Optional[WebLLMResponse]):
    """Save chat messages to session"""
    if not webllm_request.session_id:
        return
    
    try:
        session = ChatSession.objects.get(id=webllm_request.session_id)
        
        # Save user message
        ChatMessage.objects.create(
            session=session,
            message_type='user',
            content=webllm_request.content,
            metadata={'model': webllm_request.model}
        )
        
        # Save assistant response if available
        if response and response.content:
            ChatMessage.objects.create(
                session=session,
                message_type='assistant',
                content=response.content,
                tokens_used=response.usage.get('total_tokens', 0) if response.usage else 0,
                metadata={
                    'model': webllm_request.model,
                    'usage': response.usage
                }
            )
            
    except ChatSession.DoesNotExist:
        logger.warning(f"Chat session {webllm_request.session_id} not found")
    except Exception as e:
        logger.error(f"Error saving chat messages: {e}")


def stream_webllm_response(webllm_request: WebLLMRequest) -> Generator[str, None, None]:
    """
    Stream WebLLM responses in real-time
    
    This generator yields Server-Sent Events for streaming responses
    """
    start_time = time.time()
    logger.info(f"Starting stream for WebLLM request {webllm_request.request_id}")
    
    try:
        last_activity = start_time
        poll_interval = 0.2  # 200ms polling - more responsive
        response_received = False
        
        while True:
            elapsed = time.time() - start_time
            
            # Check for timeout
            if elapsed >= webllm_request.timeout:
                logger.warning(f"Stream timeout after {elapsed:.1f}s for request {webllm_request.request_id}")
                yield f"data: {json.dumps({'error': f'Request timed out after {elapsed:.1f} seconds'})}\n\n"
                break
            
            # Get next response chunk
            response = bridge_manager.get_response(webllm_request.request_id)
            
            if response is not None:
                last_activity = time.time()
                response_received = True
                
                if response.error:
                    logger.error(f"Stream error for {webllm_request.request_id}: {response.error}")
                    yield f"data: {json.dumps({'error': response.error})}\n\n"
                    break
                elif response.content:
                    yield f"data: {json.dumps({'delta': response.content})}\n\n"
                    
                    if response.done:
                        logger.info(f"Stream completed for {webllm_request.request_id}")
                        # Final usage information
                        if response.usage:
                            yield f"data: {json.dumps({'usage': response.usage})}\n\n"
                        
                        # Save chat messages for completed requests
                        try:
                            save_chat_messages(webllm_request, response)
                        except Exception as e:
                            logger.error(f"Error saving chat messages: {e}")
                        break
            else:
                # No new response, check if we should continue waiting
                time_since_activity = time.time() - last_activity
                
                # More lenient timeout for initial response
                max_inactive_time = 30 if not response_received else 10
                
                if time_since_activity > max_inactive_time:
                    logger.warning(f"Stream inactive for {time_since_activity:.1f}s for request {webllm_request.request_id}")
                    yield f"data: {json.dumps({'error': f'Stream inactive for {time_since_activity:.1f} seconds. Please ensure WebLLM is initialized in your browser.'})}\n\n"
                    break
                
                # Check if request still exists
                if webllm_request.request_id not in bridge_manager._requests:
                    logger.info(f"Request {webllm_request.request_id} no longer exists, ending stream")
                    break
                
                # Wait before next poll
                time.sleep(poll_interval)
                
    except Exception as e:
        logger.error(f"Error in stream for request {webllm_request.request_id}: {e}")
        yield f"data: {json.dumps({'error': f'Stream error: {str(e)}'})}\n\n"
        
    finally:
        # Clean up the request
        bridge_manager.cancel_request(webllm_request.request_id)
        logger.info(f"Ended stream for request {webllm_request.request_id}")

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def webllm_processing(request):
    """
    Endpoint to receive WebLLM processing updates from frontend
    This allows the backend to monitor WebLLM processing in real-time
    """
    try:
        session_id = request.data.get('session_id')
        model = request.data.get('model', 'Unknown')
        status = request.data.get('status', 'unknown')
        user_message = request.data.get('user_message', '')
        chunk = request.data.get('chunk', '')
        chunk_count = request.data.get('chunk_count', 0)
        partial_content = request.data.get('partial_content', '')
        final_content = request.data.get('final_content', '')
        processing_time_ms = request.data.get('processing_time_ms', 0)
        chunks_processed = request.data.get('chunks_processed', 0)
        usage = request.data.get('usage', {})
        error_message = request.data.get('error_message', '')
        
        # Log different types of processing updates
        if status == 'started':
            logger.info(f"🚀 WebLLM processing started - Session: {session_id}, Model: {model}, Message: {user_message[:100]}...")
        elif status == 'streaming':
            logger.info(f"📡 WebLLM streaming - Session: {session_id}, Model: {model}, Chunk: {chunk_count}, Content: {partial_content}")
        elif status == 'completed':
            logger.info(f"✅ WebLLM processing completed - Session: {session_id}, Model: {model}, "
                       f"Time: {processing_time_ms}ms, Chunks: {chunks_processed}, "
                       f"Tokens: {usage.get('total_tokens', 0)}, Content: {len(final_content)} chars")
        elif status == 'error':
            logger.error(f"❌ WebLLM processing error - Session: {session_id}, Model: {model}, Error: {error_message}")
        
        # You can also save this to database for analytics
        # For example, create a WebLLMProcessingLog model to track performance
        
        return Response({
            'success': True,
            'message': f'Processing update received: {status}',
            'timestamp': time.time()
        })
        
    except Exception as e:
        logger.error(f"Error in webllm_processing: {str(e)}")
        return Response({
            'error': f'Failed to process WebLLM update: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@api_view(['GET'])
@permission_classes([])  # Allow unauthenticated access
def webllm_status(request):
    """
    Get WebLLM bridge status
    """
    try:
        status_info = bridge_manager.get_status()
        return Response(status_info)
    
    except Exception as e:
        logger.error(f"Error in webllm_status: {str(e)}")
        return Response({
            'error': f'Failed to get status: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@api_view(['POST'])
@permission_classes([])  # Allow unauthenticated access for frontend WebLLM service
def webllm_insights(request):
    """
    Endpoint for WebLLM service to log insights (optional)
    This endpoint is called by the frontend WebLLM service but doesn't need to do much
    """
    try:
        content = request.data.get('content', '')
        model = request.data.get('model', 'WebLLM')
        timestamp = request.data.get('timestamp', '')
        
        # Log the insight for monitoring purposes
        logger.info(f"WebLLM insight logged: {len(content)} characters from model {model}")
        
        return Response({
            'success': True,
            'message': 'Insight logged successfully'
        })
        
    except Exception as e:
        logger.error(f"Error in webllm_insights: {str(e)}")
        return Response({
            'error': f'Failed to log insight: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@api_view(['POST'])
@permission_classes([])  # Allow unauthenticated access for frontend WebLLM service
def webllm_local_log(request):
    """
    Endpoint for WebLLM service to log chat messages (compatibility endpoint)
    This endpoint is called by the frontend WebLLM service
    """
    try:
        role = request.data.get('role', 'user')
        content = request.data.get('content', '')
        model = request.data.get('model', 'WebLLM')
        
        # Log the chat message for monitoring purposes
        logger.info(f"WebLLM chat log: {role} message ({len(content)} chars) from model {model}")
        
        return Response({
            'success': True,
            'message': 'Chat message logged successfully'
        })
        
    except Exception as e:
        logger.error(f"Error in webllm_local_log: {str(e)}")
        return Response({
            'error': f'Failed to log chat message: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@api_view(['GET'])
@permission_classes([])  # Allow unauthenticated access
def webllm_diagnostic(request):
    """
    Diagnostic endpoint to check WebLLM bridge system status
    """
    try:
        status_info = bridge_manager.get_status()
        
        diagnostic_info = {
            'bridge_status': 'active',
            'total_requests': status_info['total_requests'],
            'requests_by_status': status_info['requests_by_status'],
            'max_concurrent_requests': status_info['max_concurrent'],
            'instructions': {
                'frontend_required': 'WebLLM bridge requires frontend to be loaded in browser',
                'webllm_initialization': 'WebLLM model must be initialized in browser',
                'polling_required': 'Frontend must be actively polling for requests',
                'check_console': 'Open browser console to see WebLLM initialization progress'
            }
        }
        
        return Response(diagnostic_info)
        
    except Exception as e:
        logger.error(f"Error in webllm_diagnostic: {str(e)}")
        return Response({
            'error': f'Diagnostic failed: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)