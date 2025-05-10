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
import magic
import io
import base64
from django.conf import settings
import os
import re
import zipfile
import logging
from datetime import datetime
import traceback
from logging.handlers import RotatingFileHandler
import subprocess

# Configure logging with rotation
log_file_path = os.path.join(settings.BASE_DIR, 'audit.log')
handler = RotatingFileHandler(
    log_file_path,
    maxBytes=10 * 1024 * 1024,  # 10 MB
    backupCount=5  # Keep up to 5 backup files
)
handler.setFormatter(logging.Formatter('[%(asctime)s] [%(event_type)s] [user:%(user)s] %(message)s'))

logger = logging.getLogger('audit_logger')
logger.setLevel(logging.INFO)
logger.addHandler(handler)

def log_event(event_type, user, description, details_dict=None):
    """
    Logs an event in both human-readable and machine-readable formats.
    
    Args:
        event_type (str): The type of event (e.g., UPLOAD, VALIDATE, MAP).
        user (str): The username or session ID of the user.
        description (str): A human-readable description of the event.
        details_dict (dict, optional): Additional details for machine-readable logging.
    """
    # Human-readable log
    logger.info(
        f"{description}",
        extra={'event_type': event_type, 'user': user}
    )
    
    # Machine-readable log (JSON)
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "event_type": event_type,
        "user": user,
        "description": description,
        "details": details_dict or {}
    }
    
    with open(os.path.join(settings.BASE_DIR, 'audit.json'), 'a') as f:
        f.write(json.dumps(log_entry) + '\n')

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
            log_event(
                event_type="LOGIN",
                user=username,
                description="User logged in successfully."
            )
            return redirect('upload_dataset/')
        else:
            log_event(
                event_type="LOGIN_FAILED",
                user=username,
                description="Failed login attempt."
            )
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
        username = request.user.username
        log_event(
            event_type="LOGOUT",
            user=username,
            description="User logged out."
        )
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
    user = request.user.username if request.user.is_authenticated else 'anonymous'
    
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
        'resistance_granularity': request.POST.get('resistance_granularity'),
        'time_gap_attribute': request.POST.get('time_gap_attribute'),
    }
    
    # Log mapping
    log_event(
        event_type="MAP",
        user=user,
        description=f"Mapped columns: {mapping_data}",
        details_dict=mapping_data
    )
    
    # Validate required fields
    required_fields = ['bacterial_infection', 'source_input', 'dataset_format', 'date_column', 'date_format']
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
    
    # Log processing
    log_event(
        event_type="PROCESS",
        user=user,
        description=f"Dataset processed into {mapping_data['dataset_format']} format (records: {len(dataset)})",
        details_dict={"record_count": len(dataset), "format": mapping_data['dataset_format']}
    )
    
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
    
    # If not reliable, use python-magic for more accurate detection
    if mime_type not in valid_mime_types:
        file.seek(0)
        mime_type = magic.from_buffer(file.read(1024), mime=True)
        file.seek(0)
    
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
    if 'csv_file' not in request.FILES:
        messages.error(request, "No file uploaded. Please select a CSV file.")
        return redirect('upload_dataset')
    
    file = request.FILES['csv_file']
    user = request.user.username if request.user.is_authenticated else 'anonymous'
    
    # Log upload
    log_event(
        event_type="UPLOAD",
        user=user,
        description=f"Uploaded file: {file.name} (size: {file.size} bytes)",
        details_dict={"file_name": file.name, "file_size": file.size}
    )
    
    # First validate file format
    format_errors = validate_file_format(file)
    if format_errors:
        for error in format_errors:
            messages.error(request, error)
        # Log validation failure
        log_event(
            event_type="VALIDATE",
            user=user,
            description=f"File validation failed: {', '.join(format_errors)}",
            details_dict={"errors": format_errors}
        )
        return redirect('upload_dataset')
    
    # Log validation success
    log_event(
        event_type="VALIDATE",
        user=user,
        description="File passed format and structure validation."
    )
    
    # Then proceed with reading the file
    try:
        dataset = pd.read_csv(file)
        
        # Log parsing
        log_event(
            event_type="PARSE",
            user=user,
            description=f"CSV parsed into DataFrame (rows: {len(dataset)}, columns: {len(dataset.columns)})",
            details_dict={"row_count": len(dataset), "column_count": len(dataset.columns)}
        )
        
        # Additional validation by checking if we can access basic file properties
        if len(dataset.columns) == 0:
            messages.error(request, "The file has no columns. Ensure the file contains valid data.")
            return redirect('upload_dataset')
        if len(dataset) == 0:
            messages.error(request, "The file is empty. Ensure the file contains valid data.")
            return redirect('upload_dataset')
            
        # Try to perform basic operations
        try:
            dataset.head()
            dataset.columns
            dataset.dtypes
        except Exception as e:
            messages.error(request, f"File corruption detected: {str(e)}. The file may be improperly formatted.")
            return redirect('upload_dataset')
            
    except pd.errors.EmptyDataError as e:
        user = request.user.username if request.user.is_authenticated else 'anonymous'
        log_event(
            event_type="ERROR",
            user=user,
            description=f"EmptyDataError: {str(e)}",
            details_dict={"exception": str(e), "stack_trace": traceback.format_exc()}
        )
        messages.error(request, "The file appears to be empty. Ensure the file contains valid data.")
        return redirect('upload_dataset')
    except pd.errors.ParserError as e:
        user = request.user.username if request.user.is_authenticated else 'anonymous'
        log_event(
            event_type="ERROR",
            user=user,
            description=f"ParserError: {str(e)}",
            details_dict={"exception": str(e), "stack_trace": traceback.format_exc()}
        )
        messages.error(request, "The file could not be parsed. It may be corrupted or improperly formatted.")
        return redirect('upload_dataset')
    except UnicodeDecodeError as e:
        user = request.user.username if request.user.is_authenticated else 'anonymous'
        log_event(
            event_type="ERROR",
            user=user,
            description=f"UnicodeDecodeError: {str(e)}",
            details_dict={"exception": str(e), "stack_trace": traceback.format_exc()}
        )
        messages.error(request, "The file encoding appears to be invalid. Ensure the file is encoded in UTF-8.")
        return redirect('upload_dataset')
    except Exception as e:
        user = request.user.username if request.user.is_authenticated else 'anonymous'
        log_event(
            event_type="ERROR",
            user=user,
            description=f"Unexpected error: {str(e)}",
            details_dict={"exception": str(e), "stack_trace": traceback.format_exc()}
        )
        messages.error(request, f"Error reading file: {str(e)}. The file may be corrupted or improperly formatted.")
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
        gender_column = request.POST.get('gender_column')
        gender_filter = request.POST.get('gender_filter') == 'true'
        user = request.user.username if request.user.is_authenticated else 'anonymous'
        
        # Log isolation analysis
        log_event(
            event_type="ISOLATION_ANALYSIS",
            user=user,
            description=f"Filters used: Source={source}, Country={country}, Bacteria={bacteria}, Cluster={cluster_attribute}",
            details_dict={"source": source, "country": country, "bacteria": bacteria, "cluster": cluster_attribute}
        )
        
        dataset_json = request.session.get('dataset')
        mappings = request.session.get('mapping_data')
        
        if dataset_json:
            dataset = pd.read_json(dataset_json)
            
            fig = isolation_burden_analysis_graph(
                dataset, 
                source, 
                country,
                cluster_attribute,
                gender_filter,
                gender_column,
                mappings
            )
            
            # Convert plot to image
            buffer = BytesIO()
            fig.savefig(buffer, format='png', bbox_inches='tight', transparent=True)
            buffer.seek(0)
            plt.close(fig)
            
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
        user = request.user.username if request.user.is_authenticated else 'anonymous'
        
        # Log resistance analysis
        log_event(
            event_type="RESISTANCE_ANALYSIS",
            user=user,
            description=f"Filters used: Infection={infection}, Antibiotic={antibiotic}, Source={source}",
            details_dict={"infection": infection, "antibiotic": antibiotic, "source": source}
        )
        
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
        user = request.user.username if request.user.is_authenticated else 'anonymous'
        
        # Log scorecard generation
        log_event(
            event_type="SCORECARD_GENERATED",
            user=user,
            description=f"Scorecard generated for: Infection={infection}, Antibiotic={antibiotic}, Source={source}",
            details_dict={"infection": infection, "antibiotic": antibiotic, "source": source}
        )
        
        # Get dataset and mappings from session
        dataset_json = request.session.get('dataset')
        mappings = request.session.get('mapping_data', {})
        
        if dataset_json:
            dataset = pd.read_json(dataset_json)
            
            # Call the scorecard_analysis function
            figures, visualization_data = scorecard_analysis(
                dataset,
                source,
                infection,
                antibiotic,
                mappings
            )
            
            if visualization_data is None:
                return JsonResponse({'error': 'Visualization data could not be found due to insufficient data.'}, status=500)
            
            return JsonResponse(visualization_data)
            
    return JsonResponse({'error': 'Invalid request'}, status=400)

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
        anonymize = 'anonymize' in request.POST
        generate_plots = 'generate_plots' in request.POST

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

def check_file_format(request):
    dataset_json = request.session.get('dataset')
    if not dataset_json:
        return JsonResponse({'success': False, 'error': 'No dataset in session'})
    
    # Perform file format validation
    dataset = pd.read_json(dataset_json)
    if not isinstance(dataset, pd.DataFrame):
        return JsonResponse({'success': False, 'error': 'Invalid dataset format'})
    
    return JsonResponse({'success': True})

def check_file_content(request):
    dataset_json = request.session.get('dataset')
    if not dataset_json:
        return JsonResponse({'success': False, 'error': 'No dataset in session'})
    
    # Perform file content validation
    dataset = pd.read_json(dataset_json)
    if dataset.empty:
        return JsonResponse({'success': False, 'error': 'Dataset is empty'})
    
    return JsonResponse({'success': True})

def check_dataset_structure(request):
    dataset_json = request.session.get('dataset')
    if not dataset_json:
        return JsonResponse({'success': False, 'error': 'No dataset in session'})
    
    # Perform dataset structure validation
    dataset = pd.read_json(dataset_json)
    if len(dataset.columns) == 0:
        return JsonResponse({'success': False, 'error': 'Dataset has no columns'})
    
    return JsonResponse({'success': True})

def check_mapping(request):
    dataset_json = request.session.get('dataset')
    if not dataset_json:
        return JsonResponse({'success': False, 'error': 'No dataset in session'})
    
    # Perform mapping validation
    dataset = pd.read_json(dataset_json)
    if 'mapping_data' not in request.session:
        return JsonResponse({'success': False, 'error': 'No mapping data found'})
    
    return JsonResponse({'success': True})

def update_system_settings(request):
    if request.method == 'POST':
        # Update system settings
        user = request.user.username if request.user.is_authenticated else 'anonymous'
        log_event(
            event_type="CONFIG_CHANGE",
            user=user,
            description="System settings updated.",
            details_dict={"settings": request.POST}
        )
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

def deploy_new_version(request):
    if request.method == 'POST':
        # Deploy new version
        user = request.user.username if request.user.is_authenticated else 'anonymous'
        log_event(
            event_type="VERSION_DEPLOYED",
            user=user,
            description="New version deployed.",
            details_dict={"version": request.POST.get('version')}
        )
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)



