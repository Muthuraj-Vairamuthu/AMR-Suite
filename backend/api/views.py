from django.shortcuts import render, redirect
from rest_framework.views import APIView
from . models import *
from rest_framework.response import Response
from django.http import HttpResponse

# Create your views here.


def login_page(request):
    return render(request, 'login_page.html')

def login_user(request):
    login_credentials = {
        'noel': '1234',
        'muthu': '1234',
        'rishi': '1234'
    }
    username = request.POST['username']
    password = request.POST['password']

    if username in login_credentials and login_credentials[username] == password:
        return redirect('/upload_dataset')
    else:
        return HttpResponse('Login failed')

def upload_dataset(request):
    return render(request, 'upload_dataset.html')

def dataset_upload(request):
    file = request.FILES['csv_file']
    return HttpResponse('File uploaded')
