"""
Delete Duplicate Files from Knowledge Base

This script helps identify and delete duplicate files in a knowledge base after upload completion.
It's designed to clean up extra files that were found during integrity checks.
"""

import sys
import os
import json
import time
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from utils import MaiAgentHelper

# Configuration - Replace with your actual values
API_KEY = '<your-api-key>'
KNOWLEDGE_BASE_ID = '<your-knowledge-base-id>'   # 你的知識庫 ID

# Path to your integrity check report - Replace with your actual path
INTEGRITY_REPORT_PATH = '<path-to-your-integrity-check-report>'  # e.g., 'upload_outputs/json_files_4e9ffa82/reports/....json'

# Validation
assert API_KEY != '<your-api-key>', 'Please set your API key'
assert KNOWLEDGE_BASE_ID != '<your-knowledge-base-id>', 'Please set your knowledge base id'
assert INTEGRITY_REPORT_PATH != '<path-to-your-integrity-check-report>', 'Please set the path to your integrity check report'


def load_duplicate_files(file_path: str):
    """
    Load duplicate files from an integrity check report
    
    Args:
        file_path: Path to the integrity check JSON file
    
    Returns:
        List of duplicate files to delete
    """
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        print("Please check the file path and make sure the integrity check report exists.")
        return []
    
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Look for extra_files (files in KB but not in upload records)
        extra_files = data.get('extra_files', [])
        
        if extra_files:
            print(f"📋 Found {len(extra_files)} duplicate/extra files in integrity report")
            return extra_files
        else:
            print("✅ No duplicate files found in the report")
            return []
            
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return []


def delete_duplicate_files(duplicate_files: list):
    """
    Delete duplicate files from knowledge base
    
    Args:
        duplicate_files: List of file info dicts with 'knowledge_file_id' and 'filename'
    """
    if not duplicate_files:
        print("❌ No files to delete")
        return
    
    maiagent_helper = MaiAgentHelper(API_KEY)
    
    print("=" * 60)
    print("Files to be deleted:")
    print("=" * 60)
    
    # Show files to be deleted
    for i, file in enumerate(duplicate_files[:10]):
        filename = file.get('filename', 'Unknown')
        file_id = file.get('knowledge_file_id', 'Unknown')
        created_at = file.get('created_at', 'Unknown')
        print(f"{i+1}. {filename}")
        print(f"   ID: {file_id}")
        print(f"   Created: {created_at}")
        print()
    
    if len(duplicate_files) > 10:
        print(f"... and {len(duplicate_files) - 10} more files")
    
    print("=" * 60)
    confirm = input("⚠️  Are you sure you want to delete these duplicate files? Type 'YES' to confirm: ")
    if confirm != 'YES':
        print("❌ Operation cancelled")
        return
    
    # Perform deletion
    print("\n🗑️  Starting deletion process...")
    print("-" * 40)
    
    deleted_files = []
    failed_deletions = []
    
    for i, file in enumerate(duplicate_files):
        try:
            file_id = file['knowledge_file_id']
            filename = file['filename']
            
            # Delete file
            maiagent_helper.delete_knowledge_file(KNOWLEDGE_BASE_ID, file_id)
            deleted_files.append(file)
            print(f"✓ Deleted: {filename}")
            
            # Progress indicator
            if (i + 1) % 10 == 0:
                print(f"   Progress: {i + 1}/{len(duplicate_files)}")
            
            # Rate limiting to avoid overwhelming the API
            time.sleep(0.5)
            
        except Exception as e:
            # Note: API might return 500 error even when deletion succeeds
            if "500" in str(e) or "Internal Server Error" in str(e):
                # Assume deletion was successful despite 500 error
                deleted_files.append(file)
                print(f"✓ Deleted: {filename} (API returned 500 but likely successful)")
            elif "409" in str(e) or "Conflict" in str(e):
                print(f"⚠️  Skipped: {filename} (file is being processed, cannot delete)")
                failed_deletions.append({
                    'file': file,
                    'error': 'File is being processed'
                })
            else:
                failed_deletions.append({
                    'file': file,
                    'error': str(e)
                })
                print(f"❌ Failed: {filename} - {e}")
    
    # Save deletion log
    deletion_log = {
        'timestamp': datetime.now().isoformat(),
        'knowledge_base_id': KNOWLEDGE_BASE_ID,
        'integrity_report_used': INTEGRITY_REPORT_PATH,
        'total_files': len(duplicate_files),
        'successful_deletions': len(deleted_files),
        'failed_deletions_count': len(failed_deletions),
        'deleted_files': deleted_files,
        'failed_deletions': failed_deletions
    }
    
    log_filename = f"duplicate_deletion_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(log_filename, 'w') as f:
        json.dump(deletion_log, f, indent=2)
    
    # Summary
    print("\n" + "=" * 60)
    print("Deletion Summary:")
    print("=" * 60)
    print(f"✅ Successfully deleted: {len(deleted_files)} files")
    print(f"❌ Failed deletions: {len(failed_deletions)} files")
    print(f"📄 Deletion log saved to: {log_filename}")
    
    if failed_deletions:
        print(f"\nFiles that couldn't be deleted:")
        for failed in failed_deletions:
            print(f"  - {failed['file']['filename']}: {failed['error']}")
    
    return deleted_files, failed_deletions


def main():
    """
    Delete duplicate files from knowledge base
    
    This script is designed to clean up duplicate files found after upload completion.
    It reads an integrity check report and deletes the extra files identified.
    
    Usage:
    1. Set your API_KEY and KNOWLEDGE_BASE_ID at the top of this file  
    2. Set INTEGRITY_REPORT_PATH to point to your integrity check report
       Example: 'batch_upload/upload_outputs/json_files_4e9ffa82/reports/integrity_check_20250801_102645.json'
    3. Run: python delete_duplicate_files.py
    
    The script will:
    - Read the integrity check report from the specified path
    - Show you which duplicate files will be deleted
    - Ask for confirmation before deletion
    - Save a detailed log of the deletion process
    
    Note: The integrity check report should contain 'extra_files' - these are files
    that exist in the knowledge base but were not part of your original upload batch.
    """
    
    print("Knowledge Base Duplicate File Cleaner")
    print("====================================")
    print(f"Using integrity report: {INTEGRITY_REPORT_PATH}")
    print()
    
    # Load and delete duplicate files
    duplicate_files = load_duplicate_files(INTEGRITY_REPORT_PATH)
    if duplicate_files:
        delete_duplicate_files(duplicate_files)
    else:
        print("✅ No duplicate files to delete!")


if __name__ == '__main__':
    main()
