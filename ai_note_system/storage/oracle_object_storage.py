"""
Oracle Object Storage module for AI Note System.
Handles file uploads, downloads, and presigned URL generation.
"""

import os
import logging
import json
import uuid
import time
from typing import Dict, Any, List, Optional, Tuple
import requests
import oci
from oci.config import from_file
from oci.object_storage import ObjectStorageClient
from oci.object_storage.models import CreatePreauthenticatedRequestDetails
from datetime import datetime, timedelta

# Setup logging
logger = logging.getLogger("ai_note_system.storage.oracle_object_storage")

class OracleObjectStorage:
    """
    Oracle Object Storage manager class for AI Note System.
    Handles file uploads, downloads, and presigned URL generation.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the OracleObjectStorage.
        
        Args:
            config_path (Optional[str]): Path to OCI config file. If None, uses environment variables.
        """
        self.namespace = os.environ.get('OBJECT_STORAGE_NAMESPACE')
        self.bucket_name = os.environ.get('OBJECT_STORAGE_BUCKET')
        self.region = os.environ.get('OBJECT_STORAGE_REGION')
        
        # Initialize OCI client
        try:
            if config_path:
                # Use config file if provided
                self.config = from_file(config_path)
                self.client = ObjectStorageClient(self.config)
            else:
                # Use instance principal authentication (for OCI compute instances)
                signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
                self.client = ObjectStorageClient(config={}, signer=signer)
                
            logger.debug(f"Connected to Oracle Object Storage: {self.namespace}/{self.bucket_name}")
        except Exception as e:
            logger.error(f"Error connecting to Oracle Object Storage: {e}")
            raise
    
    def upload_file(self, file_path: str, object_name: Optional[str] = None) -> str:
        """
        Upload a file to Oracle Object Storage.
        
        Args:
            file_path (str): Path to the file to upload
            object_name (Optional[str]): Name to use for the object in the bucket. If None, uses the file name.
            
        Returns:
            str: Object name in the bucket
        """
        try:
            if not object_name:
                object_name = os.path.basename(file_path)
                
            # Add a UUID to ensure uniqueness
            object_name = f"{uuid.uuid4()}_{object_name}"
            
            # Read file content
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            # Upload to Object Storage
            self.client.put_object(
                namespace_name=self.namespace,
                bucket_name=self.bucket_name,
                object_name=object_name,
                put_object_body=file_content
            )
            
            logger.info(f"Uploaded file to Object Storage: {object_name}")
            return object_name
            
        except Exception as e:
            logger.error(f"Error uploading file to Object Storage: {e}")
            raise
    
    def download_file(self, object_name: str, destination_path: str) -> str:
        """
        Download a file from Oracle Object Storage.
        
        Args:
            object_name (str): Name of the object in the bucket
            destination_path (str): Path where the file should be saved
            
        Returns:
            str: Path to the downloaded file
        """
        try:
            # Get object from Object Storage
            response = self.client.get_object(
                namespace_name=self.namespace,
                bucket_name=self.bucket_name,
                object_name=object_name
            )
            
            # Save to destination
            with open(destination_path, 'wb') as f:
                for chunk in response.data.raw.stream(1024 * 1024, decode_content=False):
                    f.write(chunk)
            
            logger.info(f"Downloaded file from Object Storage: {object_name}")
            return destination_path
            
        except Exception as e:
            logger.error(f"Error downloading file from Object Storage: {e}")
            raise
    
    def generate_presigned_url(self, object_name: str, expiration_time_minutes: int = 60) -> str:
        """
        Generate a presigned URL for accessing an object.
        
        Args:
            object_name (str): Name of the object in the bucket
            expiration_time_minutes (int): Number of minutes until the URL expires
            
        Returns:
            str: Presigned URL
        """
        try:
            # Calculate expiration time
            time_expires = datetime.now() + timedelta(minutes=expiration_time_minutes)
            
            # Create pre-authenticated request
            create_par_details = CreatePreauthenticatedRequestDetails(
                name=f"par_{uuid.uuid4().hex}",
                access_type="ObjectRead",
                time_expires=time_expires,
                bucket_listing_action="Deny",
                object_name=object_name
            )
            
            par = self.client.create_preauthenticated_request(
                namespace_name=self.namespace,
                bucket_name=self.bucket_name,
                create_preauthenticated_request_details=create_par_details
            )
            
            # Construct the full URL
            base_url = f"https://objectstorage.{self.region}.oraclecloud.com"
            presigned_url = f"{base_url}{par.data.access_uri}"
            
            logger.info(f"Generated presigned URL for: {object_name}")
            return presigned_url
            
        except Exception as e:
            logger.error(f"Error generating presigned URL: {e}")
            raise
    
    def generate_upload_url(self, object_name: str, expiration_time_minutes: int = 60) -> str:
        """
        Generate a presigned URL for uploading an object.
        
        Args:
            object_name (str): Name to use for the object in the bucket
            expiration_time_minutes (int): Number of minutes until the URL expires
            
        Returns:
            str: Presigned URL for uploading
        """
        try:
            # Calculate expiration time
            time_expires = datetime.now() + timedelta(minutes=expiration_time_minutes)
            
            # Create pre-authenticated request for object write
            create_par_details = CreatePreauthenticatedRequestDetails(
                name=f"par_upload_{uuid.uuid4().hex}",
                access_type="ObjectWrite",
                time_expires=time_expires,
                bucket_listing_action="Deny",
                object_name=object_name
            )
            
            par = self.client.create_preauthenticated_request(
                namespace_name=self.namespace,
                bucket_name=self.bucket_name,
                create_preauthenticated_request_details=create_par_details
            )
            
            # Construct the full URL
            base_url = f"https://objectstorage.{self.region}.oraclecloud.com"
            presigned_url = f"{base_url}{par.data.access_uri}"
            
            logger.info(f"Generated upload URL for: {object_name}")
            return presigned_url
            
        except Exception as e:
            logger.error(f"Error generating upload URL: {e}")
            raise
    
    def delete_object(self, object_name: str) -> bool:
        """
        Delete an object from Oracle Object Storage.
        
        Args:
            object_name (str): Name of the object in the bucket
            
        Returns:
            bool: True if successful
        """
        try:
            # Delete object from Object Storage
            self.client.delete_object(
                namespace_name=self.namespace,
                bucket_name=self.bucket_name,
                object_name=object_name
            )
            
            logger.info(f"Deleted object from Object Storage: {object_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting object from Object Storage: {e}")
            raise

def init_object_storage(config_path: Optional[str] = None) -> OracleObjectStorage:
    """
    Initialize the Oracle Object Storage client.
    
    Args:
        config_path (Optional[str]): Path to OCI config file. If None, uses environment variables.
        
    Returns:
        OracleObjectStorage: Initialized Oracle Object Storage client
    """
    logger.info("Initializing Oracle Object Storage client")
    
    try:
        storage_client = OracleObjectStorage(config_path)
        logger.info("Oracle Object Storage client initialized successfully")
        return storage_client
        
    except Exception as e:
        logger.error(f"Error initializing Oracle Object Storage client: {e}")
        raise