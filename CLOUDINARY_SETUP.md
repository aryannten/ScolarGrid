# Cloudinary Setup Guide

## Why Cloudinary?
Firebase Storage requires payment, so we've switched to Cloudinary which offers:
- **25GB storage** (free tier)
- **25GB bandwidth/month** (free tier)
- Simple API for file uploads/downloads
- Perfect for a mini project like ScholarGrid

## Setup Steps

### 1. Sign Up for Cloudinary (Free)
1. Go to https://cloudinary.com/
2. Click "Sign Up for Free"
3. Create an account (use your email or sign up with Google/GitHub)

### 2. Get Your Credentials
1. After signing up, you'll be taken to the Dashboard
2. You'll see a section called "Account Details" or "Product Environment Credentials"
3. Copy these three values:
   - **Cloud Name** (e.g., `dxyz123abc`)
   - **API Key** (e.g., `123456789012345`)
   - **API Secret** (e.g., `abcdefghijklmnopqrstuvwxyz123`)

### 3. Update Your .env File
Open your `.env` file and replace the placeholder values:

```env
# ── Cloudinary (Free Cloud Storage) ───────────────────
CLOUDINARY_CLOUD_NAME=your-cloud-name-here    # Replace with your Cloud Name
CLOUDINARY_API_KEY=your-api-key-here          # Replace with your API Key
CLOUDINARY_API_SECRET=your-api-secret-here    # Replace with your API Secret
```

Example (with fake credentials):
```env
CLOUDINARY_CLOUD_NAME=dxyz123abc
CLOUDINARY_API_KEY=123456789012345
CLOUDINARY_API_SECRET=abcdefghijklmnopqrstuvwxyz123
```

### 4. Restart Your Backend
After updating `.env`, restart your FastAPI server:
```bash
uvicorn app.main:app --reload
```

## What Changed?
- ✅ Replaced Firebase Storage with Cloudinary
- ✅ Updated file upload endpoints (notes, complaint screenshots)
- ✅ Updated file deletion for admin operations
- ✅ Installed `cloudinary` package
- ✅ All tests still pass with PostgreSQL

## File Storage Folders
Files are organized in Cloudinary:
- `scholargrid/notes/` - Educational notes (PDF, DOC, PPT)
- `scholargrid/avatars/` - User profile pictures
- `scholargrid/chat_files/` - Chat attachments
- `scholargrid/complaint_attachments/` - Complaint screenshots

## Testing
Once you've added your credentials, test file upload:
1. Start the backend: `uvicorn app.main:app --reload`
2. Go to http://localhost:8000/docs
3. Try uploading a note or complaint with screenshot
4. Check your Cloudinary dashboard to see the uploaded files

## Need Help?
- Cloudinary Dashboard: https://console.cloudinary.com/
- Cloudinary Docs: https://cloudinary.com/documentation
