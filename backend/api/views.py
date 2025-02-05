from django.shortcuts import render, redirect
from rest_framework.views import APIView
from . models import *
from rest_framework.response import Response
from django.http import HttpResponse
import pandas as pd
import csv
import numpy as np
import json
from io import BytesIO
from . analysis_code import *
import matplotlib
matplotlib.use('Agg')  # Set the backend to Agg before importing pyplot
import matplotlib.pyplot as plt


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

        source_columns = dataset[request.session['mapping_data']['source_input']].unique()

        return render(request, 'isolation_burden_analysis.html', {
            'source_columns': source_columns, 
            'columns': columns
        })
    return redirect('upload_dataset')

def generate_isolation_graph(request):
    if request.method == 'POST':
        # Get form data
        source = request.POST.get('source')
        attribute = request.POST.get('attribute')
        
        # Get dataset from session
        dataset_json = request.session.get('dataset')
        if dataset_json:
            dataset = pd.read_json(dataset_json)
            mappings = request.session.get('mapping_data')
            
            # Generate the plot
            fig = isolation_burden_analysis_graph(dataset, source,attribute, mappings)
            
            # Convert plot to image
            buffer = BytesIO()
            fig.savefig(buffer, format='png', bbox_inches='tight', transparent=True)
            buffer.seek(0)
            plt.close(fig)  # Close the specific figure
            
            # Return the image
            return HttpResponse(buffer.getvalue(), content_type='image/png')
            
    return HttpResponse('Invalid request', status=400)

def resistance_analysis(request):
    dataset_json = request.session.get('dataset')
    if dataset_json:
        dataset = pd.read_json(dataset_json)
        columns = dataset.columns.tolist()

        infection_columns = dataset[request.session['mapping_data']['bacterial_infection']].unique()
        source_columns = dataset[request.session['mapping_data']['source_input']].unique()
        antibiotic_columns = []

        for column in columns:
            antibiotic_format = request.session['mapping_data']['antibiotic_format']
            antibiotic_format = antibiotic_format.replace('Antibiotic', '')
            if column.endswith(antibiotic_format):
                antibiotic_columns.append(column)
        return render(request, 'isolation_burden_analysis.html', {
            'infection_columns': infection_columns, 
            'source_columns': source_columns, 
            'antibiotic_columns': antibiotic_columns, 
            'columns': columns
        })
    return redirect('upload_dataset')

def generate_resistance_graph(request):
    if request.method == 'POST':
        # Get form data
        source = request.POST.get('source')
        infection = request.POST.get('infection')
        antibiotic = request.POST.get('antibiotic')
        
        # Get dataset from session
        dataset_json = request.session.get('dataset')
        if dataset_json:
            dataset = pd.read_json(dataset_json)
            mappings = request.session.get('mapping_data')
            
            # Generate the plot
            fig = resistance_analysis_graph(dataset, source, infection, antibiotic, mappings)
            
            # Convert plot to image
            buffer = BytesIO()
            fig.savefig(buffer, format='png', bbox_inches='tight', transparent=True)
            buffer.seek(0)
            plt.close(fig)  # Close the specific figure
            
            # Return the image
            return HttpResponse(buffer.getvalue(), content_type='image/png')
            
    return HttpResponse('Invalid request', status=400)

def scorecards(request):
    return render(request, 'scorecards.html')