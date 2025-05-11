from .utils import log_event

class SessionLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        if not request.session.exists(request.session.session_key):
            user = request.user.username if request.user.is_authenticated else 'anonymous'
            log_event('SESSION_EXPIRED', user, "User session expired")
            
        return response