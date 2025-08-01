"""
Fix Failed Files in Knowledge Base

This script identifies files with 'failed' status, deletes them, and re-uploads them.
It's designed to clean up and retry failed uploads automatically.
"""

import sys
import os
import json
import time
import asyncio
import aiohttp
import aiofiles
from datetime import datetime
from tqdm import tqdm
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import MaiAgentHelper

# Configuration - Replace with your actual values
API_KEY = '<your-api-key>'
KNOWLEDGE_BASE_ID = '<your-knowledge-base-id>'   # 你的知識庫 ID
FILES_DIRECTORY = '<your-files-directory>'    # 你要上傳的檔案目錄
STATUS_REPORT_PATH = '<path-to-your-status-report>'  # Path to status scan report, e.g., 'status_scan_20250801_124703.json'

# Validation
assert API_KEY != '<your-api-key>', 'Please set your API key'
assert KNOWLEDGE_BASE_ID != '<your-knowledge-base-id>', 'Please set your knowledge base id'
assert FILES_DIRECTORY != '<your-files-directory>', 'Please set your files directory'
assert STATUS_REPORT_PATH != '<path-to-your-status-report>', 'Please set the path to your status scan report'


class FailedFilesFixer:
    def __init__(self, api_key: str, knowledge_base_id: str, files_directory: str):
        self.api_key = api_key
        self.knowledge_base_id = knowledge_base_id
        self.files_directory = files_directory
        self.maiagent_helper = MaiAgentHelper(api_key)
        self.base_url = 'https://api.maiagent.ai/api/v1/'
        
        # Results tracking
        self.deleted_files = []
        self.failed_deletions = []
        self.successful_uploads = []
        self.failed_uploads = []
    
    def load_failed_files(self, status_report_path: str):
        """Load failed files from status scan report"""
        if not os.path.exists(status_report_path):
            print(f"❌ Status report not found: {status_report_path}")
            return []
        
        try:
            with open(status_report_path, 'r') as f:
                data = json.load(f)
            
            failed_files = data.get('failed_files', [])
            print(f"📋 Found {len(failed_files)} failed files in status report")
            return failed_files
            
        except Exception as e:
            print(f"❌ Error reading status report: {e}")
            return []
    
    def delete_failed_files(self, failed_files: list):
        """Delete failed files from knowledge base"""
        if not failed_files:
            return []
        
        print("=" * 60)
        print("Deleting Failed Files")
        print("=" * 60)
        
        # Show files to be deleted
        for i, file in enumerate(failed_files[:10]):
            filename = file.get('filename', 'Unknown')
            file_id = file.get('id', 'Unknown')
            print(f"{i+1}. {filename} (ID: {file_id})")
        
        if len(failed_files) > 10:
            print(f"... and {len(failed_files) - 10} more files")
        
        print("\n" + "=" * 60)
        confirm = input("⚠️  Delete these failed files? Type 'YES' to confirm: ")
        if confirm != 'YES':
            print("❌ Deletion cancelled")
            return []
        
        print("\n🗑️  Deleting failed files...")
        
        for i, file in enumerate(failed_files):
            try:
                file_id = file['id']
                filename = file['filename']
                
                self.maiagent_helper.delete_knowledge_file(self.knowledge_base_id, file_id)
                self.deleted_files.append(file)
                print(f"✓ Deleted: {filename}")
                
                if (i + 1) % 10 == 0:
                    print(f"   Progress: {i + 1}/{len(failed_files)}")
                
                time.sleep(0.3)  # Rate limiting
                
            except Exception as e:
                # Handle API returning 500 but deletion actually succeeding
                if "500" in str(e) or "Internal Server Error" in str(e):
                    self.deleted_files.append(file)
                    print(f"✓ Deleted: {filename} (API returned 500 but likely successful)")
                else:
                    self.failed_deletions.append({'file': file, 'error': str(e)})
                    print(f"❌ Failed to delete: {filename} - {e}")
        
        print(f"\n✅ Deletion completed: {len(self.deleted_files)} deleted, {len(self.failed_deletions)} failed")
        return self.deleted_files
    
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
    
    async def reupload_files(self, deleted_files: list):
        """Re-upload the deleted files"""
        if not deleted_files:
            return
        
        print("=" * 60)
        print("Re-uploading Files")
        print("=" * 60)
        
        # Find files that exist in the directory
        files_to_upload = []
        missing_files = []
        
        for file in deleted_files:
            filename = file['filename']
            file_path = os.path.join(self.files_directory, filename)
            
            if os.path.exists(file_path):
                files_to_upload.append(file_path)
            else:
                missing_files.append(filename)
        
        print(f"📁 Files to re-upload: {len(files_to_upload)}")
        print(f"❌ Missing files: {len(missing_files)}")
        
        if missing_files:
            print(f"\nMissing files (cannot re-upload):")
            for missing in missing_files[:5]:
                print(f"  - {missing}")
            if len(missing_files) > 5:
                print(f"  ... and {len(missing_files) - 5} more")
        
        if not files_to_upload:
            print("❌ No files available for re-upload")
            return
        
        print(f"\n🔄 Starting re-upload of {len(files_to_upload)} files...")
        
        # Upload files
        connector = aiohttp.TCPConnector(limit=5)
        timeout = aiohttp.ClientTimeout(total=300)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            with tqdm(total=len(files_to_upload), desc="Re-uploading", unit="files") as pbar:
                for file_path in files_to_upload:
                    success = await self.upload_single_file(session, file_path)
                    pbar.update(1)
                    
                    if success:
                        pbar.set_postfix(success=len(self.successful_uploads), 
                                       failed=len(self.failed_uploads))
                    
                    await asyncio.sleep(0.1)
    
    def save_results(self):
        """Save operation results to log file"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'knowledge_base_id': self.knowledge_base_id,
            'files_directory': self.files_directory,
            'status_report_used': STATUS_REPORT_PATH,
            'summary': {
                'deleted_files': len(self.deleted_files),
                'failed_deletions': len(self.failed_deletions),
                'successful_uploads': len(self.successful_uploads),
                'failed_uploads': len(self.failed_uploads)
            },
            'deleted_files': self.deleted_files,
            'failed_deletions': self.failed_deletions,
            'successful_uploads': self.successful_uploads,
            'failed_uploads': self.failed_uploads
        }
        
        log_filename = f"fix_failed_files_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(log_filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        return log_filename


async def main():
    """
    Fix failed files in knowledge base
    
    This script will:
    1. Read a status scan report to identify failed files
    2. Delete the failed files from the knowledge base
    3. Re-upload the files from the local directory
    4. Save a detailed log of all operations
    
    Usage:
    1. Set your API_KEY, KNOWLEDGE_BASE_ID, FILES_DIRECTORY, and STATUS_REPORT_PATH
    2. Make sure you have a status scan report with failed files
    3. Ensure the original files exist in FILES_DIRECTORY
    4. Run: python fix_failed_files.py
    """
    
    print("Failed Files Fixer")
    print("==================")
    print(f"Knowledge Base: {KNOWLEDGE_BASE_ID}")
    print(f"Files Directory: {FILES_DIRECTORY}")
    print(f"Status Report: {STATUS_REPORT_PATH}")
    print()
    
    fixer = FailedFilesFixer(API_KEY, KNOWLEDGE_BASE_ID, FILES_DIRECTORY)
    
    # Load failed files
    failed_files = fixer.load_failed_files(STATUS_REPORT_PATH)
    if not failed_files:
        print("✅ No failed files found!")
        return
    
    # Delete failed files
    deleted_files = fixer.delete_failed_files(failed_files)
    if not deleted_files:
        print("❌ No files were deleted, stopping...")
        return
    
    # Re-upload files
    await fixer.reupload_files(deleted_files)
    
    # Save results and show summary
    log_file = fixer.save_results()
    
    print("\n" + "=" * 60)
    print("Operation Summary:")
    print("=" * 60)
    print(f"🗑️  Files deleted: {len(fixer.deleted_files)}")
    print(f"❌ Delete failures: {len(fixer.failed_deletions)}")
    print(f"✅ Files re-uploaded: {len(fixer.successful_uploads)}")
    print(f"❌ Upload failures: {len(fixer.failed_uploads)}")
    print(f"📄 Log saved to: {log_file}")
    
    if fixer.failed_uploads:
        print(f"\nUpload failures:")
        for failed in fixer.failed_uploads[:3]:
            print(f"  - {failed['filename']}: {failed['error']}")


if __name__ == '__main__':
    asyncio.run(main())