from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages

class AuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Define public URLs that don't require authentication
        self.public_urls = [
            reverse('accounts:login'),
            reverse('accounts:register'),
            reverse('accounts:reset-otp'),
            reverse('accounts:reset-verify'),
            '/admin/',
            '/static/',
            '/media/',
            '/',  # Home page
            '/home2/',  # Secondary home page if exists
        ]

    def __call__(self, request):
        # Check if the current path requires authentication
        requires_auth = not any(
            request.path.startswith(url) 
            for url in self.public_urls
        )
        
        if requires_auth and not request.user.is_authenticated:
            messages.warning(request, 'Please login to access this page')
            return redirect('accounts:login')
            
        response = self.get_response(request)
        return response

    def process_request(self, request):
        # Additional request processing if needed
        pass