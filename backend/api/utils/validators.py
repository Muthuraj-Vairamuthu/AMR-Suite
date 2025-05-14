import pandas as pd
from datetime import datetime
import chardet
import mimetypes
from typing import Dict, List, Tuple

class DatasetValidator:
    def __init__(self, dataset=None, mapping_data=None):
        self.dataset = dataset
        self.mapping_data = mapping_data
        # Define required and optional fields
        self.required_fields = {
            'date': 'date_column',
            'bacteria': 'bacterial_infection',
            'source': 'source_input'
        }
        self.optional_fields = {
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

            # Check required columns
            missing_fields = []
            for field, mapping_key in self.required_fields.items():
                mapped_column = self.mapping_data.get(mapping_key)
                if not mapped_column or mapped_column not in self.dataset.columns:
                    missing_fields.append(mapping_key)

            if missing_fields:
                results['errors'].append(f'Missing required columns: {", ".join(missing_fields)}')
                results['success'] = False

            # Check optional columns and add warnings
            for field, mapping_key in self.optional_fields.items():
                mapped_column = self.mapping_data.get(mapping_key)
                if mapped_column and mapped_column not in self.dataset.columns:
                    results['warnings'].append(f'Optional column {mapping_key} was specified but not found in dataset')

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
            # Check required fields
            for field, mapping_key in self.required_fields.items():
                self._check_column_missing_data(field, mapping_key, results)

            # Check optional fields if they are present
            for field, mapping_key in self.optional_fields.items():
                if self.mapping_data.get(mapping_key):  # Only check if field was specified
                    self._check_column_missing_data(field, mapping_key, results)

        except Exception as e:
            results['warnings'].append(f'Error checking missing data: {str(e)}')

        return results

    def _check_column_missing_data(self, field, mapping_key, results):
        """Helper method to check missing data for a single column"""
        column = self.mapping_data.get(mapping_key)
        if column and column in self.dataset.columns:
            missing_pct = (self.dataset[column].isna().sum() / len(self.dataset)) * 100
            results['missing_data'][field] = float(missing_pct)
            
            if missing_pct > 0:
                results['warnings'].append(f'{field} has {missing_pct:.1f}% missing values')
            if missing_pct > 20:
                results['warnings'].append(f'{field} has critical missing data ({missing_pct:.1f}%)')

    def check_duplicates(self):
        """Check for duplicate records based on isolate ID if available"""
        results = {
            'success': True,
            'duplicates': 0,
            'warnings': []
        }

        try:
            isolate_id = self.mapping_data.get('isolate_id')
            if isolate_id and isolate_id in self.dataset.columns:
                # Check duplicates only in isolate ID column
                duplicates = self.dataset[isolate_id].duplicated()
                results['duplicates'] = int(duplicates.sum())
                if results['duplicates'] > 0:
                    results['warnings'].append(f'Found {results["duplicates"]} duplicate isolate IDs')
            else:
                # Skip duplicate check if no isolate ID
                results['warnings'].append('No isolate ID column specified - skipping duplicate check')
                results['duplicates'] = 0

        except Exception as e:
            results['warnings'].append(f'Error checking duplicates: {str(e)}')

        return results