from django.shortcuts import render, redirect
from rest_framework.views import APIView
from . models import *
from rest_framework.response import Response
from django.http import HttpResponse
import pandas as pd
import csv
import numpy as np
import json

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
    dataset = pd.read_csv(file)
    dataset = dataset.sort_values(by='Year')
    
    # Store dataset in session
    request.session['dataset'] = dataset.to_json()
    
    columns = dataset.columns.tolist()
    return render(request, 'dataset_mapping.html', {'columns': columns})

def mapping_dataset(request):
    if request.method == 'POST':
        # Get dataset from session
        dataset_json = request.session.get('dataset')
        if dataset_json:
            dataset = pd.read_json(dataset_json)
            
            mapping_data = {
                'bacterial_infection': request.POST.get('bacterial_infection'),
                'source_input': request.POST.get('source_input'),
                'antibiotic_format': request.POST.get('antibiotic_format'),
                'dataset_format': request.POST.get('dataset_format'),
                'cluster_attribute': request.POST.get('cluster_attribute'),
                'time_stamp': request.POST.get('time_stamp')
            }
            
            # Store mapping data in session
            request.session['mapping_data'] = mapping_data
            
            print("Received mapping data:", mapping_data)
            print("Dataset shape:", dataset.shape)
            
            return render(request, 'main_results.html')
        else:
            return HttpResponse('No dataset found in session')
    
    return redirect('upload_dataset')


def isolation_burden_analysis(request):
    # Get dataset from session
    dataset_json = request.session.get('dataset')
    if dataset_json:
        dataset = pd.read_json(dataset_json)
        columns = dataset.columns.tolist()
        return render(request, 'isolation_burden_analysis.html', {'columns': columns})
    return redirect('upload_dataset')

def generate_isolation_graph(request):
    if request.method == 'POST':
        # Get form data
        attribute = request.POST.get('attribute')
        source = request.POST.get('source')
        
        # Get dataset from session
        dataset_json = request.session.get('dataset')
        if dataset_json:
            dataset = pd.read_json(dataset_json)
            
            # TODO: Generate your graph here using matplotlib or plotly
            # For now, returning a placeholder response
            return HttpResponse('Graph generation endpoint')
            
    return HttpResponse('Invalid request', status=400)

def resistance_analysis(request):
    return render(request, 'resistance_analysis.html')

def scorecards(request):
    return render(request, 'scorecards.html')