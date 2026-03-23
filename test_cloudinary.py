"""
Quick test script to verify Cloudinary credentials are working
Run this to test Cloudinary upload without needing authentication
"""

import cloudinary
import cloudinary.uploader
from pathlib import Path

# Your Cloudinary credentials
cloudinary.config(
    cloud_name="djm7er1m9",
    api_key="882535745655684",
    api_secret="PQ2CYk2MR28fP1Z4oizU81nrH0s",
    secure=True
)

def test_upload():
    """Test uploading a simple text file to Cloudinary"""
    print("Testing Cloudinary upload...")
    
    # Create a test file
    test_content = b"This is a test file for Cloudinary upload"
    
    try:
        # Upload to Cloudinary
        result = cloudinary.uploader.upload(
            test_content,
            folder="scholargrid/notes",
            public_id="test_upload",
            resource_type="raw"
        )
        
        print("✅ Upload successful!")
        print(f"File URL: {result['secure_url']}")
        print(f"Public ID: {result['public_id']}")
        print(f"\nCloudinary is working correctly! 🎉")
        
        # Clean up - delete the test file
        cloudinary.uploader.destroy(result['public_id'], resource_type='raw')
        print("\n✅ Test file cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return False

if __name__ == "__main__":
    test_upload()
