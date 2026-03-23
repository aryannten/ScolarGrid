"""
Cloudinary storage service for ScholarGrid Backend API

Free cloud storage using Cloudinary (25GB storage, 25GB bandwidth/month).
Simple alternative to Firebase Storage.
"""

import os
import uuid
from typing import Optional, Tuple
from pathlib import Path
from fastapi import UploadFile
import cloudinary
import cloudinary.uploader
from app.core.config import settings


def initialize_cloudinary():
    """Initialize Cloudinary with credentials from environment."""
    cloudinary.config(
        cloud_name=settings.cloudinary_cloud_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True
    )


async def upload_file_to_storage(
    file: UploadFile,
    folder: str,
    allowed_extensions: Optional[set] = None
) -> Tuple[str, str, int]:
    """
    Upload a file to Cloudinary.
    
    Args:
        file: FastAPI UploadFile object
        folder: Storage folder (e.g., 'notes', 'avatars')
        allowed_extensions: Set of allowed file extensions
        
    Returns:
        Tuple[str, str, int]: (file_url, filename, file_size)
    """
    if not file.filename:
        raise ValueError("File must have a filename")
    
    # Get file extension
    file_extension = Path(file.filename).suffix.lower()
    
    # Validate extension
    if allowed_extensions and file_extension not in allowed_extensions:
        raise ValueError(
            f"File type {file_extension} not allowed. "
            f"Allowed types: {', '.join(allowed_extensions)}"
        )
    
    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    
    # Read file content
    file_content = await file.read()
    file_size = len(file_content)
    
    if file_size == 0:
        raise ValueError("File is empty")
    
    # Determine resource type
    resource_type = 'image' if file_extension in {'.jpg', '.jpeg', '.png', '.gif', '.webp'} else 'raw'
    
    # Upload to Cloudinary
    result = cloudinary.uploader.upload(
        file_content,
        folder=folder,
        public_id=unique_filename.rsplit('.', 1)[0],  # Remove extension for public_id
        resource_type=resource_type
    )
    
    # Get secure URL
    file_url = result['secure_url']
    
    # Reset file pointer
    await file.seek(0)
    
    return file_url, unique_filename, file_size


async def delete_file_from_storage(file_path: str) -> bool:
    """
    Delete a file from Cloudinary.
    
    Args:
        file_path: Path like 'notes/uuid' (without extension)
        
    Returns:
        bool: True if deleted, False if not found
    """
    try:
        # Determine resource type from path
        resource_type = 'raw'  # Default to raw for documents
        
        result = cloudinary.uploader.destroy(file_path, resource_type=resource_type)
        
        # Try as image if raw deletion failed
        if result.get('result') != 'ok':
            result = cloudinary.uploader.destroy(file_path, resource_type='image')
        
        return result.get('result') == 'ok'
    except Exception:
        return False


# Storage folder constants
STORAGE_FOLDERS = {
    'notes': 'scholargrid/notes',
    'avatars': 'scholargrid/avatars',
    'chat_files': 'scholargrid/chat_files',
    'complaint_attachments': 'scholargrid/complaint_attachments'
}

# Allowed file extensions
ALLOWED_EXTENSIONS = {
    'notes': {'.pdf', '.doc', '.docx', '.ppt', '.pptx'},
    'avatars': {'.jpg', '.jpeg', '.png', '.webp'},
    'chat_files': {'.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png', '.txt', '.zip'},
    'complaint_attachments': {'.jpg', '.jpeg', '.png'}
}
