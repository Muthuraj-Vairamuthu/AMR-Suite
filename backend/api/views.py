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
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from social_django.utils import load_strategy, load_backend
from social_core.backends.oauth import BaseOAuth2
from social_core.exceptions import MissingBackend, AuthAlreadyAssociated

# Create your views here.

def home(request):
    return render(request, 'home.html') 
def home2(request):
    return render(request,'home2.html')
def scorecard_info(request):
    return render(request, 'scorecard_info.html') 

def login_view(request):
    # Clear any existing messages when first loading the page
    if request.method == 'GET':
        storage = messages.get_messages(request)
        storage.used = True

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            print(f"{username} logged in successfully")
            return redirect('upload_dataset')
        else:
            messages.error(request, 'Invalid username or password.')
            return redirect('login')
    
def resistance_info(request):
    return render(request,'resistance_info.html')
def isolation_info(request):
    return render(request,'isolation_info.html')
def login_page(request):
    return render(request, 'login_page.html')

def signup_view(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            messages.success(request, 'Account created successfully. Please login.')
            return redirect('login')
        except Exception as e:
            messages.error(request, 'Error creating account. Please try again.')
            return redirect('signup')
    
    return render(request, 'signup_page.html')

def logout_view(request):
    if request.user.is_authenticated:
        print(f"Logging out user: {request.user.username}")
        logout(request)
    return redirect('login')


@login_required
def upload_dataset(request):
    if not request.user.is_authenticated:
        return redirect('login')
        
    return render(request, 'upload_dataset.html', {
        'welcome_message': f'Welcome, {request.user.username}!'
    })
def login_user(request):
    # Your login logic here
    return HttpResponse("Login Successful")

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

def google_callback(request):
    if request.user.is_authenticated:
        return redirect('upload_dataset')
    
    try:
        strategy = load_strategy(request)
        backend = load_backend(strategy=strategy, name='google-oauth2', redirect_uri=None)
        
        if 'code' in request.GET:
            try:
                user = backend.complete(request=request)
                if user and user.is_active:
                    login(request, user)
                    print(f"Successfully authenticated Google user: {user.email}")
                    messages.success(request, f'Welcome, {user.first_name}!')
                    return redirect('upload_dataset')
            except Exception as e:
                print(f"Error completing Google authentication: {str(e)}")
                messages.error(request, f'Google authentication error: {str(e)}')
    except Exception as e:
        print(f"Error in Google callback: {str(e)}")
        messages.error(request, 'An error occurred during Google authentication.')
    
    return redirect('login')