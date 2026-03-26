"""
Firebase Admin SDK integration for ScholarGrid Backend API

Provides Firebase Authentication token verification and Firebase Storage
file management (upload, download, delete) for notes, avatars, chat files,
and complaint attachments.
"""

import os
import uuid
from typing import Optional, Tuple
from pathlib import Path

import firebase_admin
from firebase_admin import credentials, auth, storage
from fastapi import UploadFile

from app.core.config import settings


# Global Firebase app instance
_firebase_app: Optional[firebase_admin.App] = None


def initialize_firebase() -> firebase_admin.App:
    """
    Initialize Firebase Admin SDK with service account credentials.
    
    This function should be called once during application startup.
    Uses the FIREBASE_CREDENTIALS_PATH from settings to load the
    service account JSON file.
    
    Returns:
        firebase_admin.App: Initialized Firebase app instance
        
    Raises:
        ValueError: If credentials file is not found or invalid
        Exception: If Firebase initialization fails
    """
    global _firebase_app
    
    if _firebase_app is not None:
        return _firebase_app
    
    credentials_path = settings.firebase_credentials_path
    
    if not os.path.exists(credentials_path):
        raise ValueError(
            f"Firebase credentials file not found at {credentials_path}. "
            "Please ensure FIREBASE_CREDENTIALS_PATH is set correctly."
        )
    
    try:
        cred = credentials.Certificate(credentials_path)
        _firebase_app = firebase_admin.initialize_app(cred, {
            'storageBucket': None  # Will be set from credentials
        })
        return _firebase_app
    except Exception as e:
        raise Exception(f"Failed to initialize Firebase Admin SDK: {str(e)}")


def get_firebase_app() -> firebase_admin.App:
    """
    Get the initialized Firebase app instance.
    
    Returns:
        firebase_admin.App: The Firebase app instance
        
    Raises:
        RuntimeError: If Firebase has not been initialized
    """
    if _firebase_app is None:
        raise RuntimeError(
            "Firebase has not been initialized. "
            "Call initialize_firebase() during application startup."
        )
    return _firebase_app


async def verify_firebase_token(token: str) -> dict:
    """
    Verify a Firebase ID token and extract user information.
    
    This function verifies the JWT token issued by Firebase Authentication
    and returns the decoded token containing user identity information.
    
    Args:
        token: Firebase ID token (JWT) from the client
        
    Returns:
        dict: Decoded token containing user information with keys:
            - uid: Firebase user ID
            - email: User email address
            - email_verified: Whether email is verified
            - name: User display name (if available)
            - picture: User profile picture URL (if available)
            
    Raises:
        auth.InvalidIdTokenError: If token is invalid or expired
        auth.ExpiredIdTokenError: If token has expired
        auth.RevokedIdTokenError: If token has been revoked
        ValueError: If token is empty or malformed
    """
    if not token:
        raise ValueError("Token cannot be empty")
    
    try:
        # Verify the token and decode it
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except auth.RevokedIdTokenError as e:
        raise auth.RevokedIdTokenError(f"Firebase token has been revoked: {str(e)}")
    except auth.ExpiredIdTokenError as e:
        raise auth.ExpiredIdTokenError(f"Firebase token has expired: {str(e)}", cause=e)
    except auth.InvalidIdTokenError as e:
        raise auth.InvalidIdTokenError(f"Invalid Firebase token: {str(e)}")
    except Exception as e:
        raise ValueError(f"Token verification failed: {str(e)}")


async def upload_file_to_storage(
    file: UploadFile,
    folder: str,
    allowed_extensions: Optional[set] = None
) -> Tuple[str, str, int]:
    """
    Upload a file to Firebase Storage.
    
    Generates a unique filename using UUID, validates file extension,
    uploads to the specified folder in Firebase Storage, and returns
    the public download URL.
    
    Args:
        file: FastAPI UploadFile object containing the file data
        folder: Storage folder path (e.g., 'notes/', 'avatars/', 'chat_files/')
        allowed_extensions: Set of allowed file extensions (e.g., {'.pdf', '.jpg'})
                          If None, all extensions are allowed
        
    Returns:
        Tuple[str, str, int]: (download_url, filename, file_size)
            - download_url: Public URL to access the file
            - filename: Generated unique filename with extension
            - file_size: Size of the file in bytes
            
    Raises:
        ValueError: If file extension is not allowed or file is empty
        Exception: If upload to Firebase Storage fails
    """
    if not file.filename:
        raise ValueError("File must have a filename")
    
    # Get file extension
    file_extension = Path(file.filename).suffix.lower()
    
    # Validate extension if restrictions are provided
    if allowed_extensions and file_extension not in allowed_extensions:
        raise ValueError(
            f"File type {file_extension} not allowed. "
            f"Allowed types: {', '.join(allowed_extensions)}"
        )
    
    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    
    # Ensure folder ends with /
    if not folder.endswith('/'):
        folder += '/'
    
    blob_path = f"{folder}{unique_filename}"
    
    try:
        # Read file content
        file_content = await file.read()
        file_size = len(file_content)
        
        if file_size == 0:
            raise ValueError("File is empty")
        
        # Get storage bucket
        bucket = storage.bucket()
        blob = bucket.blob(blob_path)
        
        # Set content type based on extension
        content_type = _get_content_type(file_extension)
        
        # Upload file
        blob.upload_from_string(
            file_content,
            content_type=content_type
        )
        
        # Make the blob publicly accessible
        blob.make_public()
        
        # Get public URL
        download_url = blob.public_url
        
        return download_url, unique_filename, file_size
        
    except Exception as e:
        raise Exception(f"Failed to upload file to Firebase Storage: {str(e)}")
    finally:
        # Reset file pointer for potential reuse
        await file.seek(0)


async def download_file_from_storage(file_path: str) -> bytes:
    """
    Download a file from Firebase Storage.
    
    Args:
        file_path: Full path to the file in storage (e.g., 'notes/uuid.pdf')
        
    Returns:
        bytes: File content as bytes
        
    Raises:
        FileNotFoundError: If file does not exist in storage
        Exception: If download fails
    """
    try:
        bucket = storage.bucket()
        blob = bucket.blob(file_path)
        
        if not blob.exists():
            raise FileNotFoundError(f"File not found in storage: {file_path}")
        
        # Download file content
        file_content = blob.download_as_bytes()
        return file_content
        
    except FileNotFoundError:
        raise
    except Exception as e:
        raise Exception(f"Failed to download file from Firebase Storage: {str(e)}")


async def delete_file_from_storage(file_path: str) -> bool:
    """
    Delete a file from Firebase Storage.
    
    Args:
        file_path: Full path to the file in storage (e.g., 'notes/uuid.pdf')
        
    Returns:
        bool: True if file was deleted, False if file did not exist
        
    Raises:
        Exception: If deletion fails for reasons other than file not existing
    """
    try:
        bucket = storage.bucket()
        blob = bucket.blob(file_path)
        
        if not blob.exists():
            return False
        
        # Delete the file
        blob.delete()
        return True
        
    except Exception as e:
        raise Exception(f"Failed to delete file from Firebase Storage: {str(e)}")


def _get_content_type(file_extension: str) -> str:
    """
    Get MIME content type for a file extension.
    
    Args:
        file_extension: File extension including the dot (e.g., '.pdf')
        
    Returns:
        str: MIME content type
    """
    content_types = {
        # Documents
        '.pdf': 'application/pdf',
        '.doc': 'application/msword',
        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        '.ppt': 'application/vnd.ms-powerpoint',
        '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        
        # Images
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.webp': 'image/webp',
        
        # Other
        '.txt': 'text/plain',
        '.zip': 'application/zip',
    }
    
    return content_types.get(file_extension.lower(), 'application/octet-stream')


# Storage folder constants for consistency
STORAGE_FOLDERS = {
    'notes': 'notes/',
    'avatars': 'avatars/',
    'chat_files': 'chat_files/',
    'complaint_attachments': 'complaint_attachments/'
}

# Allowed file extensions by category
ALLOWED_EXTENSIONS = {
    'notes': {'.pdf', '.doc', '.docx', '.ppt', '.pptx'},
    'avatars': {'.jpg', '.jpeg', '.png', '.webp'},
    'chat_files': {'.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png', '.txt', '.zip'},
    'complaint_attachments': {'.jpg', '.jpeg', '.png'}
}
