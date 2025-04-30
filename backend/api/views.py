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
import os
import re


# Create your views here.
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
            
            # Get resistance value mappings
            susceptible_values = request.POST.getlist('susceptible_values')
            intermediate_values = request.POST.getlist('intermediate_values')
            resistant_values = request.POST.getlist('resistant_values')
            
            # Store mappings if provided
            if any([susceptible_values, intermediate_values, resistant_values]):
                mapping_data['resistance_mappings'] = {
                    'susceptible': susceptible_values,
                    'intermediate': intermediate_values,
                    'resistant': resistant_values
                }
            
            request.session['mapping_data'] = mapping_data

            if mapping_data['dataset_format'] == 'Wide':
                suffix = mapping_data['antibiotic_format'].replace('Antibiotic', '')
                antibiotic_columns = [col for col in dataset.columns if col.endswith(suffix)]
                antibiotic_columns = sorted(list(set(antibiotic_columns)))
                
                # Apply resistance mappings for Wide format
                if 'resistance_mappings' in mapping_data:
                    for col in antibiotic_columns:
                        # Apply mappings to each antibiotic column
                        for value in susceptible_values:
                            dataset.loc[dataset[col] == value, col] = 'Susceptible'
                        for value in intermediate_values:
                            dataset.loc[dataset[col] == value, col] = 'Intermediate'
                        for value in resistant_values:
                            dataset.loc[dataset[col] == value, col] = 'Resistant'

                request.session['antibiotic_columns'] = antibiotic_columns
            else:
                # For Long format
                result_col = mapping_data['antibiotic_result_col']
                
                # Apply resistance mappings before pivoting
                if 'resistance_mappings' in mapping_data:
                    # Apply mappings to the result column
                    for value in susceptible_values:
                        dataset.loc[dataset[result_col] == value, result_col] = 'Susceptible'
                    for value in intermediate_values:
                        dataset.loc[dataset[result_col] == value, result_col] = 'Intermediate'
                    for value in resistant_values:
                        dataset.loc[dataset[result_col] == value, result_col] = 'Resistant'
                
                # Get unique antibiotic names
                antibiotic_columns = dataset[mapping_data['antibiotic_name_col']].unique().tolist()
                request.session['antibiotic_columns'] = antibiotic_columns
                
                # Transform from long to wide format
                dataset[antibiotic_columns] = None
                for index, row in dataset.iterrows():
                    antibiotic_name = row[mapping_data['antibiotic_name_col']]
                    result = row[mapping_data['antibiotic_result_col']]
                    dataset.loc[index, antibiotic_name] = result

            # Update the dataset in the session
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
# def check_scorecard_data(request):
#     organism = request.GET.get('infection')
#     antibiotic_full = request.GET.get('antibiotic', '').strip()
#     antibiotic = antibiotic_full.split('_')[0]
#     source = request.GET.get('source')

#     if not all([organism, antibiotic, source]):
#         return JsonResponse({'error': 'Missing parameters'}, status=400)

    # try:
    #     base_path = os.path.join(settings.BASE_DIR, 'scorecards', organism, source)
    #     year_file = os.path.join(base_path, f'{antibiotic}_{organism}_year.json')
    #     snapshot_file = os.path.join(base_path, f'{antibiotic}_{organism}_countries.json')

    #     if os.path.exists(year_file):
    #         with open(year_file, 'r') as f:
    #             year_data = json.load(f)
    #         return JsonResponse({
    #             'mode': 'year_based',
    #             'data': year_data
    #         }, safe=False)

    #     elif os.path.exists(snapshot_file):
    #         with open(snapshot_file, 'r') as f:
    #             snapshot_data = json.load(f)

    #         points = []
    #         for country in snapshot_data:
    #             if country['years']:
    #                 latest_year = sorted(country['years'], key=lambda x: x['year'])[-1]
    #                 points.append({
    #                     'x': max(0, latest_year['x']),
    #                     'y': latest_year['y'],
    #                     'label': country['name']
    #                 })

    #         median_x = sorted([p['x'] for p in points])[len(points) // 2] if points else 0
    #         median_y = sorted([p['y'] for p in points])[len(points) // 2] if points else 0

    #         return JsonResponse({
    #             'mode': 'snapshot',
    #             'points': points,
    #             'medians': {'x': median_x, 'y': median_y}
    #         }, safe=False)

    #     else:
    #         return JsonResponse({'error': 'No scorecard data found for this selection'}, status=404)

    # except Exception as e:
    #     return JsonResponse({'error': str(e)}, status=500)

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

# def generate_scorecards(request):
#     if request.method == 'POST':
#         source = request.POST.get('source')
#         infection = request.POST.get('infection')
#         antibiotic = request.POST.get('antibiotic')

#         print(f"Generating scorecards for: {source}, {infection}, {antibiotic}")

#         dataset = pd.read_json(request.session['dataset'])

#         figures = scorecard_analysis(
#             dataset,
#             source,
#             infection,
#             antibiotic,
#             request.session['mapping_data']
#         )
        
#         pngs = []
#         for fig in figures:
#             buffer = BytesIO()
#             fig.savefig(buffer, format='png', bbox_inches='tight', transparent=True)
#             buffer.seek(0)
#             image = base64.b64encode(buffer.getvalue()).decode('utf-8')
#             pngs.append(image)
#             plt.close(fig)

#         return JsonResponse({'pngs': pngs})
    
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