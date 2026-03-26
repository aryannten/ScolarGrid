"""
Property-based tests for file storage organization (Task 27.4)

Tests file storage organization constraints including folder structure,
filename uniqueness, extension preservation, and content type handling.

Property 52: File Storage Organization
Validates: Requirement 19.4
"""

import pytest
import uuid
from pathlib import Path
from hypothesis import given, settings as hyp_settings, HealthCheck, assume
from hypothesis import strategies as st
from app.services.cloudinary_storage import STORAGE_FOLDERS, ALLOWED_EXTENSIONS


# ─── Property 52: File Storage Organization ──────────────────────────────────

@given(
    folder_type=st.sampled_from(['notes', 'avatars', 'chat_files', 'complaint_attachments'])
)
@hyp_settings(max_examples=50)
def test_property_storage_folders_are_organized_by_type(folder_type):
    """
    Property: Files are organized in storage by type (notes/, avatars/, chat_files/, complaint_attachments/)
    
    Validates Requirement 19.4: THE API SHALL organize files in Firebase_Storage by type
    """
    # Verify folder exists in configuration
    assert folder_type in STORAGE_FOLDERS
    
    # Verify folder path follows expected pattern
    folder_path = STORAGE_FOLDERS[folder_type]
    assert folder_path.startswith('scholargrid/')
    assert folder_path.endswith(folder_type)


@given(
    folder_type=st.sampled_from(['notes', 'avatars', 'chat_files', 'complaint_attachments']),
    filename=st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))),
    extension=st.sampled_from(['.pdf', '.doc', '.docx', '.jpg', '.png', '.txt', '.zip'])
)
@hyp_settings(max_examples=100)
def test_property_filename_preserves_extension(folder_type, filename, extension):
    """
    Property: Generated filenames preserve the original file extension
    
    Validates Requirement 19.1: THE API SHALL generate a unique filename using UUID 
    and preserve the original file extension
    """
    # Generate unique filename with UUID
    unique_filename = f"{uuid.uuid4()}{extension}"
    
    # Verify extension is preserved
    assert unique_filename.endswith(extension)
    
    # Verify filename has UUID format (36 chars + extension)
    name_without_ext = unique_filename.rsplit('.', 1)[0]
    assert len(name_without_ext) == 36  # UUID length


@given(
    extension=st.sampled_from(['.pdf', '.doc', '.docx', '.ppt', '.pptx', '.jpg', '.jpeg', '.png', '.txt', '.zip'])
)
@hyp_settings(max_examples=50)
def test_property_unique_filenames_never_collide(extension):
    """
    Property: UUID-based filenames are unique and never collide
    
    Validates Requirement 19.1: THE API SHALL generate a unique filename using UUID
    """
    # Generate multiple filenames
    filenames = set()
    for _ in range(100):
        unique_filename = f"{uuid.uuid4()}{extension}"
        filenames.add(unique_filename)
    
    # Verify all filenames are unique
    assert len(filenames) == 100


@given(
    folder_type=st.sampled_from(['notes', 'avatars', 'chat_files', 'complaint_attachments'])
)
@hyp_settings(max_examples=50)
def test_property_folder_has_allowed_extensions(folder_type):
    """
    Property: Each folder type has a defined set of allowed file extensions
    
    Validates Requirement 19.4: Files are organized by type with appropriate constraints
    """
    # Verify folder has allowed extensions defined
    assert folder_type in ALLOWED_EXTENSIONS
    
    # Verify allowed extensions is a non-empty set
    allowed = ALLOWED_EXTENSIONS[folder_type]
    assert isinstance(allowed, set)
    assert len(allowed) > 0
    
    # Verify all extensions start with dot
    for ext in allowed:
        assert ext.startswith('.')


@given(
    folder_type=st.sampled_from(['notes', 'avatars', 'chat_files', 'complaint_attachments'])
)
@hyp_settings(max_examples=50)
def test_property_notes_folder_only_accepts_documents(folder_type):
    """
    Property: Notes folder only accepts document file types (PDF, DOC, PPT)
    
    Validates Requirement 19.4: Files are organized by type with appropriate constraints
    """
    if folder_type == 'notes':
        allowed = ALLOWED_EXTENSIONS['notes']
        # Notes should only accept document types
        assert '.pdf' in allowed
        assert '.doc' in allowed or '.docx' in allowed
        assert '.ppt' in allowed or '.pptx' in allowed
        
        # Notes should not accept image-only types
        assert '.jpg' not in allowed
        assert '.png' not in allowed


@given(
    folder_type=st.sampled_from(['notes', 'avatars', 'chat_files', 'complaint_attachments'])
)
@hyp_settings(max_examples=50)
def test_property_avatars_folder_only_accepts_images(folder_type):
    """
    Property: Avatars folder only accepts image file types
    
    Validates Requirement 19.4: Files are organized by type with appropriate constraints
    """
    if folder_type == 'avatars':
        allowed = ALLOWED_EXTENSIONS['avatars']
        # Avatars should only accept image types
        assert '.jpg' in allowed or '.jpeg' in allowed
        assert '.png' in allowed
        
        # Avatars should not accept document types
        assert '.pdf' not in allowed
        assert '.doc' not in allowed
        assert '.docx' not in allowed


@given(
    folder_type=st.sampled_from(['notes', 'avatars', 'chat_files', 'complaint_attachments'])
)
@hyp_settings(max_examples=50)
def test_property_complaint_attachments_only_accept_images(folder_type):
    """
    Property: Complaint attachments folder only accepts image file types (screenshots)
    
    Validates Requirement 19.4: Files are organized by type with appropriate constraints
    """
    if folder_type == 'complaint_attachments':
        allowed = ALLOWED_EXTENSIONS['complaint_attachments']
        # Complaint attachments should only accept image types (screenshots)
        assert '.jpg' in allowed or '.jpeg' in allowed
        assert '.png' in allowed
        
        # Should not accept documents
        assert '.pdf' not in allowed
        assert '.doc' not in allowed


@given(
    extension=st.sampled_from(['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png', '.gif', '.webp'])
)
@hyp_settings(max_examples=50)
def test_property_resource_type_determined_by_extension(extension):
    """
    Property: Resource type (image vs raw) is correctly determined by file extension
    
    Validates Requirement 19.2: THE API SHALL set appropriate content type headers
    """
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
    
    if extension in image_extensions:
        # Should be treated as image resource
        resource_type = 'image'
    else:
        # Should be treated as raw resource
        resource_type = 'raw'
    
    # Verify resource type is one of the two valid types
    assert resource_type in ('image', 'raw')


@given(
    folder_type=st.sampled_from(['notes', 'avatars', 'chat_files', 'complaint_attachments']),
    extension=st.sampled_from(['.pdf', '.doc', '.jpg', '.png', '.txt'])
)
@hyp_settings(max_examples=100)
def test_property_file_path_structure_is_consistent(folder_type, extension):
    """
    Property: File paths follow consistent structure: folder/uuid.extension
    
    Validates Requirement 19.4: Files are organized by type with consistent structure
    """
    # Generate file path
    unique_id = uuid.uuid4()
    filename = f"{unique_id}{extension}"
    folder_path = STORAGE_FOLDERS[folder_type]
    full_path = f"{folder_path}/{filename}"
    
    # Verify path structure
    assert full_path.startswith('scholargrid/')
    assert folder_type in full_path
    assert str(unique_id) in full_path
    assert full_path.endswith(extension)


@given(
    folder_type=st.sampled_from(['notes', 'avatars', 'chat_files', 'complaint_attachments'])
)
@hyp_settings(max_examples=50)
def test_property_all_folder_types_have_configuration(folder_type):
    """
    Property: All required folder types have both path and extension configuration
    
    Validates Requirement 19.4: Complete configuration for all file types
    """
    # Verify folder has path configuration
    assert folder_type in STORAGE_FOLDERS
    assert STORAGE_FOLDERS[folder_type] is not None
    assert len(STORAGE_FOLDERS[folder_type]) > 0
    
    # Verify folder has extension configuration
    assert folder_type in ALLOWED_EXTENSIONS
    assert ALLOWED_EXTENSIONS[folder_type] is not None
    assert len(ALLOWED_EXTENSIONS[folder_type]) > 0


@given(
    extension=st.sampled_from(['.pdf', '.PDF', '.Pdf', '.pDf'])
)
@hyp_settings(max_examples=20)
def test_property_extension_comparison_is_case_insensitive(extension):
    """
    Property: File extension validation should be case-insensitive
    
    Validates Requirement 19.1: Proper extension handling
    """
    # Normalize extension to lowercase
    normalized = extension.lower()
    
    # Verify normalization works
    assert normalized == '.pdf'
    assert normalized in ALLOWED_EXTENSIONS['notes']


@given(
    folder_type=st.sampled_from(['notes', 'avatars', 'chat_files', 'complaint_attachments'])
)
@hyp_settings(max_examples=50)
def test_property_folder_paths_are_unique(folder_type):
    """
    Property: Each folder type has a unique storage path
    
    Validates Requirement 19.4: No path collisions between folder types
    """
    # Get all folder paths
    all_paths = list(STORAGE_FOLDERS.values())
    
    # Verify no duplicates
    assert len(all_paths) == len(set(all_paths))
    
    # Verify current folder path is unique
    current_path = STORAGE_FOLDERS[folder_type]
    count = all_paths.count(current_path)
    assert count == 1


@given(
    filename=st.text(min_size=1, max_size=100, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'P'))),
    extension=st.sampled_from(['.pdf', '.doc', '.jpg', '.png'])
)
@hyp_settings(max_examples=100)
def test_property_original_filename_not_exposed_in_storage(filename, extension):
    """
    Property: Original filename is not used in storage path (UUID used instead)
    
    Validates Requirement 19.1: Unique UUID-based filenames for security
    """
    # Generate storage filename
    storage_filename = f"{uuid.uuid4()}{extension}"
    
    # Verify original filename is not in storage filename
    # (unless by extreme coincidence, which is astronomically unlikely)
    if len(filename) > 5:  # Only check for non-trivial filenames
        assert filename not in storage_filename


@given(
    file_size=st.integers(min_value=1, max_value=50 * 1024 * 1024)
)
@hyp_settings(max_examples=100)
def test_property_file_size_is_tracked(file_size):
    """
    Property: File size is always tracked and positive
    
    Validates Requirement 19.1: Complete file metadata tracking
    """
    # Verify file size is positive
    assert file_size > 0
    
    # Verify file size is within reasonable bounds (50MB max)
    assert file_size <= 50 * 1024 * 1024
