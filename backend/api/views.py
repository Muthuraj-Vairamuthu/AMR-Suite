from django.shortcuts import render, redirect
from rest_framework.views import APIView
from . models import *
from rest_framework.response import Response
from django.http import HttpResponse, JsonResponse, FileResponse
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
import io
import base64
from django.conf import settings
import traceback
import os
import re
import zipfile
from AMR_Suite.utils import log_event
from .utils.validators import DatasetValidator
import json

def home(request):
    """Renders the main home page"""
    return render(request, 'home.html')

def home2(request):
    return render(request,'home2.html')
def scorecard_info(request):
    return render(request, 'scorecard_info.html') 
def video(request):
    return render(request, 'video.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        user = authenticate(request, username=username, 
                          password=request.POST.get('password'))
        
        if user is not None:
            login(request, user)
            log_event('LOGIN', username, f"User logged in successfully")
            return redirect('upload_dataset')
        else:
            log_event('LOGIN_FAILED', username, "Invalid login attempt")
            messages.error(request, 'Invalid username or password.')
            
    return render(request, 'login.html')

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
        username = request.user.username
        log_event('LOGOUT', username, "User logged out")
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
    if request.method != 'POST':
        messages.error(request, "Invalid request method. Please submit the mapping form.")
        return redirect('upload_dataset')
    
    dataset_json = request.session.get('dataset')
    if not dataset_json:
        messages.error(request, "No dataset found in session. Please upload a dataset first.")
        return redirect('upload_dataset')
    
    dataset = pd.read_json(dataset_json)
    
    mapping_data = {
        'isolate_id': request.POST.get('isolate_id'),  # Add this line
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
        'resistance_granularity': request.POST.get('resistance_granularity'),
        'time_gap_attribute': request.POST.get('time_gap_attribute'),
    }
    
    # Validate required fields
    required_fields = ['isolate_id', 'bacterial_infection', 'source_input', 'dataset_format', 'date_column', 'date_format']
    for field in required_fields:
        if not mapping_data[field]:
            messages.error(request, f"Required field '{field.replace('_', ' ')}' is missing. Please fill in all required fields.")
            return redirect('upload_dataset')
    
    # Store mappings in session
    request.session['mapping_data'] = mapping_data
    
    # Transform dataset based on mappings
    try:
        if mapping_data['dataset_format'] == 'Wide':
            suffix = mapping_data['antibiotic_format'].replace('Antibiotic', '')
            antibiotic_columns = [col for col in dataset.columns if col.endswith(suffix)]
            if not antibiotic_columns:
                messages.error(request, f"No columns found with suffix '{suffix}'. Ensure the antibiotic format is correct.")
                return redirect('upload_dataset')
            request.session['antibiotic_columns'] = antibiotic_columns
        else:
            antibiotic_columns = dataset[mapping_data['antibiotic_name_col']].unique().tolist()
            request.session['antibiotic_columns'] = antibiotic_columns
    except Exception as e:
        messages.error(request, f"Error processing dataset: {str(e)}. Please check your mappings and try again.")
        return redirect('upload_dataset')
    
    # Update the dataset in the session
    request.session['dataset'] = dataset.to_json()
    dataset.to_csv('static/media/original_dataset.csv', index=False)
    
    return render(request, 'main_results.html')


def validate_file_format(file):
    """Validate CSV file format using extension, MIME type, and content inspection"""
    errors = []
    
    # 1. Check File Extension
    if not file.name.lower().endswith('.csv'):
        errors.append("Invalid file extension. Only .csv files are supported.")
    
    # 2. Verify MIME Type
    valid_mime_types = ['text/csv']
    
    # First try Django's built-in MIME type detection
    mime_type = getattr(file, 'content_type', mimetypes.guess_type(file.name)[0])
        
    if mime_type not in valid_mime_types:
        errors.append(f"Invalid MIME type: {mime_type}. Only text/csv is supported.")
    
    # 3. Inspect File Content
    try:
        file.seek(0)
        # Check if it's a valid CSV
        sample = file.read(1024).decode('utf-8')
        file.seek(0)
        if not any(char in sample for char in [',', ';', '\t']):
            errors.append("File content doesn't appear to be valid CSV. Ensure the file uses commas, semicolons, or tabs as delimiters.")
    except Exception as e:
        errors.append(f"Error reading file content: {str(e)}. The file may be corrupted or encoded incorrectly.")
    
    return errors

def dataset_upload(request):
    if 'csv_file' not in request.FILES:
        log_event('ERROR', request.user.username, "No file uploaded")
        messages.error(request, "No file uploaded. Please select a CSV file.")
        return redirect('upload_dataset')
    
    file = request.FILES['csv_file']
    
    try:
        log_event('UPLOAD', request.user.username, f"Uploaded file: {file.name}", 
                 {'size': file.size, 'content_type': file.content_type})
        
        # Validate file format
        format_errors = validate_file_format(file)
        if format_errors:
            log_event('VALIDATE', request.user.username, "File validation failed", 
                     {'errors': format_errors})
            for error in format_errors:
                messages.error(request, error)
            return redirect('upload_dataset')
        
        log_event('VALIDATE', request.user.username, "File passed validation")
        
        # Read dataset
        dataset = pd.read_csv(file)
        log_event('PARSE', request.user.username, "CSV parsed into DataFrame",
                 {'rows': len(dataset), 'columns': len(dataset.columns)})
        
        # Store in session
        request.session['dataset'] = dataset.to_json()
        
        return render(request, 'dataset_mapping.html', {'columns': dataset.columns.tolist()})
        
    except Exception as e:
        log_event('ERROR', request.user.username, f"Error processing upload: {str(e)}", 
                 {'traceback': traceback.format_exc()})
        messages.error(request, f"Error processing file: {str(e)}")
        return redirect('upload_dataset')

def isolation_burden_analysis(request):
    log_event('ISOLATION_BURDEN_ANALYSIS', request.user.username, "Isolation burden analysis initiated")
    
    dataset_json = request.session.get('dataset')
    mapping_data = request.session.get('mapping_data', {})
    
    if dataset_json:
        try:
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
            
            log_event('ISOLATION_BURDEN_ANALYSIS', request.user.username, "Data prepared for isolation burden analysis", {
                'bacteria_species_count': len(bacteria_species),
                'source_columns_count': len(source_columns),
                'country_columns_count': len(country_columns),
                'all_columns_count': len(all_columns)
            })
            
            return render(request, 'isolation_burden_analysis.html', {
                'bacteria_species': bacteria_species,
                'source_columns': source_columns,
                'country_columns': country_columns,
                'cluster_attributes': all_columns,
                'gender_columns': all_columns  # Add this for gender column selection
            })
        except Exception as e:
            log_event('ERROR', request.user.username, f"Error in isolation burden analysis: {str(e)}", {
                'traceback': traceback.format_exc()
            })
            messages.error(request, "An error occurred while processing the dataset.")
            return redirect('upload_dataset')
    
    log_event('ISOLATION_BURDEN_ANALYSIS', request.user.username, "No dataset found in session")
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
    """Handles both GET and POST requests for resistance analysis"""
    if request.method == 'GET':
        dataset_json = request.session.get('dataset')
        if dataset_json:
            try:
                dataset = pd.read_json(dataset_json)
                mappings = request.session.get('mapping_data', {})
                
                # Get the correct column names from mappings
                bacteria_column = mappings.get('bacterial_infection')
                source_column = mappings.get('source_input')
                antibiotic_format = mappings.get('antibiotic_format', '')
                
                # Get unique values and handle None/empty values
                bacteria_species = []
                if bacteria_column and bacteria_column in dataset.columns:
                    bacteria_species = sorted(list(dataset[bacteria_column].dropna().unique()))
                    print(f"Found bacteria species: {bacteria_species}")  # Debug print
                
                source_columns = []
                if source_column and source_column in dataset.columns:
                    source_columns = sorted(list(dataset[source_column].dropna().unique()))
                
                # Get antibiotic columns based on format
                antibiotic_columns = []
                if antibiotic_format:
                    suffix = antibiotic_format.replace('Antibiotic', '')
                    antibiotic_columns = sorted([col for col in dataset.columns 
                                       if col.endswith(suffix)])
                
                log_event('RESISTANCE_ANALYSIS_PAGE', request.user.username, 
                         "Loading resistance analysis page", {
                             'bacteria_count': len(bacteria_species),
                             'sources_count': len(source_columns),
                             'antibiotics_count': len(antibiotic_columns)
                         })
                
                context = {
                    'bacteria_species': bacteria_species,
                    'source_columns': source_columns,
                    'antibiotic_columns': antibiotic_columns
                }
                
                return render(request, 'resistance_analysis.html', context)
                
            except Exception as e:
                log_event('ERROR', request.user.username, 
                         f"Error preparing resistance analysis page: {str(e)}", 
                         {'traceback': traceback.format_exc()})
                messages.error(request, f"Error preparing resistance analysis: {str(e)}")
                return redirect('upload_dataset')
                
        messages.error(request, "No dataset found. Please upload a dataset first.")
        return redirect('upload_dataset')
    
    if request.method == 'POST':
        filters = {
            'source': request.POST.get('source'),
            'infection': request.POST.get('infection'),
            'antibiotic': request.POST.get('antibiotic')
        }
        
        log_event('RESISTANCE_ANALYSIS', request.user.username, 
                 "Resistance analysis initiated", filters)
        
        try:
            # Your existing analysis code...
            results = {"message": "Analysis completed successfully"}
            log_event('ANALYSIS_COMPLETE', request.user.username, 
                     "Resistance analysis completed successfully")
            return JsonResponse(results)
        except Exception as e:
            log_event('ERROR', request.user.username, 
                     f"Error in resistance analysis: {str(e)}", 
                     {'traceback': traceback.format_exc()})
            return JsonResponse({'error': str(e)}, status=500)

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


def google_callback(request):
    if request.user.is_authenticated:
        log_event('GOOGLE_CALLBACK', request.user.username, "User already authenticated, redirecting to upload_dataset")
        return redirect('upload_dataset')
    
    try:
        strategy = load_strategy(request)
        backend = load_backend(strategy=strategy, name='google-oauth2', redirect_uri=None)
        
        if 'code' in request.GET:
            try:
                user = backend.complete(request=request)
                if user and user.is_active:
                    login(request, user)
                    log_event('GOOGLE_AUTH_SUCCESS', user.username, f"Successfully authenticated Google user: {user.email}")
                    messages.success(request, f'Welcome, {user.first_name}!')
                    return redirect('upload_dataset')
            except Exception as e:
                log_event('GOOGLE_AUTH_ERROR', 'UNKNOWN', f"Error completing Google authentication: {str(e)}", {'traceback': traceback.format_exc()})
                messages.error(request, f'Google authentication error: {str(e)}')
    except Exception as e:
        log_event('GOOGLE_CALLBACK_ERROR', 'UNKNOWN', f"Error in Google callback: {str(e)}", {'traceback': traceback.format_exc()})
        messages.error(request, 'An error occurred during Google authentication.')
    
    log_event('GOOGLE_CALLBACK_REDIRECT', 'UNKNOWN', "Redirecting to login page due to authentication failure")
    return redirect('login')

    
def generate_scorecards(request):
    if request.method == 'POST':
        source = request.POST.get('source')
        infection = request.POST.get('infection')
        antibiotic = request.POST.get('antibiotic')

        print(f"Generating scorecards for: {source}, {infection}, {antibiotic}")

        # First try to load the data from JSON files if they exist
        json_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'Scorecards JSONs',
            infection,
            source,
            antibiotic
        )
        
        print(f"Looking for scorecard JSONs in: {json_dir}")
        
        visualization_data = {
            'years': [],
            'countries': {}  # Use dict first for easier lookup, then convert to list
        }
        
        # Check if directory exists and contains JSON files
        if os.path.exists(json_dir):
            try:
                # Get all JSON files in the directory
                json_files = [f for f in os.listdir(json_dir) if f.endswith('_scorecard.json')]
                print(f"Found {len(json_files)} JSON files")
                
                # Process each JSON file
                for json_file in json_files:
                    try:
                        with open(os.path.join(json_dir, json_file), 'r') as f:
                            year_data = json.load(f)
                            print(f"Loaded JSON data for year: {year_data.get('year', 'unknown')}")
                            
                            # Add year data to visualization_data
                            visualization_data['years'].append(year_data)
                            
                            # Process each country in the year data
                            for country in year_data['countries']:
                                country_name = country['name']
                                
                                if country_name not in visualization_data['countries']:
                                    visualization_data['countries'][country_name] = {
                                        'name': country_name,
                                        'years': []
                                    }
                                
                                # Add this year's data to the country
                                visualization_data['countries'][country_name]['years'].append({
                                    'year': year_data['year'],
                                    'x': country['x'],
                                    'y': country['y'],
                                    'median_intercept': year_data['median_intercept'],
                                    'median_slope': year_data['median_slope']
                                })
                    except Exception as e:
                        print(f"Error processing JSON file {json_file}: {str(e)}")
                
                # If we loaded data successfully from JSON files, convert countries dict to list and return
                if visualization_data['years']:
                    visualization_data['countries'] = list(visualization_data['countries'].values())
                    print(f"Successfully processed JSON data: {len(visualization_data['years'])} years, {len(visualization_data['countries'])} countries")
                    return JsonResponse(visualization_data)
            except Exception as e:
                print(f"Error loading JSON files: {str(e)}")
        else:
            print(f"JSON directory does not exist: {json_dir}")
        
        # If we couldn't load from JSON files, proceed with generating from the dataset
        dataset = pd.read_json(request.session['dataset'])

        # Call the updated scorecard_analysis function that returns both figures and data
        figures, visualization_data = scorecard_analysis(
            dataset,
            source,
            infection,
            antibiotic,
            request.session['mapping_data']
        )

        if visualization_data is None:
            return JsonResponse({'error': 'Visualization data could not be found due to insufficient data.'}, status=500)
        
        # Now we can directly use the structured data returned from the analysis function
        print(f"Generated visualization data with {len(visualization_data['years'])} years and {len(visualization_data['countries'])} countries")
        return JsonResponse(visualization_data)

def get_unique_values(request):
    """API endpoint to get unique values from a dataset column"""
    column_name = request.GET.get('column')
    
    if not column_name:
        return JsonResponse({'error': 'Column name not provided'}, status=400)
    
    dataset_json = request.session.get('dataset')
    if not dataset_json:
        return JsonResponse({'error': 'No dataset in session'}, status=400)
    
    try:
        dataset = pd.read_json(dataset_json)
        if column_name not in dataset.columns:
            return JsonResponse({'error': f'Column {column_name} not found'}, status=404)
        
        unique_values = dataset[column_name].dropna().unique().tolist()
        # Convert all values to strings
        unique_values = [str(val) for val in unique_values if val is not None]
        
        return JsonResponse({'values': unique_values})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def get_columns_with_suffix(request):
    """API endpoint to get columns with a specific suffix and their unique values"""
    suffix = request.GET.get('suffix')
    
    if not suffix:
        return JsonResponse({'error': 'Suffix not provided'}, status=400)
    
    dataset_json = request.session.get('dataset')
    if not dataset_json:
        return JsonResponse({'error': 'No dataset in session'}, status=400)
    
    try:
        dataset = pd.read_json(dataset_json)
        columns_with_suffix = [col for col in dataset.columns if col.endswith(suffix)]
        
        if not columns_with_suffix:
            return JsonResponse({'error': f'No columns found with suffix {suffix}'}, status=404)
        
        # Get all unique values from these columns
        all_values = []
        for col in columns_with_suffix:
            values = dataset[col].dropna().unique().tolist()
            all_values.extend(values)
        
        # Get unique values and convert to strings
        unique_values = list(set([str(val) for val in all_values if val is not None]))
        
        return JsonResponse({'values': unique_values})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def synthetic_dataset_creation(request):
    """Renders the synthetic dataset creation page"""
    return render(request, 'synthetic_dataset_creation.html')

def generate_synthetic_dataset(request):
    if request.method == 'POST':
        input_file_path = 'static/media/original_dataset.csv'
        output_folder = 'Synthetic_Dataset_Files/'
        os.makedirs(output_folder, exist_ok=True)

        n_total = int(request.POST.get('n_total', 10000))
        preserve_proportions = request.POST.get('preserve_proportions', 'country_year')
        anonymize = 'anonymize' in request
        generate_plots = 'generate_plots' in request

        r_script_path = 'static/media/generate_synthetic_dataset.R'
        output_prefix = os.path.join(output_folder, 'synthetic_output')

        print(f"Generating synthetic dataset with n_total={n_total}, anonymize={anonymize}, plots={generate_plots}, preserve={preserve_proportions}")

        try:
            subprocess.run([
                'Rscript',
                r_script_path,
                input_file_path,
                output_prefix,
                str(n_total),
                str(anonymize).upper(),
                str(generate_plots).upper(),
                preserve_proportions
            ], check=True)

            # 📦 Return generated CSV for download
            csv_path = f"{output_prefix}.csv"
            pdf_path = f"{output_prefix}.pdf"
            zip_path = os.path.join("Synthetic_Dataset_Files", "synthetic_output_bundle.zip")

            # ✅ Create ZIP archive
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                if os.path.exists(csv_path):
                    zipf.write(csv_path, arcname='synthetic_data.csv')
                if os.path.exists(pdf_path):
                    zipf.write(pdf_path, arcname='synthetic_output.pdf')

                img_files = [img for img in os.listdir(output_folder) if img.endswith('.png')]
                for img in img_files:
                    zipf.write(os.path.join(output_folder, img), arcname=img)


            if os.path.exists(zip_path):
                return FileResponse(open(zip_path, 'rb'), as_attachment=True, filename='synthetic_output_bundle.zip')
            else:
                return HttpResponse("Error: ZIP file not found.", status=500)

        except subprocess.CalledProcessError as e:
            return HttpResponse(f"Error generating dataset: {str(e)}", status=500)

    return HttpResponse("Invalid request method.", status=405)

from io import StringIO

def validate_dataset(request):
    """Endpoint for real-time dataset validation"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)

    print("Starting dataset validation...")
    
    # Check if both dataset and mapping data exist in session
    dataset_json = request.session.get('dataset')
    mapping_data = request.session.get('mapping_data')
    
    print(f"Session data - Dataset: {'Present' if dataset_json else 'Missing'}, "
          f"Mapping: {'Present' if mapping_data else 'Missing'}")
    
    # Remove the problematic debug line and replace with simpler logging
    print("Session data:")
    print(f"Dataset present: {bool(dataset_json)}")
    print(f"Mapping data: {mapping_data}")
    
    if not dataset_json:
        return JsonResponse({
            'success': False,
            'error': 'No dataset found in session. Please upload a dataset first.'
        })
    
    if not mapping_data:
        return JsonResponse({
            'success': False,
            'error': 'No mapping data found. Please complete the dataset mapping first.'
        })

    try:
        # Convert JSON string to DataFrame
        try:
            dataset = pd.read_json(StringIO(dataset_json))
        except Exception as e:
            print(f"Error parsing dataset JSON: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'Error parsing dataset. Please try uploading again.'
            }, status=400)

        print(f"Dataset loaded successfully with {len(dataset)} rows and {len(dataset.columns)} columns")
        
        # Create validator instance
        validator = DatasetValidator(dataset=dataset, mapping_data=mapping_data)
        
        # Initialize results dictionary
        results = {
            'success': True,
            'errors': [],
            'warnings': [],
            'missing_data': {},
            'duplicates': 0,
            'steps': {
                'format': True,
                'structure': False,
                'missing_data': False,
                'duplicates': False
            }
        }
        
        # Run validations one by one with error handling
        try:
            # Structure validation
            print("Running structure validation...")
            structure_results = validator.validate_dataset_structure()
            results['errors'].extend(structure_results.get('errors', []))
            results['steps']['structure'] = len(structure_results.get('errors', [])) == 0
            
            # Missing data check
            print("Checking for missing data...")
            missing_data_results = validator.check_missing_data()
            results['warnings'].extend(missing_data_results.get('warnings', []))
            results['missing_data'] = missing_data_results.get('missing_data', {})
            results['steps']['missing_data'] = not any(
                pct > 20 for pct in results['missing_data'].values()
            )
            
            # Duplicates check
            print("Checking for duplicates...")
            duplicate_results = validator.check_duplicates()
            results['duplicates'] = duplicate_results.get('duplicates', 0)
            results['steps']['duplicates'] = results['duplicates'] == 0
            
            if results['duplicates'] > 0:
                results['warnings'].append(
                    f"Found {results['duplicates']} duplicate records"
                )
        
        except Exception as e:
            print(f"Error during validation steps: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': f'Error during validation: {str(e)}'
            }, status=500)
        
        # Update overall success status
        results['success'] = all([
            results['steps']['format'],
            results['steps']['structure'],
            results['steps']['missing_data'],
            results['steps']['duplicates']
        ])
        
        # Convert any numpy types to native Python types for JSON serialization
        results['missing_data'] = {k: float(v) for k, v in results['missing_data'].items()}
        
        print(f"Validation complete. Results: {results}")
        return JsonResponse(results)

    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }, status=500)



