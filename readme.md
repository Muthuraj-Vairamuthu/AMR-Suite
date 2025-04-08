# AMR Suite User Guide & Documentation

## Table of Contents
1. [Overview](#overview)
2. [Workflow Steps](#workflow-steps)
    - [Upload Dataset](#1-upload-dataset)
    - [Dataset Mapping](#2-dataset-mapping)
    - [Dataset Checks](#3-dataset-checks)
    - [Results Page](#4-results-page)
    - [Isolation Burden Analysis](#5-isolation-burden-analysis)
    - [Resistance Analysis](#6-resistance-analysis)
    - [Scorecards](#7-scorecards)
3. [Common Errors and Resolutions](#common-errors-and-resolutions)
4. [Technical Notes](#technical-notes)

---

## Overview

The AMR Suite is a web-based application designed to analyze antimicrobial resistance (AMR) data. It is an end to end tool to analayse isolation burden and resistance patterns. It also features and intutitve scorecard feature.

---

## Workflow Steps

### 1. Upload Dataset

#### How to Use
- Navigate to the **Upload Dataset** page.
- Drag and drop your `.csv` file into the designated area or click the **Browse** button to select a file from your computer.
- Click the **Upload Dataset** button to proceed.

#### What Happens Internally
- The uploaded file is validated for:
  - File format (must be `.csv`).
  - MIME type (ensures the file is a valid CSV).
  - Content structure (checks for valid delimiters like commas, tabs, or semicolons).
- If the file passes validation, it is stored in the session for further processing.

---

### 2. Dataset Mapping

#### How to Use
- After uploading the dataset, you will be redirected to the **Dataset Mapping** page.
- Fill in the required fields:
  - **Dataset Format**: Choose between Wide or Long.
  - **Bacterial Infection**: Select the column representing bacterial infections.
  - **Source Input**: Select the column representing the source of the data.
  - **Antibiotic Details**:
    - For **Wide format**: Specify the suffix used in antibiotic column names. Wide format data organizes each subject in a single row, with different variables (e.g., antibiotic results) in separate columns.
    - For **Long format**: Select the columns for antibiotic names and results. Long format data organizes each observation in a separate row, often with repeated rows for the same subject and a column indicating the variable type.
  - **Date Details**: Specify the date column, format, and granularity (yearly, monthly, or daily).
  - **Clustering Details**: Select the column for clustering attributes and the time stamp granularity.
- Click **Process Dataset** to save the mappings.

#### What Happens Internally
- The mapping data is stored in the session for subsequent steps.
- For Wide format, antibiotic columns are identified based on the provided suffix.
- For Long format, antibiotic results are mapped to their respective names.

---

### 3. Dataset Checks

#### How to Use
- After mapping, the system automatically validates the dataset for:
  - Structural integrity (e.g., presence of columns, non-empty rows).
  - Duplicate records.
  - Valid date formats in the specified date column.
  - Future dates (if any).

#### What Happens Internally
- The system performs comprehensive checks:
  - Ensures the dataset has valid columns and rows.
  - Checks for duplicate records.
  - Validates the date column against the specified format.
- Errors are displayed on the **Results Page** if any issues are detected.

---

### 4. Results Page

#### How to Use
- After dataset checks, you will be redirected to the **Results Page**.
- Choose one of the available analysis options:
  - **Isolation Burden Analysis**
  - **Resistance Analysis**
  - **Scorecards**
- Click the corresponding button to proceed with the selected analysis.

#### What Happens Internally
- The system uses the mapped dataset and performs the selected analysis.
- Results are visualized as interactive graphs or scorecards.

---

### 5. Isolation Burden Analysis

#### How to Use
- Select **Isolation Burden Analysis** from the **Results Page**.
- Specify the following filters:
  - **Source**: Select a specific source/sample_type or choose "All Sources."
  - **Country**: Select a specific country or choose "All Countries."
  - **Cluster Attribute**: Choose a column for grouping data such as Age Group.
  - **Gender Filter**: Enable or disable gender-based filtering.
- Click **Generate Graph** to view the analysis.

#### What Happens Internally
- The system filters the dataset based on the selected criteria.
- Data is grouped by the specified cluster attribute and gender (if enabled).
- A graph is generated to visualize isolation rates across the selected dimensions.

---

### 6. Resistance Analysis

#### How to Use
- Select **Resistance Analysis** from the **Results Page**.
- Choose the required filters:
  - **Infection**: Bacterial species (e.g., *Klebsiella pneumoniae*).
  - **Antibiotic**: Select the antibiotic (e.g., *Amikacin_I*).
  - **Source**: Sample source (e.g., *Nails*).
- Click **Generate** to view the resistance trends.

#### What Happens Internally
- The dataset is filtered based on the selected infection, antibiotic, and source.
- Dates are parsed using the specified format and grouped by the chosen granularity (`yearly`, `monthly`, or `daily`).
- The resistance rate is computed as:  
  **Resistance Rate = (Resistant / Total) × 100**

#### Confidence Intervals
- The system uses **bootstrapping** (1000 samples) to compute a **95% confidence interval (CI)** for each resistance rate.
- CIs are clipped between 0–100% to ensure clean visualization.

#### Visualization
- A line graph displays resistance rates over time, with shaded regions representing the confidence intervals.
- Continuous lines show non-zero resistance periods, while standalone gray markers denote zero-resistance points.
- The plot follows a dark theme with white gridlines for readability.

---

## Common Errors and Resolutions

1. **File Not Uploaded**
    - **Error**: "No file chosen."
    - **Cause**: No file was selected for upload.
    - **Resolution**: Ensure you select a `.csv` file before clicking the **Upload Dataset** button.

2. **Invalid File Format**
    - **Error**: "Invalid file extension. Only `.csv` files are supported."
    - **Cause**: The uploaded file is not a `.csv` file.
    - **Resolution**: Upload a valid `.csv` file.

3. **Empty File**
    - **Error**: "The file appears to be empty."
    - **Cause**: The uploaded file has no data.
    - **Resolution**: Verify the file content and re-upload.

4. **Corrupted File**
    - **Error**: "The file could not be parsed - it may be corrupted."
    - **Cause**: The file contains invalid or unreadable data.
    - **Resolution**: Check the file for corruption and ensure it is a valid CSV.

5. **Missing Columns**
    - **Error**: "Dataset has no columns - invalid format."
    - **Cause**: The file does not contain column headers.
    - **Resolution**: Ensure the file includes column headers and re-upload.

6. **Invalid Date Format**
    - **Error**: "Invalid date format in date column."
    - **Cause**: The date column does not match the specified format.
    - **Resolution**: Verify the date format in the dataset and update the mapping accordingly.

7. **Future Dates**
    - **Error**: "Future dates found in the dataset."
    - **Cause**: The date column contains dates beyond the current year.
    - **Resolution**: Correct the date values in the dataset.

---

## Technical Notes

- **Session Management**: The application uses Django sessions to store uploaded datasets and mapping configurations.
- **Validation**: File validation is performed using MIME type detection and content inspection.
- **Graph Generation**: Graphs are generated using Matplotlib with a dark theme for better visualization.
- **Error Handling**: Errors are displayed as messages on the respective pages, guiding users to resolve issues.

---

