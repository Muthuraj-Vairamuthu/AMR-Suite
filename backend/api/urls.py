from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),  # Default route goes to login
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('upload-dataset/', views.upload_dataset, name='upload_dataset'),
    path('dataset_upload', views.dataset_upload, name='dataset_upload'),
    path('mapping_dataset', views.mapping_dataset, name='mapping_dataset'),
    path('isolation_burden_analysis', views.isolation_burden_analysis, name='isolation_burden_analysis'),
    path('generate_isolation_graph', views.generate_isolation_graph, name='generate_isolation_graph'),
    path('resistance_analysis', views.resistance_analysis, name='resistance_analysis'),
    path('generate_resistance_graph', views.generate_resistance_graph, name='generate_resistance_graph'),
    path('oauth/callback/google/', views.google_callback, name='google_callback'),
]
