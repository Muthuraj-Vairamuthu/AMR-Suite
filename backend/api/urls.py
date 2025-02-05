from django.urls import path
from .views import (login_page, login_user, upload_dataset, dataset_upload, 
                mapping_dataset, isolation_burden_analysis, generate_isolation_graph,
                resistance_analysis, generate_resistance_graph)

urlpatterns = [
    path('', login_page),
    path('login', login_user),
    path('upload_dataset', upload_dataset),
    path('dataset_upload', dataset_upload),
    path('mapping_dataset', mapping_dataset),
    path('isolation_burden_analysis', isolation_burden_analysis),
    path('generate_isolation_graph', generate_isolation_graph),
    path('resistance_analysis', resistance_analysis),
    path('generate_resistance_graph', generate_resistance_graph)
]
