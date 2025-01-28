from django.urls import path
from .views import login_page, login_user, upload_dataset, dataset_upload

urlpatterns = [
    path('', login_page),
    path('login', login_user),
    path('upload_dataset', upload_dataset),
    path('dataset_upload', dataset_upload)
]
