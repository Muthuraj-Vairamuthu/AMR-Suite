from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Main home page
    path('home/', views.home, name='home_page'),  # Explicit home path
    path('upload/', views.upload_dataset, name='upload_dataset'),
    path('login/', views.login_page, name='login'),
    # ... other URLs ...
] 