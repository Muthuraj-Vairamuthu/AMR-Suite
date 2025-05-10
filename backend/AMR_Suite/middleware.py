import logging
import traceback
from django.http import JsonResponse
from django.contrib.sessions.middleware import SessionMiddleware
from .utils import log_event

class ErrorLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
            return response
        except Exception as e:
            user = request.user.username if request.user.is_authenticated else 'anonymous'
            log_event(
                event_type="ERROR",
                user=user,
                description=f"Unhandled exception: {str(e)}",
                details_dict={"exception": str(e), "stack_trace": traceback.format_exc()}
            )
            return JsonResponse({'error': 'An unexpected error occurred.'}, status=500)

class SessionExpiryLoggingMiddleware(SessionMiddleware):
    def process_response(self, request, response):
        if not request.session or request.session.is_empty():
            user = request.user.username if request.user.is_authenticated else 'anonymous'
            log_event(
                event_type="SESSION_EXPIRED",
                user=user,
                description="User session expired."
            )
        return super().process_response(request, response) 