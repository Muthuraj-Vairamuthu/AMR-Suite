# AMR Suite - User Guide & Documentation

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

**AMR Suite** is a web-based application built to analyze antimicrobial resistance (AMR) data. It provides an end-to-end pipeline to process, validate, and visualize AMR datasets. With features for **Isolation Burden Analysis**, **Resistance Analysis**, and **Scorecards**, it is designed to help researchers and public health analysts gain actionable insights through an intuitive interface.

---

## Workflow Steps

### 1. Upload Dataset

#### How to Use
- Go to the **Upload Dataset** page.
- Drag and drop your `.csv` file into the dropzone or use the **Browse** button to select it.
- Click **Upload Dataset** to continue.

#### What Happens Internally
- File is validated for:
  - Correct `.csv` extension.
  - Valid MIME type.
  - Valid delimiters (`,`, `;`, or tabs).
- If valid, the file is stored in the session for further processing.

---

### 2. Dataset Mapping

#### How to Use
- After upload, proceed to the **Dataset Mapping** page.
- Fill in these fields:
  - **Dataset Format**: Choose **Wide** or **Long**.
  - **Bacterial Infection**: Column with bacterial species.
  - **Source Input**: Column with sample source.
  - **Antibiotic Details**:
    - **Wide**: Provide suffix for antibiotic columns (e.g., `_I`, `_R`, `_S`).
    - **Long**: Select columns for antibiotic names and results.
  - **Date Details**:
    - Column name
    - Format (e.g., `YYYY-MM-DD`)
    - Granularity (`yearly`, `monthly`, `daily`)
  - **Clustering Details**:
    - Column used for clustering (e.g., Age Group)
    - Timestamp granularity
- Click **Process Dataset** to save.

#### What Happens Internally
- Mapping is stored in the session.
- For **Wide**, columns with antibiotic suffix are extracted.
- For **Long**, antibiotic names and results are aligned for each row.

---

### 3. Dataset Checks

#### How to Use
- The system automatically validates the dataset after mapping.

#### What Happens Internally
Checks performed include:
- Structural validity (columns and non-empty rows)
- Duplicate detection
- Date format verification
- Detection of future dates
- Results of checks are shown on the **Results Page** if any issues arise.

---

### 4. Results Page

#### How to Use
- After checks, you'll be directed to the **Results Page**.
- Choose from:
  - **Isolation Burden Analysis**
  - **Resistance Analysis**
  - **Scorecards**
- Click the corresponding button to continue.

#### What Happens Internally
- The selected analysis is performed using the processed and validated dataset.
- Results are visualized as interactive graphs or scorecards.

---

### 5. Isolation Burden Analysis

#### How to Use
- From the Results Page, select **Isolation Burden Analysis**.
- Apply filters:
  - **Source** (e.g., Blood, Urine, etc.)
  - **Country** or **All Countries**
  - **Cluster Attribute** (e.g., Age Group, Region)
  - **Gender Filter** (enable if needed)
- Click **Generate Graph**.

#### What Happens Internally
- Data is grouped based on selected filters.
- Isolation counts are calculated and displayed using grouped bar or line charts.

---

### 6. Resistance Analysis

#### How to Use
- From the Results Page, select **Resistance Analysis**.
- Select filters:
  - **Infection** (e.g., *E. coli*, *Klebsiella pneumoniae*)
  - **Antibiotic** (e.g., *Amikacin_I*)
  - **Source** (e.g., *Urine*, *Blood*)
- Click **Generate**.

#### What Happens Internally
- Filters are applied to the dataset.
- Dates are parsed and grouped by granularity.
- **Resistance Rate** is calculated:
  
  \[
  \text{Resistance Rate} = \left( \frac{\text{Resistant}}{\text{Total}} \right) \times 100
  \]

#### Confidence Intervals
- **Bootstrapping** with 1000 samples is used to compute **95% CI**.
- CI values are clipped to 0–100% for display.

#### Visualization
- A line graph is plotted:
  - **Line**: Non-zero resistance rates over time.
  - **Shaded Area**: 95% CI.
  - **Gray Dots**: Time points with zero resistance.

---

### 7. Scorecards

#### How to Use
- From the Results Page, select **Scorecards**.
- Depending on implementation, the user may view:
  - Per-source or per-country resistance summaries.
  - Stratified indicators by age group, gender, or infection type.

#### What Happens Internally
- Summarized statistics like resistance prevalence, frequency distributions, and top resistant organisms are calculated and formatted into visual scorecards.

---

## Common Errors and Resolutions

| Error | Cause | Resolution |
|------|-------|------------|
| **No file chosen** | No file was selected. | Select a `.csv` file before uploading. |
| **Invalid file extension** | Uploaded file isn't a `.csv`. | Upload a valid `.csv` file. |
| **The file appears to be empty** | File has no data. | Ensure your file has content. |
| **File could not be parsed** | Possibly corrupted or invalid delimiters. | Open the file and confirm it is readable. |
| **Dataset has no columns** | File lacks headers. | Ensure the file has properly formatted headers. |
| **Invalid date format** | Dates don't match the format you specified. | Recheck the date format and update mapping. |
| **Future dates found** | Date column has values from the future. | Update dataset to correct invalid dates. |

---

## Technical Notes

- **Session Handling**: Django sessions store the uploaded data and mappings.
- **Validation**:
  - MIME type is checked to prevent invalid files.
  - Parsing includes header inspection, delimiter consistency, and empty rows check.
- **Visualization**:
  - Graphs are rendered using **Matplotlib**.
  - Default theme is **dark** with white gridlines for contrast.
- **Bootstrapping**: Used to compute resistance rate confidence intervals robustly.
- **Error Messages**: Displayed inline to guide users on how to fix issues.

---

