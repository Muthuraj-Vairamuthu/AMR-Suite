"""
URL configuration for AMR_Suite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('api.urls')),
    path('login', include('api.urls')),
    path('upload_dataset', include('api.urls')),
    path('dataset_upload', include('api.urls')),
    path('mapping_dataset', include('api.urls')),
    path('isolation_burden_analysis', include('api.urls')),
    path('generate_isolation_graph', include('api.urls')),
    path('resistance_analysis', include('api.urls')),
    path('generate_resistance_graph', include('api.urls'))
]
