import pandas as pd
from datetime import datetime
import chardet
import mimetypes
from typing import Dict, List, Tuple

class DatasetValidator:
    def __init__(self, dataset=None, mapping_data=None):
        self.dataset = dataset
        self.mapping_data = mapping_data
        self.required_fields = {
            'date': 'date_column',
            'bacteria': 'bacterial_infection',
            'source': 'source_input',
            'isolate': 'isolate_id'
        }
        # Add antibiotic fields based on format
        if mapping_data and mapping_data.get('dataset_format') == 'Wide':
            self.antibiotic_suffix = mapping_data.get('antibiotic_format', '').replace('Antibiotic', '')
        else:
            self.required_fields.update({
                'antibiotic_name': 'antibiotic_name_col',
                'antibiotic_result': 'antibiotic_result_col'
            })

    def validate_dataset_structure(self):
        """Validate dataset structure and required fields"""
        results = {
            'success': True,
            'errors': [],
            'warnings': []
        }

        try:
            if self.dataset is None or self.dataset.empty:
                results['errors'].append('Dataset is empty')
                results['success'] = False
                return results

            # Check required columns based on dataset format
            missing_fields = []
            for field, mapping_key in self.required_fields.items():
                mapped_column = self.mapping_data.get(mapping_key)
                if not mapped_column or mapped_column not in self.dataset.columns:
                    missing_fields.append(mapping_key)

            if missing_fields:
                results['errors'].append(f'Missing required columns: {", ".join(missing_fields)}')
                results['success'] = False

            # Check for future/invalid dates
            date_column = self.mapping_data.get('date_column')
            if date_column and date_column in self.dataset.columns:
                current_year = datetime.now().year
                
                # Convert to numeric, coerce errors to NaN
                years = pd.to_numeric(self.dataset[date_column], errors='coerce')
                
                # Check for invalid years (non-numeric, negative, or too old)
                invalid_years = years[(years < 1950) | (years.isna())]
                if not invalid_years.empty:
                    results['errors'].append(
                        f'Found {len(invalid_years)} invalid years in {date_column} (years < 1950 or non-numeric)'
                    )
                    results['success'] = False
                
                # Check for future years
                future_years = years[years > current_year]
                if not future_years.empty:
                    results['errors'].append(
                        f'Found {len(future_years)} future years in {date_column} (years > {current_year})'
                    )
                    results['success'] = False

        except Exception as e:
            results['errors'].append(f'Validation error: {str(e)}')
            results['success'] = False

        return results

    def check_missing_data(self):
        """Analyze missing data in critical columns"""
        results = {
            'success': True,
            'warnings': [],
            'missing_data': {}
        }

        try:
            for field, mapping_key in self.required_fields.items():
                column = self.mapping_data.get(mapping_key)
                if column and column in self.dataset.columns:
                    missing_pct = (self.dataset[column].isna().sum() / len(self.dataset)) * 100
                    results['missing_data'][field] = float(missing_pct)
                    
                    if missing_pct > 0:
                        results['warnings'].append(f'{field} has {missing_pct:.1f}% missing values')
                    if missing_pct > 20:
                        results['warnings'].append(f'{field} has critical missing data ({missing_pct:.1f}%)')

        except Exception as e:
            results['warnings'].append(f'Error checking missing data: {str(e)}')

        return results

    def check_duplicates(self):
        """Check for duplicate records"""
        results = {
            'success': True,
            'duplicates': 0
        }

        try:
            duplicates = self.dataset.duplicated()
            results['duplicates'] = int(duplicates.sum())
        except Exception as e:
            results['warnings'] = [f'Error checking duplicates: {str(e)}']

        return results