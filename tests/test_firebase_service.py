"""
Unit tests for Firebase service

Tests Firebase Admin SDK initialization, token verification,
and file storage operations.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from io import BytesIO

import firebase_admin
from firebase_admin import auth, storage
from fastapi import UploadFile

from app.services.firebase_service import (
    initialize_firebase,
    get_firebase_app,
    verify_firebase_token,
    upload_file_to_storage,
    download_file_from_storage,
    delete_file_from_storage,
    _get_content_type,
    STORAGE_FOLDERS,
    ALLOWED_EXTENSIONS
)


class TestFirebaseInitialization:
    """Test Firebase Admin SDK initialization"""
    
    @patch('app.firebase_service.firebase_admin.initialize_app')
    @patch('app.firebase_service.credentials.Certificate')
    @patch('app.firebase_service.os.path.exists')
    def test_initialize_firebase_success(self, mock_exists, mock_cert, mock_init):
        """Test successful Firebase initialization"""
        mock_exists.return_value = True
        mock_app = Mock()
        mock_init.return_value = mock_app
        
        # Reset global state
        import app.firebase_service
        app.firebase_service._firebase_app = None
        
        result = initialize_firebase()
        
        assert result == mock_app
        mock_exists.assert_called_once()
        mock_cert.assert_called_once()
        mock_init.assert_called_once()
    
    @patch('app.firebase_service.os.path.exists')
    def test_initialize_firebase_missing_credentials(self, mock_exists):
        """Test Firebase initialization fails when credentials file is missing"""
        mock_exists.return_value = False
        
        # Reset global state
        import app.firebase_service
        app.firebase_service._firebase_app = None
        
        with pytest.raises(ValueError, match="Firebase credentials file not found"):
            initialize_firebase()
    
    @patch('app.firebase_service.firebase_admin.initialize_app')
    @patch('app.firebase_service.credentials.Certificate')
    @patch('app.firebase_service.os.path.exists')
    def test_initialize_firebase_initialization_error(self, mock_exists, mock_cert, mock_init):
        """Test Firebase initialization handles SDK errors"""
        mock_exists.return_value = True
        mock_init.side_effect = Exception("SDK initialization failed")
        
        # Reset global state
        import app.firebase_service
        app.firebase_service._firebase_app = None
        
        with pytest.raises(Exception, match="Failed to initialize Firebase Admin SDK"):
            initialize_firebase()
    
    def test_get_firebase_app_not_initialized(self):
        """Test get_firebase_app raises error when not initialized"""
        # Reset global state
        import app.firebase_service
        app.firebase_service._firebase_app = None
        
        with pytest.raises(RuntimeError, match="Firebase has not been initialized"):
            get_firebase_app()
    
    def test_get_firebase_app_success(self):
        """Test get_firebase_app returns initialized app"""
        mock_app = Mock()
        
        # Set global state
        import app.firebase_service
        app.firebase_service._firebase_app = mock_app
        
        result = get_firebase_app()
        assert result == mock_app


class TestTokenVerification:
    """Test Firebase token verification"""
    
    @pytest.mark.asyncio
    @patch('app.firebase_service.auth.verify_id_token')
    async def test_verify_token_success(self, mock_verify):
        """Test successful token verification"""
        mock_decoded = {
            'uid': 'test-uid-123',
            'email': 'test@example.com',
            'email_verified': True
        }
        mock_verify.return_value = mock_decoded
        
        result = await verify_firebase_token('valid-token')
        
        assert result == mock_decoded
        mock_verify.assert_called_once_with('valid-token')
    
    @pytest.mark.asyncio
    async def test_verify_token_empty(self):
        """Test token verification fails with empty token"""
        with pytest.raises(ValueError, match="Token cannot be empty"):
            await verify_firebase_token('')
    
    @pytest.mark.asyncio
    @patch('app.firebase_service.auth.verify_id_token')
    async def test_verify_token_invalid(self, mock_verify):
        """Test token verification fails with invalid token"""
        mock_verify.side_effect = auth.InvalidIdTokenError("Invalid token")
        
        with pytest.raises(auth.InvalidIdTokenError, match="Invalid Firebase token"):
            await verify_firebase_token('invalid-token')
    
    @pytest.mark.asyncio
    @patch('app.firebase_service.auth.verify_id_token')
    async def test_verify_token_expired(self, mock_verify):
        """Test token verification fails with expired token"""
        mock_verify.side_effect = auth.ExpiredIdTokenError("Token expired", cause=Exception("expired"))
        
        with pytest.raises(auth.ExpiredIdTokenError, match="Firebase token has expired"):
            await verify_firebase_token('expired-token')
    
    @pytest.mark.asyncio
    @patch('app.firebase_service.auth.verify_id_token')
    async def test_verify_token_revoked(self, mock_verify):
        """Test token verification fails with revoked token"""
        mock_verify.side_effect = auth.RevokedIdTokenError("Token revoked")
        
        with pytest.raises(auth.RevokedIdTokenError, match="Firebase token has been revoked"):
            await verify_firebase_token('revoked-token')


class TestFileUpload:
    """Test file upload to Firebase Storage"""
    
    @pytest.mark.asyncio
    @patch('app.firebase_service.storage.bucket')
    async def test_upload_file_success(self, mock_bucket):
        """Test successful file upload"""
        # Create mock file
        file_content = b"test file content"
        mock_file = Mock(spec=UploadFile)
        mock_file.filename = "test.pdf"
        mock_file.read = AsyncMock(return_value=file_content)
        mock_file.seek = AsyncMock()
        
        # Mock storage bucket and blob
        mock_blob = Mock()
        mock_blob.public_url = "https://storage.googleapis.com/bucket/notes/uuid.pdf"
        mock_bucket_instance = Mock()
        mock_bucket_instance.blob.return_value = mock_blob
        mock_bucket.return_value = mock_bucket_instance
        
        result = await upload_file_to_storage(
            mock_file,
            'notes',
            {'.pdf', '.doc'}
        )
        
        download_url, filename, file_size = result
        
        assert download_url == mock_blob.public_url
        assert filename.endswith('.pdf')
        assert file_size == len(file_content)
        mock_blob.upload_from_string.assert_called_once()
        mock_blob.make_public.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_upload_file_no_filename(self):
        """Test upload fails when file has no filename"""
        mock_file = Mock(spec=UploadFile)
        mock_file.filename = None
        
        with pytest.raises(ValueError, match="File must have a filename"):
            await upload_file_to_storage(mock_file, 'notes')
    
    @pytest.mark.asyncio
    async def test_upload_file_invalid_extension(self):
        """Test upload fails with invalid file extension"""
        mock_file = Mock(spec=UploadFile)
        mock_file.filename = "test.exe"
        
        with pytest.raises(ValueError, match="File type .exe not allowed"):
            await upload_file_to_storage(
                mock_file,
                'notes',
                {'.pdf', '.doc'}
            )
    
    @pytest.mark.asyncio
    @patch('app.firebase_service.storage.bucket')
    async def test_upload_file_empty_content(self, mock_bucket):
        """Test upload fails with empty file"""
        mock_file = Mock(spec=UploadFile)
        mock_file.filename = "test.pdf"
        mock_file.read = AsyncMock(return_value=b"")
        mock_file.seek = AsyncMock()
        
        with pytest.raises(Exception, match="Failed to upload file to Firebase Storage"):
            await upload_file_to_storage(mock_file, 'notes')
    
    @pytest.mark.asyncio
    @patch('app.firebase_service.storage.bucket')
    async def test_upload_file_storage_error(self, mock_bucket):
        """Test upload handles storage errors"""
        mock_file = Mock(spec=UploadFile)
        mock_file.filename = "test.pdf"
        mock_file.read = AsyncMock(return_value=b"content")
        mock_file.seek = AsyncMock()
        
        mock_blob = Mock()
        mock_blob.upload_from_string.side_effect = Exception("Storage error")
        mock_bucket_instance = Mock()
        mock_bucket_instance.blob.return_value = mock_blob
        mock_bucket.return_value = mock_bucket_instance
        
        with pytest.raises(Exception, match="Failed to upload file to Firebase Storage"):
            await upload_file_to_storage(mock_file, 'notes')


class TestFileDownload:
    """Test file download from Firebase Storage"""
    
    @pytest.mark.asyncio
    @patch('app.firebase_service.storage.bucket')
    async def test_download_file_success(self, mock_bucket):
        """Test successful file download"""
        file_content = b"downloaded content"
        
        mock_blob = Mock()
        mock_blob.exists.return_value = True
        mock_blob.download_as_bytes.return_value = file_content
        
        mock_bucket_instance = Mock()
        mock_bucket_instance.blob.return_value = mock_blob
        mock_bucket.return_value = mock_bucket_instance
        
        result = await download_file_from_storage('notes/test.pdf')
        
        assert result == file_content
        mock_blob.exists.assert_called_once()
        mock_blob.download_as_bytes.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('app.firebase_service.storage.bucket')
    async def test_download_file_not_found(self, mock_bucket):
        """Test download fails when file does not exist"""
        mock_blob = Mock()
        mock_blob.exists.return_value = False
        
        mock_bucket_instance = Mock()
        mock_bucket_instance.blob.return_value = mock_blob
        mock_bucket.return_value = mock_bucket_instance
        
        with pytest.raises(FileNotFoundError, match="File not found in storage"):
            await download_file_from_storage('notes/nonexistent.pdf')
    
    @pytest.mark.asyncio
    @patch('app.firebase_service.storage.bucket')
    async def test_download_file_storage_error(self, mock_bucket):
        """Test download handles storage errors"""
        mock_blob = Mock()
        mock_blob.exists.return_value = True
        mock_blob.download_as_bytes.side_effect = Exception("Download error")
        
        mock_bucket_instance = Mock()
        mock_bucket_instance.blob.return_value = mock_blob
        mock_bucket.return_value = mock_bucket_instance
        
        with pytest.raises(Exception, match="Failed to download file from Firebase Storage"):
            await download_file_from_storage('notes/test.pdf')


class TestFileDelete:
    """Test file deletion from Firebase Storage"""
    
    @pytest.mark.asyncio
    @patch('app.firebase_service.storage.bucket')
    async def test_delete_file_success(self, mock_bucket):
        """Test successful file deletion"""
        mock_blob = Mock()
        mock_blob.exists.return_value = True
        
        mock_bucket_instance = Mock()
        mock_bucket_instance.blob.return_value = mock_blob
        mock_bucket.return_value = mock_bucket_instance
        
        result = await delete_file_from_storage('notes/test.pdf')
        
        assert result is True
        mock_blob.exists.assert_called_once()
        mock_blob.delete.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('app.firebase_service.storage.bucket')
    async def test_delete_file_not_found(self, mock_bucket):
        """Test delete returns False when file does not exist"""
        mock_blob = Mock()
        mock_blob.exists.return_value = False
        
        mock_bucket_instance = Mock()
        mock_bucket_instance.blob.return_value = mock_blob
        mock_bucket.return_value = mock_bucket_instance
        
        result = await delete_file_from_storage('notes/nonexistent.pdf')
        
        assert result is False
        mock_blob.exists.assert_called_once()
        mock_blob.delete.assert_not_called()
    
    @pytest.mark.asyncio
    @patch('app.firebase_service.storage.bucket')
    async def test_delete_file_storage_error(self, mock_bucket):
        """Test delete handles storage errors"""
        mock_blob = Mock()
        mock_blob.exists.return_value = True
        mock_blob.delete.side_effect = Exception("Delete error")
        
        mock_bucket_instance = Mock()
        mock_bucket_instance.blob.return_value = mock_blob
        mock_bucket.return_value = mock_bucket_instance
        
        with pytest.raises(Exception, match="Failed to delete file from Firebase Storage"):
            await delete_file_from_storage('notes/test.pdf')


class TestContentType:
    """Test content type detection"""
    
    def test_get_content_type_pdf(self):
        """Test PDF content type"""
        assert _get_content_type('.pdf') == 'application/pdf'
    
    def test_get_content_type_doc(self):
        """Test DOC content type"""
        assert _get_content_type('.doc') == 'application/msword'
    
    def test_get_content_type_docx(self):
        """Test DOCX content type"""
        assert _get_content_type('.docx') == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    
    def test_get_content_type_jpg(self):
        """Test JPG content type"""
        assert _get_content_type('.jpg') == 'image/jpeg'
    
    def test_get_content_type_png(self):
        """Test PNG content type"""
        assert _get_content_type('.png') == 'image/png'
    
    def test_get_content_type_unknown(self):
        """Test unknown extension returns default"""
        assert _get_content_type('.unknown') == 'application/octet-stream'
    
    def test_get_content_type_case_insensitive(self):
        """Test content type detection is case insensitive"""
        assert _get_content_type('.PDF') == 'application/pdf'
        assert _get_content_type('.Jpg') == 'image/jpeg'


class TestConstants:
    """Test module constants"""
    
    def test_storage_folders_defined(self):
        """Test storage folders are properly defined"""
        assert 'notes' in STORAGE_FOLDERS
        assert 'avatars' in STORAGE_FOLDERS
        assert 'chat_files' in STORAGE_FOLDERS
        assert 'complaint_attachments' in STORAGE_FOLDERS
        
        # All folders should end with /
        for folder in STORAGE_FOLDERS.values():
            assert folder.endswith('/')
    
    def test_allowed_extensions_defined(self):
        """Test allowed extensions are properly defined"""
        assert 'notes' in ALLOWED_EXTENSIONS
        assert 'avatars' in ALLOWED_EXTENSIONS
        assert 'chat_files' in ALLOWED_EXTENSIONS
        assert 'complaint_attachments' in ALLOWED_EXTENSIONS
        
        # Notes should allow document types
        assert '.pdf' in ALLOWED_EXTENSIONS['notes']
        assert '.doc' in ALLOWED_EXTENSIONS['notes']
        assert '.docx' in ALLOWED_EXTENSIONS['notes']
        
        # Avatars should allow image types
        assert '.jpg' in ALLOWED_EXTENSIONS['avatars']
        assert '.png' in ALLOWED_EXTENSIONS['avatars']
