"""
Custom Dataset Curation & Analysis Assistant

This module provides functionality for fetching, cleaning, and summarizing open datasets,
as well as generating preprocessing code skeletons.
"""

import os
import logging
import json
import re
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime
import requests
import pandas as pd
import numpy as np

# Import related components
from ..database.db_manager import DatabaseManager
from ..api.llm_interface import LLMInterface, get_llm_interface

# Set up logging
logger = logging.getLogger(__name__)

class DatasetSource:
    """Sources for datasets"""
    KAGGLE = "kaggle"
    UCI = "uci"
    HUGGINGFACE = "huggingface"
    OPENML = "openml"
    GITHUB = "github"
    CUSTOM = "custom"

class DatasetAssistant:
    """
    Custom Dataset Curation & Analysis Assistant
    
    Features:
    - Fetch datasets from various sources
    - Clean and preprocess datasets
    - Generate dataset summaries and statistics
    - Create preprocessing code skeletons
    """
    
    def __init__(self, db_manager: DatabaseManager, 
                 llm_interface: Optional[LLMInterface] = None):
        """Initialize the dataset assistant"""
        self.db_manager = db_manager
        self.llm_interface = llm_interface or get_llm_interface()
        
        # Ensure database tables exist
        self._ensure_tables()
    
    def _ensure_tables(self) -> None:
        """Ensure that all required tables exist in the database"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        # Create datasets table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS datasets (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            source TEXT NOT NULL,
            source_url TEXT,
            local_path TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            size_bytes INTEGER,
            num_rows INTEGER,
            num_columns INTEGER,
            license TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        ''')
        
        # Create dataset columns table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS dataset_columns (
            id INTEGER PRIMARY KEY,
            dataset_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            data_type TEXT NOT NULL,
            description TEXT,
            stats TEXT,
            FOREIGN KEY (dataset_id) REFERENCES datasets(id)
        )
        ''')
        
        # Create dataset summaries table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS dataset_summaries (
            id INTEGER PRIMARY KEY,
            dataset_id INTEGER NOT NULL,
            summary_text TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (dataset_id) REFERENCES datasets(id)
        )
        ''')
        
        # Create preprocessing code table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS preprocessing_code (
            id INTEGER PRIMARY KEY,
            dataset_id INTEGER NOT NULL,
            language TEXT NOT NULL,
            code TEXT NOT NULL,
            description TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (dataset_id) REFERENCES datasets(id)
        )
        ''')
        
        conn.commit()
    
    def search_datasets(self, query: str, source: Optional[str] = None, 
                      limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for datasets from various sources
        
        Args:
            query: The search query
            source: Optional source to search (kaggle, uci, huggingface, etc.)
            limit: Maximum number of results to return
            
        Returns:
            List of dataset summaries
        """
        logger.info(f"Searching for datasets: {query}")
        
        results = []
        
        # If source is specified, only search that source
        if source:
            if source == DatasetSource.KAGGLE:
                results.extend(self._search_kaggle(query, limit))
            elif source == DatasetSource.UCI:
                results.extend(self._search_uci(query, limit))
            elif source == DatasetSource.HUGGINGFACE:
                results.extend(self._search_huggingface(query, limit))
            elif source == DatasetSource.OPENML:
                results.extend(self._search_openml(query, limit))
            elif source == DatasetSource.GITHUB:
                results.extend(self._search_github(query, limit))
        else:
            # Search all sources and combine results
            results.extend(self._search_kaggle(query, limit // 3))
            results.extend(self._search_huggingface(query, limit // 3))
            results.extend(self._search_openml(query, limit // 3))
        
        # Sort by relevance and limit results
        results = sorted(results, key=lambda x: x.get('relevance', 0), reverse=True)[:limit]
        
        return results
    
    def fetch_dataset(self, user_id: int, dataset_info: Dict[str, Any], 
                    local_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Fetch a dataset and store it locally
        
        Args:
            user_id: The ID of the user
            dataset_info: Information about the dataset to fetch
            local_path: Optional local path to store the dataset
            
        Returns:
            Dictionary with dataset details
        """
        logger.info(f"Fetching dataset: {dataset_info.get('name', 'Unknown')}")
        
        # Create a default local path if not provided
        if not local_path:
            data_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'datasets')
            os.makedirs(data_dir, exist_ok=True)
            
            # Create a safe filename from the dataset name
            safe_name = re.sub(r'[^\w\-\.]', '_', dataset_info.get('name', 'dataset'))
            local_path = os.path.join(data_dir, f"{safe_name}_{datetime.now().strftime('%Y%m%d%H%M%S')}")
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(os.path.abspath(local_path)), exist_ok=True)
        
        # Fetch the dataset based on the source
        source = dataset_info.get('source', '')
        source_url = dataset_info.get('source_url', '')
        
        if source == DatasetSource.KAGGLE:
            dataset_path = self._fetch_kaggle_dataset(dataset_info, local_path)
        elif source == DatasetSource.HUGGINGFACE:
            dataset_path = self._fetch_huggingface_dataset(dataset_info, local_path)
        elif source == DatasetSource.OPENML:
            dataset_path = self._fetch_openml_dataset(dataset_info, local_path)
        elif source == DatasetSource.UCI:
            dataset_path = self._fetch_uci_dataset(dataset_info, local_path)
        elif source == DatasetSource.GITHUB:
            dataset_path = self._fetch_github_dataset(dataset_info, local_path)
        elif source_url:
            # Try to download from the provided URL
            dataset_path = self._download_from_url(source_url, local_path)
        else:
            return {'error': 'Unsupported dataset source or missing source URL'}
        
        if not dataset_path or not os.path.exists(dataset_path):
            return {'error': 'Failed to fetch dataset'}
        
        # Analyze the dataset
        dataset_stats = self.analyze_dataset(dataset_path)
        
        # Store dataset information in the database
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        
        cursor.execute('''
        INSERT INTO datasets (
            user_id, name, description, source, source_url, local_path,
            created_at, updated_at, size_bytes, num_rows, num_columns, license
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            dataset_info.get('name', 'Unknown'),
            dataset_info.get('description', ''),
            source,
            source_url,
            dataset_path,
            now,
            now,
            dataset_stats.get('size_bytes', 0),
            dataset_stats.get('num_rows', 0),
            dataset_stats.get('num_columns', 0),
            dataset_info.get('license', '')
        ))
        
        dataset_id = cursor.lastrowid
        
        # Store column information
        for column in dataset_stats.get('columns', []):
            cursor.execute('''
            INSERT INTO dataset_columns (
                dataset_id, name, data_type, description, stats
            )
            VALUES (?, ?, ?, ?, ?)
            ''', (
                dataset_id,
                column.get('name', ''),
                column.get('data_type', ''),
                column.get('description', ''),
                json.dumps(column.get('stats', {}))
            ))
        
        conn.commit()
        
        # Return the dataset information
        return {
            'id': dataset_id,
            'name': dataset_info.get('name', 'Unknown'),
            'description': dataset_info.get('description', ''),
            'source': source,
            'source_url': source_url,
            'local_path': dataset_path,
            'created_at': now,
            'updated_at': now,
            'size_bytes': dataset_stats.get('size_bytes', 0),
            'num_rows': dataset_stats.get('num_rows', 0),
            'num_columns': dataset_stats.get('num_columns', 0),
            'license': dataset_info.get('license', ''),
            'columns': dataset_stats.get('columns', [])
        }
    
    def analyze_dataset(self, dataset_path: str) -> Dict[str, Any]:
        """
        Analyze a dataset and generate statistics
        
        Args:
            dataset_path: Path to the dataset file
            
        Returns:
            Dictionary with dataset statistics
        """
        logger.info(f"Analyzing dataset: {dataset_path}")
        
        # Get file size
        size_bytes = os.path.getsize(dataset_path)
        
        # Determine file type and load dataset
        file_ext = os.path.splitext(dataset_path)[1].lower()
        
        try:
            if file_ext == '.csv':
                df = pd.read_csv(dataset_path)
            elif file_ext == '.json':
                df = pd.read_json(dataset_path)
            elif file_ext == '.xlsx' or file_ext == '.xls':
                df = pd.read_excel(dataset_path)
            elif file_ext == '.parquet':
                df = pd.read_parquet(dataset_path)
            elif file_ext == '.feather':
                df = pd.read_feather(dataset_path)
            elif file_ext == '.pickle' or file_ext == '.pkl':
                df = pd.read_pickle(dataset_path)
            else:
                # Try CSV as a default
                df = pd.read_csv(dataset_path)
        except Exception as e:
            logger.error(f"Failed to load dataset: {e}")
            return {
                'size_bytes': size_bytes,
                'error': f"Failed to load dataset: {str(e)}"
            }
        
        # Get basic statistics
        num_rows = len(df)
        num_columns = len(df.columns)
        
        # Analyze each column
        columns = []
        for col_name in df.columns:
            col_data = df[col_name]
            col_type = str(col_data.dtype)
            
            # Get column statistics based on data type
            stats = {}
            
            if np.issubdtype(col_data.dtype, np.number):
                # Numeric column
                stats = {
                    'min': float(col_data.min()) if not pd.isna(col_data.min()) else None,
                    'max': float(col_data.max()) if not pd.isna(col_data.max()) else None,
                    'mean': float(col_data.mean()) if not pd.isna(col_data.mean()) else None,
                    'median': float(col_data.median()) if not pd.isna(col_data.median()) else None,
                    'std': float(col_data.std()) if not pd.isna(col_data.std()) else None,
                    'null_count': int(col_data.isna().sum()),
                    'null_percentage': float(col_data.isna().mean() * 100)
                }
            elif col_data.dtype == 'object' or col_data.dtype == 'string':
                # String column
                stats = {
                    'unique_count': int(col_data.nunique()),
                    'null_count': int(col_data.isna().sum()),
                    'null_percentage': float(col_data.isna().mean() * 100),
                    'most_common': col_data.value_counts().head(5).to_dict() if not col_data.isna().all() else {}
                }
            elif col_data.dtype == 'bool':
                # Boolean column
                stats = {
                    'true_count': int(col_data.sum()),
                    'false_count': int((~col_data & ~col_data.isna()).sum()),
                    'null_count': int(col_data.isna().sum()),
                    'null_percentage': float(col_data.isna().mean() * 100)
                }
            elif pd.api.types.is_datetime64_any_dtype(col_data):
                # Datetime column
                stats = {
                    'min': col_data.min().isoformat() if not pd.isna(col_data.min()) else None,
                    'max': col_data.max().isoformat() if not pd.isna(col_data.max()) else None,
                    'null_count': int(col_data.isna().sum()),
                    'null_percentage': float(col_data.isna().mean() * 100)
                }
            else:
                # Other column types
                stats = {
                    'unique_count': int(col_data.nunique()),
                    'null_count': int(col_data.isna().sum()),
                    'null_percentage': float(col_data.isna().mean() * 100)
                }
            
            columns.append({
                'name': col_name,
                'data_type': col_type,
                'description': '',  # Will be filled by generate_dataset_summary
                'stats': stats
            })
        
        return {
            'size_bytes': size_bytes,
            'num_rows': num_rows,
            'num_columns': num_columns,
            'columns': columns
        }
    
    def generate_dataset_summary(self, dataset_id: int) -> Dict[str, Any]:
        """
        Generate a summary of a dataset
        
        Args:
            dataset_id: The ID of the dataset
            
        Returns:
            Dictionary with the generated summary
        """
        logger.info(f"Generating summary for dataset {dataset_id}")
        
        # Get dataset information
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT id, name, description, source, source_url, local_path,
               created_at, size_bytes, num_rows, num_columns, license
        FROM datasets
        WHERE id = ?
        ''', (dataset_id,))
        
        row = cursor.fetchone()
        
        if not row:
            return {'error': 'Dataset not found'}
        
        dataset = {
            'id': row[0],
            'name': row[1],
            'description': row[2],
            'source': row[3],
            'source_url': row[4],
            'local_path': row[5],
            'created_at': row[6],
            'size_bytes': row[7],
            'num_rows': row[8],
            'num_columns': row[9],
            'license': row[10],
            'columns': []
        }
        
        # Get column information
        cursor.execute('''
        SELECT id, name, data_type, description, stats
        FROM dataset_columns
        WHERE dataset_id = ?
        ''', (dataset_id,))
        
        for row in cursor.fetchall():
            column = {
                'id': row[0],
                'name': row[1],
                'data_type': row[2],
                'description': row[3],
                'stats': json.loads(row[4]) if row[4] else {}
            }
            dataset['columns'].append(column)
        
        # Load a sample of the dataset for analysis
        try:
            file_ext = os.path.splitext(dataset['local_path'])[1].lower()
            
            if file_ext == '.csv':
                df = pd.read_csv(dataset['local_path'], nrows=100)
            elif file_ext == '.json':
                df = pd.read_json(dataset['local_path'])
            elif file_ext == '.xlsx' or file_ext == '.xls':
                df = pd.read_excel(dataset['local_path'], nrows=100)
            elif file_ext == '.parquet':
                df = pd.read_parquet(dataset['local_path'])
            elif file_ext == '.feather':
                df = pd.read_feather(dataset['local_path'])
            elif file_ext == '.pickle' or file_ext == '.pkl':
                df = pd.read_pickle(dataset['local_path'])
            else:
                # Try CSV as a default
                df = pd.read_csv(dataset['local_path'], nrows=100)
            
            # Get a sample of the data as a string
            sample_data = df.head(5).to_string()
        except Exception as e:
            logger.error(f"Failed to load dataset sample: {e}")
            sample_data = "Failed to load dataset sample"
        
        # Prepare column information for the prompt
        columns_info = ""
        for column in dataset['columns']:
            columns_info += f"Column: {column['name']}\n"
            columns_info += f"Type: {column['data_type']}\n"
            
            stats = column.get('stats', {})
            if 'min' in stats and 'max' in stats:
                columns_info += f"Range: {stats['min']} to {stats['max']}\n"
            if 'null_count' in stats:
                columns_info += f"Null values: {stats['null_count']} ({stats.get('null_percentage', 0):.2f}%)\n"
            if 'unique_count' in stats:
                columns_info += f"Unique values: {stats['unique_count']}\n"
            if 'most_common' in stats and stats['most_common']:
                columns_info += "Most common values:\n"
                for value, count in list(stats['most_common'].items())[:3]:
                    columns_info += f"  - {value}: {count}\n"
            
            columns_info += "\n"
        
        # Prepare prompt for LLM
        prompt = f"""
        You are an expert data scientist analyzing a dataset. Generate a comprehensive summary of the following dataset:
        
        Dataset Name: {dataset['name']}
        Description: {dataset['description'] or 'No description provided'}
        Source: {dataset['source']}
        Size: {dataset['size_bytes']} bytes
        Rows: {dataset['num_rows']}
        Columns: {dataset['num_columns']}
        License: {dataset['license'] or 'Unknown'}
        
        Column Information:
        {columns_info}
        
        Sample Data:
        {sample_data}
        
        Your summary should include:
        1. A brief overview of the dataset
        2. The potential use cases for this dataset
        3. Key observations about the data (patterns, anomalies, etc.)
        4. Data quality assessment (missing values, outliers, etc.)
        5. Preprocessing steps that might be necessary
        6. Potential challenges in working with this dataset
        7. Brief descriptions for each column explaining what the data represents
        
        Format your response as a well-structured markdown document with appropriate headings and sections.
        """
        
        # Generate summary using LLM
        summary_text = self.llm_interface.generate_text(prompt, max_tokens=2000)
        
        # Store the summary in the database
        now = datetime.now().isoformat()
        
        cursor.execute('''
        INSERT INTO dataset_summaries (dataset_id, summary_text, created_at)
        VALUES (?, ?, ?)
        ''', (dataset_id, summary_text, now))
        
        summary_id = cursor.lastrowid
        
        # Extract column descriptions from the summary
        column_descriptions = self._extract_column_descriptions(summary_text, dataset['columns'])
        
        # Update column descriptions
        for column in column_descriptions:
            cursor.execute('''
            UPDATE dataset_columns
            SET description = ?
            WHERE dataset_id = ? AND name = ?
            ''', (column['description'], dataset_id, column['name']))
        
        conn.commit()
        
        return {
            'id': summary_id,
            'dataset_id': dataset_id,
            'summary_text': summary_text,
            'created_at': now,
            'column_descriptions': column_descriptions
        }
    
    def generate_preprocessing_code(self, dataset_id: int, language: str = 'python') -> Dict[str, Any]:
        """
        Generate preprocessing code for a dataset
        
        Args:
            dataset_id: The ID of the dataset
            language: The programming language for the code (python, r, etc.)
            
        Returns:
            Dictionary with the generated code
        """
        logger.info(f"Generating preprocessing code for dataset {dataset_id}")
        
        # Get dataset information
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT id, name, description, source, local_path, num_rows, num_columns
        FROM datasets
        WHERE id = ?
        ''', (dataset_id,))
        
        row = cursor.fetchone()
        
        if not row:
            return {'error': 'Dataset not found'}
        
        dataset = {
            'id': row[0],
            'name': row[1],
            'description': row[2],
            'source': row[3],
            'local_path': row[4],
            'num_rows': row[5],
            'num_columns': row[6],
            'columns': []
        }
        
        # Get column information
        cursor.execute('''
        SELECT name, data_type, description, stats
        FROM dataset_columns
        WHERE dataset_id = ?
        ''', (dataset_id,))
        
        for row in cursor.fetchall():
            column = {
                'name': row[0],
                'data_type': row[1],
                'description': row[2],
                'stats': json.loads(row[3]) if row[3] else {}
            }
            dataset['columns'].append(column)
        
        # Get the dataset summary if available
        cursor.execute('''
        SELECT summary_text
        FROM dataset_summaries
        WHERE dataset_id = ?
        ORDER BY created_at DESC
        LIMIT 1
        ''', (dataset_id,))
        
        row = cursor.fetchone()
        summary_text = row[0] if row else "No summary available"
        
        # Prepare column information for the prompt
        columns_info = ""
        for column in dataset['columns']:
            columns_info += f"Column: {column['name']}\n"
            columns_info += f"Type: {column['data_type']}\n"
            columns_info += f"Description: {column['description'] or 'No description'}\n"
            
            stats = column.get('stats', {})
            if 'null_count' in stats and stats['null_count'] > 0:
                columns_info += f"Null values: {stats['null_count']} ({stats.get('null_percentage', 0):.2f}%)\n"
            
            columns_info += "\n"
        
        # Determine file type
        file_ext = os.path.splitext(dataset['local_path'])[1].lower()
        
        # Prepare prompt for LLM
        prompt = f"""
        You are an expert data scientist creating preprocessing code for a dataset. Generate comprehensive {language} code for preprocessing the following dataset:
        
        Dataset Name: {dataset['name']}
        Description: {dataset['description'] or 'No description provided'}
        File Type: {file_ext}
        Rows: {dataset['num_rows']}
        Columns: {dataset['num_columns']}
        
        Column Information:
        {columns_info}
        
        Dataset Summary:
        {summary_text[:500]}...
        
        Generate complete, well-documented {language} code that:
        1. Loads the dataset
        2. Performs exploratory data analysis (basic statistics, distributions, correlations)
        3. Handles missing values appropriately for each column
        4. Performs feature engineering where appropriate
        5. Encodes categorical variables
        6. Normalizes/standardizes numerical features
        7. Handles outliers
        8. Splits the data into training and testing sets
        9. Saves the preprocessed dataset
        
        Include detailed comments explaining each step and the rationale behind preprocessing decisions.
        The code should be production-ready, efficient, and follow best practices for {language}.
        """
        
        # Generate code using LLM
        code = self.llm_interface.generate_text(prompt, max_tokens=3000)
        
        # Extract code blocks if the response is in markdown format
        if '```' in code:
            code_blocks = re.findall(r'```(?:\w+)?\s*(.*?)\s*```', code, re.DOTALL)
            if code_blocks:
                code = '\n\n'.join(code_blocks)
        
        # Store the code in the database
        now = datetime.now().isoformat()
        
        cursor.execute('''
        INSERT INTO preprocessing_code (dataset_id, language, code, description, created_at)
        VALUES (?, ?, ?, ?, ?)
        ''', (dataset_id, language, code, f"Preprocessing code for {dataset['name']}", now))
        
        code_id = cursor.lastrowid
        conn.commit()
        
        return {
            'id': code_id,
            'dataset_id': dataset_id,
            'language': language,
            'code': code,
            'description': f"Preprocessing code for {dataset['name']}",
            'created_at': now
        }
    
    def get_user_datasets(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get datasets for a user
        
        Args:
            user_id: The ID of the user
            limit: Maximum number of datasets to return
            
        Returns:
            List of dataset summaries
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT id, name, description, source, created_at, num_rows, num_columns
        FROM datasets
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT ?
        ''', (user_id, limit))
        
        datasets = []
        for row in cursor.fetchall():
            dataset = {
                'id': row[0],
                'name': row[1],
                'description': row[2],
                'source': row[3],
                'created_at': row[4],
                'num_rows': row[5],
                'num_columns': row[6]
            }
            datasets.append(dataset)
        
        return datasets
    
    def _search_kaggle(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for datasets on Kaggle"""
        try:
            # This requires the kaggle API and authentication
            # For a real implementation, you would use the kaggle API client
            # Here we'll just return a placeholder
            return [{
                'name': f"Kaggle Dataset for {query}",
                'description': f"This is a placeholder for a Kaggle dataset related to {query}",
                'source': DatasetSource.KAGGLE,
                'source_url': f"https://www.kaggle.com/datasets?search={query}",
                'size': "Unknown",
                'last_updated': datetime.now().isoformat(),
                'license': "Unknown",
                'relevance': 0.9
            }]
        except Exception as e:
            logger.error(f"Error searching Kaggle: {e}")
            return []
    
    def _search_huggingface(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for datasets on Hugging Face"""
        try:
            # For a real implementation, you would use the Hugging Face API
            # Here we'll just return a placeholder
            return [{
                'name': f"Hugging Face Dataset for {query}",
                'description': f"This is a placeholder for a Hugging Face dataset related to {query}",
                'source': DatasetSource.HUGGINGFACE,
                'source_url': f"https://huggingface.co/datasets?search={query}",
                'size': "Unknown",
                'last_updated': datetime.now().isoformat(),
                'license': "Unknown",
                'relevance': 0.85
            }]
        except Exception as e:
            logger.error(f"Error searching Hugging Face: {e}")
            return []
    
    def _search_openml(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for datasets on OpenML"""
        try:
            # For a real implementation, you would use the OpenML API
            # Here we'll just return a placeholder
            return [{
                'name': f"OpenML Dataset for {query}",
                'description': f"This is a placeholder for an OpenML dataset related to {query}",
                'source': DatasetSource.OPENML,
                'source_url': f"https://www.openml.org/search?type=data&sort=runs&q={query}",
                'size': "Unknown",
                'last_updated': datetime.now().isoformat(),
                'license': "Unknown",
                'relevance': 0.8
            }]
        except Exception as e:
            logger.error(f"Error searching OpenML: {e}")
            return []
    
    def _search_uci(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for datasets on UCI Machine Learning Repository"""
        try:
            # For a real implementation, you would scrape or use an API if available
            # Here we'll just return a placeholder
            return [{
                'name': f"UCI Dataset for {query}",
                'description': f"This is a placeholder for a UCI dataset related to {query}",
                'source': DatasetSource.UCI,
                'source_url': f"https://archive.ics.uci.edu/ml/datasets.php?format=&task=&att=&area=&numAtt=&numIns=&type=&sort=nameUp&view=list&search={query}",
                'size': "Unknown",
                'last_updated': datetime.now().isoformat(),
                'license': "Unknown",
                'relevance': 0.75
            }]
        except Exception as e:
            logger.error(f"Error searching UCI: {e}")
            return []
    
    def _search_github(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for datasets on GitHub"""
        try:
            # For a real implementation, you would use the GitHub API
            # Here we'll just return a placeholder
            return [{
                'name': f"GitHub Dataset for {query}",
                'description': f"This is a placeholder for a GitHub dataset related to {query}",
                'source': DatasetSource.GITHUB,
                'source_url': f"https://github.com/search?q={query}+dataset",
                'size': "Unknown",
                'last_updated': datetime.now().isoformat(),
                'license': "Unknown",
                'relevance': 0.7
            }]
        except Exception as e:
            logger.error(f"Error searching GitHub: {e}")
            return []
    
    def _fetch_kaggle_dataset(self, dataset_info: Dict[str, Any], local_path: str) -> Optional[str]:
        """Fetch a dataset from Kaggle"""
        # This requires the kaggle API and authentication
        # For a real implementation, you would use the kaggle API client
        # Here we'll just create a placeholder file
        try:
            with open(f"{local_path}.csv", 'w') as f:
                f.write("id,feature1,feature2,target\n")
                f.write("1,0.5,0.7,1\n")
                f.write("2,0.3,0.2,0\n")
                f.write("3,0.8,0.9,1\n")
            
            return f"{local_path}.csv"
        except Exception as e:
            logger.error(f"Error fetching Kaggle dataset: {e}")
            return None
    
    def _fetch_huggingface_dataset(self, dataset_info: Dict[str, Any], local_path: str) -> Optional[str]:
        """Fetch a dataset from Hugging Face"""
        # For a real implementation, you would use the Hugging Face datasets library
        # Here we'll just create a placeholder file
        try:
            with open(f"{local_path}.csv", 'w') as f:
                f.write("text,label\n")
                f.write("This is a positive example,1\n")
                f.write("This is a negative example,0\n")
                f.write("This is a neutral example,2\n")
            
            return f"{local_path}.csv"
        except Exception as e:
            logger.error(f"Error fetching Hugging Face dataset: {e}")
            return None
    
    def _fetch_openml_dataset(self, dataset_info: Dict[str, Any], local_path: str) -> Optional[str]:
        """Fetch a dataset from OpenML"""
        # For a real implementation, you would use the OpenML API
        # Here we'll just create a placeholder file
        try:
            with open(f"{local_path}.csv", 'w') as f:
                f.write("feature1,feature2,feature3,class\n")
                f.write("1.2,3.4,5.6,A\n")
                f.write("2.3,4.5,6.7,B\n")
                f.write("3.4,5.6,7.8,A\n")
            
            return f"{local_path}.csv"
        except Exception as e:
            logger.error(f"Error fetching OpenML dataset: {e}")
            return None
    
    def _fetch_uci_dataset(self, dataset_info: Dict[str, Any], local_path: str) -> Optional[str]:
        """Fetch a dataset from UCI Machine Learning Repository"""
        # For a real implementation, you would download from the UCI website
        # Here we'll just create a placeholder file
        try:
            with open(f"{local_path}.csv", 'w') as f:
                f.write("attr1,attr2,attr3,class\n")
                f.write("1,2,3,yes\n")
                f.write("4,5,6,no\n")
                f.write("7,8,9,yes\n")
            
            return f"{local_path}.csv"
        except Exception as e:
            logger.error(f"Error fetching UCI dataset: {e}")
            return None
    
    def _fetch_github_dataset(self, dataset_info: Dict[str, Any], local_path: str) -> Optional[str]:
        """Fetch a dataset from GitHub"""
        # For a real implementation, you would use the GitHub API or git clone
        # Here we'll just create a placeholder file
        try:
            with open(f"{local_path}.csv", 'w') as f:
                f.write("col1,col2,col3\n")
                f.write("val1,val2,val3\n")
                f.write("val4,val5,val6\n")
            
            return f"{local_path}.csv"
        except Exception as e:
            logger.error(f"Error fetching GitHub dataset: {e}")
            return None
    
    def _download_from_url(self, url: str, local_path: str) -> Optional[str]:
        """Download a file from a URL"""
        try:
            # Determine file extension from URL
            file_ext = os.path.splitext(url)[1]
            if not file_ext:
                file_ext = '.csv'  # Default to CSV
            
            full_path = f"{local_path}{file_ext}"
            
            # Download the file
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            with open(full_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return full_path
        except Exception as e:
            logger.error(f"Error downloading from URL: {e}")
            return None
    
    def _extract_column_descriptions(self, summary_text: str, columns: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Extract column descriptions from the summary text"""
        column_descriptions = []
        
        for column in columns:
            column_name = column['name']
            
            # Look for descriptions in the summary text
            # This is a simple approach and might not work for all summaries
            pattern = rf"(?:Column|Field|Feature)(?:\s+name)?(?:\s*:\s*|\s+)?{re.escape(column_name)}(?:\s*:\s*|\s+)?([^\n.]+)"
            match = re.search(pattern, summary_text, re.IGNORECASE)
            
            description = ""
            if match:
                description = match.group(1).strip()
            else:
                # Try a more general approach
                sentences = re.split(r'(?<=[.!?])\s+', summary_text)
                for sentence in sentences:
                    if column_name in sentence:
                        description = sentence.strip()
                        break
            
            column_descriptions.append({
                'name': column_name,
                'description': description
            })
        
        return column_descriptions

# Helper functions for easier access to dataset assistant functionality

def search_datasets(db_manager, query: str, source: Optional[str] = None, 
                  limit: int = 10) -> List[Dict[str, Any]]:
    """
    Search for datasets from various sources
    
    Args:
        db_manager: Database manager instance
        query: The search query
        source: Optional source to search (kaggle, uci, huggingface, etc.)
        limit: Maximum number of results to return
        
    Returns:
        List of dataset summaries
    """
    assistant = DatasetAssistant(db_manager)
    return assistant.search_datasets(query, source, limit)

def fetch_dataset(db_manager, user_id: int, dataset_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fetch a dataset and store it locally
    
    Args:
        db_manager: Database manager instance
        user_id: The ID of the user
        dataset_info: Information about the dataset to fetch
        
    Returns:
        Dictionary with dataset details
    """
    assistant = DatasetAssistant(db_manager)
    return assistant.fetch_dataset(user_id, dataset_info)

def generate_dataset_summary(db_manager, dataset_id: int) -> Dict[str, Any]:
    """
    Generate a summary of a dataset
    
    Args:
        db_manager: Database manager instance
        dataset_id: The ID of the dataset
        
    Returns:
        Dictionary with the generated summary
    """
    assistant = DatasetAssistant(db_manager)
    return assistant.generate_dataset_summary(dataset_id)

def generate_preprocessing_code(db_manager, dataset_id: int, language: str = 'python') -> Dict[str, Any]:
    """
    Generate preprocessing code for a dataset
    
    Args:
        db_manager: Database manager instance
        dataset_id: The ID of the dataset
        language: The programming language for the code (python, r, etc.)
        
    Returns:
        Dictionary with the generated code
    """
    assistant = DatasetAssistant(db_manager)
    return assistant.generate_preprocessing_code(dataset_id, language)