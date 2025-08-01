"""
Upload Missing Files to Knowledge Base

This script identifies missing files from an integrity check report and uploads them.
It's designed to upload files that were supposed to be uploaded but are missing from the knowledge base.
"""

import os
import json
import asyncio
import aiohttp
import aiofiles
from datetime import datetime
from tqdm import tqdm

# Configuration - Replace with your actual values
API_KEY = '<your-api-key>'
KNOWLEDGE_BASE_ID = '<your-knowledge-base-id>'   # 你的知識庫 ID
FILES_DIRECTORY = '<your-files-directory>'    # 你要上傳的檔案目錄
INTEGRITY_REPORT_PATH = '<path-to-your-integrity-check-report>'  # Path to integrity check report

# Validation
assert API_KEY != '<your-api-key>', 'Please set your API key'
assert KNOWLEDGE_BASE_ID != '<your-knowledge-base-id>', 'Please set your knowledge base id'
assert FILES_DIRECTORY != '<your-files-directory>', 'Please set your files directory'
assert INTEGRITY_REPORT_PATH != '<path-to-your-integrity-check-report>', 'Please set the path to your integrity check report'


class MissingFilesUploader:
    def __init__(self, api_key: str, knowledge_base_id: str, files_directory: str):
        self.api_key = api_key
        self.knowledge_base_id = knowledge_base_id
        self.files_directory = files_directory
        self.base_url = 'https://api.maiagent.ai/api/v1/'
        
        # Results tracking
        self.successful_uploads = []
        self.failed_uploads = []
    
    def load_missing_files(self, integrity_report_path: str):
        """
        Load missing files from an integrity check report
        
        Args:
            integrity_report_path: Path to the integrity check JSON file
        
        Returns:
            List of missing files to upload
        """
        if not os.path.exists(integrity_report_path):
            print(f"❌ Integrity report not found: {integrity_report_path}")
            print("Please check the file path and make sure the integrity check report exists.")
            return []
        
        try:
            with open(integrity_report_path, 'r') as f:
                data = json.load(f)
            
            # Look for missing_files (files in upload records but not in KB)
            missing_files = data.get('missing_files', [])
            
            if missing_files:
                print(f"📋 Found {len(missing_files)} missing files in integrity report")
                return missing_files
            else:
                print("✅ No missing files found in the report")
                return []
                
        except Exception as e:
            print(f"❌ Error reading integrity report: {e}")
            return []
    
    async def get_upload_url(self, session: aiohttp.ClientSession, file_path: str):
        """Get presigned upload URL"""
        url = f"{self.base_url}upload-presigned-url/"
        headers = {
            'Authorization': f'Api-Key {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        file_size = os.path.getsize(file_path)
        filename = os.path.basename(file_path)
        
        payload = {
            'filename': filename,
            'modelName': 'chatbot-file',
            'fieldName': 'file',
            'fileSize': file_size
        }
        
        async with session.post(url, headers=headers, json=payload) as response:
            response.raise_for_status()
            return await response.json()
    
    async def upload_to_s3(self, session: aiohttp.ClientSession, file_path: str, upload_info: dict):
        """Upload file to S3"""
        async with aiofiles.open(file_path, 'rb') as f:
            file_data = await f.read()
        
        data = aiohttp.FormData()
        for key, value in upload_info['fields'].items():
            data.add_field(key, value)
        
        data.add_field('file', file_data, 
                      filename=os.path.basename(file_path),
                      content_type='application/octet-stream')
        
        upload_url = upload_info['url']
        
        async with session.post(upload_url, data=data) as response:
            if response.status == 204:
                return upload_info['fields']['key']
            else:
                error_text = await response.text()
                raise Exception(f"S3 upload failed: {response.status} - {error_text}")
    
    async def register_file(self, session: aiohttp.ClientSession, file_key: str, original_filename: str):
        """Register file to knowledge base"""
        url = f"{self.base_url}knowledge-bases/{self.knowledge_base_id}/files/"
        headers = {'Authorization': f'Api-Key {self.api_key}'}
        
        payload = {
            'files': [{
                'file': file_key,
                'filename': original_filename
            }]
        }
        
        async with session.post(url, headers=headers, json=payload) as response:
            response.raise_for_status()
            return await response.json()
    
    async def upload_single_file(self, session: aiohttp.ClientSession, file_path: str):
        """Upload a single file"""
        try:
            upload_info = await self.get_upload_url(session, file_path)
            file_key = await self.upload_to_s3(session, file_path, upload_info)
            original_filename = os.path.basename(file_path)
            response = await self.register_file(session, file_key, original_filename)
            
            # Extract new file ID
            new_file_id = None
            if response and isinstance(response, list) and len(response) > 0 and 'id' in response[0]:
                new_file_id = response[0]['id']
            
            self.successful_uploads.append({
                'file_path': file_path,
                'filename': original_filename,
                'new_file_id': new_file_id,
                'upload_time': datetime.now().isoformat()
            })
            
            return True
            
        except Exception as e:
            self.failed_uploads.append({
                'file_path': file_path,
                'filename': os.path.basename(file_path),
                'error': str(e),
                'upload_time': datetime.now().isoformat()
            })
            return False
    
    async def upload_missing_files(self, missing_files: list):
        """
        Upload missing files to knowledge base
        
        Args:
            missing_files: List of missing file info dicts with 'filename' and 'filepath'
        """
        if not missing_files:
            print("❌ No files to upload")
            return
        
        print("=" * 60)
        print("Files to be uploaded:")
        print("=" * 60)
        
        # Check which files exist and prepare upload list
        files_to_upload = []
        files_not_found = []
        
        for file in missing_files:
            filename = file.get('filename', 'Unknown')
            filepath = file.get('filepath', '')
            
            # Try both the filepath from report and files_directory + filename
            possible_paths = [
                filepath,
                os.path.join(self.files_directory, filename)
            ]
            
            file_found = False
            for path in possible_paths:
                if path and os.path.exists(path):
                    files_to_upload.append(path)
                    print(f"✓ Found: {filename}")
                    file_found = True
                    break
            
            if not file_found:
                files_not_found.append(filename)
                print(f"❌ Not found: {filename}")
        
        print("\n" + "=" * 50)
        print(f"📁 Files ready to upload: {len(files_to_upload)}")
        print(f"❌ Files not found: {len(files_not_found)}")
        
        if files_not_found:
            print(f"\nFiles not found in directory:")
            for missing in files_not_found[:5]:
                print(f"  - {missing}")
            if len(files_not_found) > 5:
                print(f"  ... and {len(files_not_found) - 5} more")
        
        if not files_to_upload:
            print("❌ No files available for upload")
            return
        
        print("\n" + "=" * 60)
        confirm = input("⚠️  Upload these missing files? Type 'YES' to confirm: ")
        if confirm != 'YES':
            print("❌ Upload cancelled")
            return
        
        # Perform upload
        print(f"\n📤 Starting upload of {len(files_to_upload)} files...")
        
        connector = aiohttp.TCPConnector(limit=5)  # Limit concurrent uploads
        timeout = aiohttp.ClientTimeout(total=300)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            with tqdm(total=len(files_to_upload), desc="Uploading", unit="files") as pbar:
                for file_path in files_to_upload:
                    success = await self.upload_single_file(session, file_path)
                    pbar.update(1)
                    
                    if success:
                        pbar.set_postfix(success=len(self.successful_uploads), 
                                       failed=len(self.failed_uploads))
                    
                    # Rate limiting
                    await asyncio.sleep(0.1)
        
        # Save upload results
        self._save_upload_results()
    
    def _save_upload_results(self):
        """Save upload results to log file"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'knowledge_base_id': self.knowledge_base_id,
            'files_directory': self.files_directory,
            'integrity_report_used': INTEGRITY_REPORT_PATH,
            'total_files': len(self.successful_uploads) + len(self.failed_uploads),
            'successful_uploads': len(self.successful_uploads),
            'failed_uploads': len(self.failed_uploads),
            'successful_uploads_details': self.successful_uploads,
            'failed_uploads_details': self.failed_uploads
        }
        
        log_filename = f"missing_files_upload_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(log_filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n📄 Upload log saved to: {log_filename}")
        return log_filename


async def main():
    """
    Upload missing files to knowledge base
    
    This script is designed to upload files that are missing from the knowledge base
    based on an integrity check report.
    
    Usage:
    1. Set your API_KEY, KNOWLEDGE_BASE_ID, FILES_DIRECTORY, and INTEGRITY_REPORT_PATH
    2. Make sure you have an integrity check report with missing_files
    3. Ensure the missing files exist in FILES_DIRECTORY  
    4. Run: python upload_missing_files.py
    
    The script will:
    - Read the integrity check report from the specified path
    - Check which missing files exist in your local directory
    - Show you which files will be uploaded
    - Ask for confirmation before upload
    - Save a detailed log of the upload process
    
    Note: The integrity check report should contain 'missing_files' - these are files
    that were supposed to be uploaded but are missing from the knowledge base.
    """
    
    print("Missing Files Uploader")
    print("=====================")
    print(f"Knowledge Base: {KNOWLEDGE_BASE_ID}")
    print(f"Files Directory: {FILES_DIRECTORY}")
    print(f"Integrity Report: {INTEGRITY_REPORT_PATH}")
    print()
    
    uploader = MissingFilesUploader(API_KEY, KNOWLEDGE_BASE_ID, FILES_DIRECTORY)
    
    # Load missing files from integrity report
    missing_files = uploader.load_missing_files(INTEGRITY_REPORT_PATH)
    
    if missing_files:
        await uploader.upload_missing_files(missing_files)
        
        # Show summary
        print("\n" + "=" * 60)
        print("Upload Summary:")
        print("=" * 60)
        print(f"✅ Successfully uploaded: {len(uploader.successful_uploads)} files")
        print(f"❌ Failed uploads: {len(uploader.failed_uploads)} files")
        
        if uploader.failed_uploads:
            print(f"\nUpload failures:")
            for failed in uploader.failed_uploads[:5]:
                print(f"  - {failed['filename']}: {failed['error']}")
    else:
        print("✅ No missing files to upload!")


if __name__ == '__main__':
    asyncio.run(main())