
# Dataset Processing Pipeline Overview

## Pipeline Overview

The pipeline consists of the following steps:

- **Upload Dataset**: User uploads a CSV file.
- **Validate File Format**: Check if the file is a valid CSV.
- **Parse Dataset**: Read the CSV file into a Pandas DataFrame.
- **Validate Dataset Content**: Ensure the dataset is not empty and has valid structure.
- **Store Dataset in Session**: Save the dataset in the user’s session for further processing.
- **Map Dataset Columns**: Allow the user to map dataset columns to specific fields (e.g., bacterial infection, source input, etc.).
- **Process Dataset**: Transform the dataset based on the mappings and perform further analysis.

## Step-by-Step Execution

### 1. Upload Dataset

**Code Executed**: `dataset_upload` view in `backend/api/views.py`.

**How It Works**:
- The user uploads a CSV file via the form in `upload_dataset.html`.
- The file is sent to the `dataset_upload` view via a POST request.
- The file is validated using the `validate_file_format` function.
- If valid, it's read into a Pandas DataFrame.

**Real-Time & Robust**:
- File format is validated immediately after upload.
- Errors (e.g., invalid file type, empty file) are displayed in real-time.

### 2. Validate File Format

**Code Executed**: `validate_file_format` function in `backend/api/views.py`.

**How It Works**:
- The file extension, MIME type, and content are checked to ensure it’s a valid CSV.
- Errors are returned if the file is invalid.

**Real-Time & Robust**:
- Immediate validation after upload.
- Multiple aspects of the file are checked.

### 3. Parse Dataset

**Code Executed**: `dataset_upload` view in `backend/api/views.py`.

**How It Works**:
- CSV is read into a DataFrame using `pd.read_csv`.
- Basic checks (e.g., `head`, `columns`, `dtypes`) ensure file integrity.

**Real-Time & Robust**:
- Parsing occurs immediately after validation.
- Errors are caught and displayed.

### 4. Validate Dataset Content

**Code Executed**: `dataset_upload` view in `backend/api/views.py`.

**How It Works**:
- Checks for non-empty dataset and valid structure.

**Real-Time & Robust**:
- Validation follows parsing.
- Common issues (e.g., empty columns, duplicates) are flagged.

### 5. Store Dataset in Session

**Code Executed**: `dataset_upload` view in `backend/api/views.py`.

**How It Works**:
- DataFrame is converted to JSON and stored in `request.session['dataset']`.
- Column names passed to `dataset_mapping.html` for mapping.

**Real-Time & Robust**:
- Session storage ensures dataset availability.

### 6. Map Dataset Columns

**Code Executed**: `mapping_dataset` view in `backend/api/views.py`.

**How It Works**:
- Users map columns to fields via `dataset_mapping.html` form.
- Mappings are stored in `request.session['mapping_data']`.
- Dataset is transformed accordingly.

**Real-Time & Robust**:
- Mappings validated immediately.
- Errors (e.g., missing fields) shown in real-time.

### 7. Process Dataset

**Code Executed**: `mapping_dataset` view in `backend/api/views.py`.

**How It Works**:
- Dataset transformed based on mappings.
- Stored in session and saved as `static/media/original_dataset.csv`.
- Redirect to `main_results.html` for analysis.

**Real-Time & Robust**:
- Immediate transformation.
- Dataset validated and processed reliably.

## Real-Time Checks

**Code Executed**: `checkValidationStatus` function in `main_results.html`.

**How It Works**:
- API calls to validate file format, content, structure, and mappings.
- UI updated with ✓ or ✗ based on validation results.

**Real-Time & Robust**:
- Sequential checks update UI in real-time.
- Immediate error feedback halts further checks.

## Robustness

### Validation
- Multi-step validation (format, content, structure, mappings).

### Error Handling
- Real-time error capture and display.

### Session Management
- Session retains dataset and mappings across steps.

## What Else is Required?

### Error Handling
- More detailed error messages for clarity.

### Logging
- Log validation results and errors.

### Performance Optimization
- Chunking and async processing for large files.

### User Feedback
- Progress indicators for time-consuming tasks.

### Security
- Sanitize inputs to avoid exploits (e.g., SQL injection, file attacks).

## Summary

The pipeline is real-time and robust, with validations and transformations at every step. It handles errors well and provides immediate feedback. Future enhancements like logging, performance optimization, and improved security can make it even stronger.
