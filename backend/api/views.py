from django.shortcuts import render, redirect
from rest_framework.views import APIView
from . models import *
from rest_framework.response import Response
from django.http import HttpResponse, JsonResponse
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
import mimetypes
import magic
import io
import base64
from django.conf import settings


# Create your views here.
def home(request):
    """Renders the main home page"""
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
            return redirect('upload_dataset/')
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

def mapping_dataset(request):
    if request.method == 'POST':
        dataset_json = request.session.get('dataset')
        if dataset_json:
            dataset = pd.read_json(dataset_json)
            
            mapping_data = {
                'bacterial_infection': request.POST.get('bacterial_infection'),
                'source_input': request.POST.get('source_input'),
                'dataset_format': request.POST.get('dataset_format'),
                'cluster_attribute': request.POST.get('cluster_attribute'),
                'time_stamp': request.POST.get('time_stamp'),
                'antibiotic_format': request.POST.get('antibiotic_format'),
                'antibiotic_name_col': request.POST.get('antibiotic_name_col'),
                'antibiotic_result_col': request.POST.get('antibiotic_result_col'),
                'date_format': request.POST.get('date_format'),
                'date_column': request.POST.get('date_column'),
                'resistance_granularity': request.POST.get('resistance_granularity')
            }

            request.session['mapping_data'] = mapping_data

            if mapping_data['dataset_format'] == 'Wide':
                suffix = mapping_data['antibiotic_format'].replace('Antibiotic', '')
                antibiotic_columns = [col for col in dataset.columns if col.endswith(suffix)]
                antibiotic_columns = sorted(list(set(antibiotic_columns)))

                request.session['antibiotic_columns'] = antibiotic_columns

            else:
                antibiotic_columns = dataset[mapping_data['antibiotic_name_col']].unique().tolist()
                request.session['antibiotic_columns'] = antibiotic_columns

                dataset[antibiotic_columns] = None

                for index, row in dataset.iterrows():
                    antibiotic_name = row[mapping_data['antibiotic_name_col']]
                    result = row[mapping_data['antibiotic_result_col']]
                    dataset.loc[index, antibiotic_name] = result

                request.session['dataset'] = dataset.to_json()

            return render(request, 'main_results.html')
    return redirect('upload_dataset')

def validate_file_format(file):
    """Validate CSV file format using extension, MIME type, and content inspection"""
    errors = []
    
    # 1. Check File Extension
    if not file.name.lower().endswith('.csv'):
        errors.append("Invalid file extension. Only .csv files are supported")
    
    # 2. Verify MIME Type
    valid_mime_types = ['text/csv']
    
    # First try Django's built-in MIME type detection
    mime_type = getattr(file, 'content_type', mimetypes.guess_type(file.name)[0])
    
    # If not reliable, use python-magic for more accurate detection
    if mime_type not in valid_mime_types:
        file.seek(0)
        mime_type = magic.from_buffer(file.read(1024), mime=True)
        file.seek(0)
    
    if mime_type not in valid_mime_types:
        errors.append(f"Invalid MIME type: {mime_type}. Only text/csv is supported")
    
    # Inspect File Content
    try:
        file.seek(0)
        # Check if it's a valid CSV
        sample = file.read(1024).decode('utf-8')
        file.seek(0)
        if not any(char in sample for char in [',', ';', '\t']):
            errors.append("File content doesn't appear to be valid CSV")
    except Exception as e:
        errors.append(f"Error reading file content: {str(e)}")
    
    return errors

def validate_dataset(dataset, mapping_data, file=None):
    """Perform comprehensive validation checks on the dataset"""
    errors = []
    
    # File Format Validation
    if file:
        format_errors = validate_file_format(file)
        errors.extend(format_errors)
    
    # Dataset Structure Validation
    
    if len(dataset.columns) == 0:
        errors.append("Dataset has no columns - invalid format")
    elif len(dataset) == 0:
        errors.append("Dataset is empty - invalid format")
    
    # Duplicate Records Check
    if dataset.duplicated().any():
        errors.append("Duplicate records found in the dataset")
    
    # Date Validity Check
    if 'date_column' in mapping_data:
        try:
            dates = pd.to_datetime(dataset[mapping_data['date_column']])
            if (dates.dt.year > pd.Timestamp.now().year).any():
                errors.append("Future dates found in the dataset")
        except:
            errors.append("Invalid date format in date column")
    
    return errors

def dataset_upload(request):
    file = request.FILES['csv_file']
    
    # First validate file format
    format_errors = validate_file_format(file)
    if format_errors:
        for error in format_errors:
            messages.error(request, error)
        return redirect('upload_dataset')
    
    # Then proceed with reading the file
    try:
        dataset = pd.read_csv(file)
        
        # Additional validation by checking if we can access basic file properties
        if len(dataset.columns) == 0 or len(dataset) == 0:
            messages.error(request, "The file appears to be corrupted or empty")
            return redirect('upload_dataset')
            
        # Try to perform basic operations
        try:
            dataset.head()
            dataset.columns
            dataset.dtypes
        except Exception as e:
            messages.error(request, f"File corruption detected: {str(e)}")
            return redirect('upload_dataset')
            
    except pd.errors.EmptyDataError:
        messages.error(request, "The file appears to be empty")
        return redirect('upload_dataset')
    except pd.errors.ParserError:
        messages.error(request, "The file could not be parsed - it may be corrupted")
        return redirect('upload_dataset')
    except UnicodeDecodeError:
        messages.error(request, "The file encoding appears to be invalid")
        return redirect('upload_dataset')
    except Exception as e:
        messages.error(request, f"Error reading file: {str(e)}")
        return redirect('upload_dataset')
    
    # Store dataset in session
    request.session['dataset'] = dataset.to_json()
    
    columns = dataset.columns.tolist()
    return render(request, 'dataset_mapping.html', {'columns': columns})

def isolation_burden_analysis(request):
    dataset_json = request.session.get('dataset')
    mapping_data = request.session.get('mapping_data', {})
    
    if dataset_json:
        dataset = pd.read_json(dataset_json)
        
        # Get unique bacteria species
        bacteria_column = mapping_data.get('bacterial_infection')
        source_column = mapping_data.get('source_input')
        
        # Get unique values for each column
        bacteria_species = list(dataset[bacteria_column].unique())
        source_columns = list(dataset[source_column].unique())
        country_columns = list(dataset['Country'].unique()) if 'Country' in dataset.columns else []
        
        # Get all columns for cluster attribute and gender selection
        all_columns = dataset.columns.tolist()
        
        # Add 'All' options
        bacteria_species.insert(0, 'All Bacteria')
        source_columns.insert(0, 'All Sources')
        country_columns.insert(0, 'All Countries')
        all_columns.insert(0, 'None')

        return render(request, 'isolation_burden_analysis.html', {
            'bacteria_species': bacteria_species,
            'source_columns': source_columns,
            'country_columns': country_columns,
            'cluster_attributes': all_columns,
            'gender_columns': all_columns  # Add this for gender column selection
        })
    return redirect('upload_dataset')

def generate_isolation_graph(request):
    if request.method == 'POST':
        source = request.POST.get('source')
        country = request.POST.get('country')
        bacteria = request.POST.get('bacteria')
        cluster_attribute = request.POST.get('cluster_attribute')
        gender_column = request.POST.get('gender_column')  # Get selected gender column
        gender_filter = request.POST.get('gender_filter') == 'true'
        
        dataset_json = request.session.get('dataset')
        mappings = request.session.get('mapping_data')
        
        if dataset_json:
            dataset = pd.read_json(dataset_json)
            
            if bacteria != 'All Bacteria':
                dataset = dataset[dataset[mappings['bacterial_infection']] == bacteria]
            
            fig = isolation_burden_analysis_graph(
                dataset, 
                source, 
                country,
                cluster_attribute,
                gender_filter,
                gender_column,  # Pass gender column to analysis function
                mappings
            )
            
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
    mapping_data = request.session.get('mapping_data', {})
    if dataset_json:
        dataset = pd.read_json(dataset_json)
        columns = dataset.columns.tolist()

        return render(request, 'resistance_analysis.html', {
            'infection_columns': dataset[mapping_data['bacterial_infection']].unique(),
            'source_columns': dataset[mapping_data['source_input']].unique(),
            'antibiotic_columns': request.session['antibiotic_columns'],
            'columns': columns
        })
    return redirect('upload_dataset')

def generate_resistance_graph(request):
    if request.method == 'POST':
        source = request.POST.get('source')
        infection = request.POST.get('infection')
        antibiotic = request.POST.get('antibiotic')
        
        # Get dataset and mappings from session
        dataset_json = request.session.get('dataset')
        mappings = request.session.get('mapping_data', {})
        
        if dataset_json:
            dataset = pd.read_json(dataset_json)
            
            fig = resistance_analysis_graph(dataset, source, infection, antibiotic, mappings)
            
            # Convert plot to image
            buffer = BytesIO()
            fig.savefig(buffer, format='png', bbox_inches='tight', transparent=True)
            buffer.seek(0)
            plt.close(fig)
            
            return HttpResponse(buffer.getvalue(), content_type='image/png')
            
    return HttpResponse('Invalid request', status=400)

def scorecards(request):
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
        return render(request, 'scorecard_analysis.html', {
            'infection_columns': infection_columns, 
            'source_columns': source_columns, 
            'antibiotic_columns': antibiotic_columns, 
            'columns': columns
        })
    return redirect('upload_dataset')


def generate_scorecard_graph(request):
    pass
    

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

def generate_scorecards(request):
    if request.method == 'POST':
        source = request.POST.get('source')
        infection = request.POST.get('infection')
        antibiotic = request.POST.get('antibiotic')

        print(f"Generating scorecards for: {source}, {infection}, {antibiotic}")

        dataset = pd.read_json(request.session['dataset'])

        figures = scorecard_analysis(
            dataset,
            source,
            infection,
            antibiotic,
            request.session['mapping_data']
        )
        
        pngs = []
        for fig in figures:
            buffer = BytesIO()
            fig.savefig(buffer, format='png', bbox_inches='tight', transparent=True)
            buffer.seek(0)
            image = base64.b64encode(buffer.getvalue()).decode('utf-8')
            pngs.append(image)
            plt.close(fig)

        return JsonResponse({'pngs': pngs})