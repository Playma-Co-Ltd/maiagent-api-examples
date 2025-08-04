"""
Knowledge Base File Status Scanner

This script scans all files in a knowledge base and reports their status distribution.
It helps identify files with problematic statuses like 'initial', 'processing', or 'failed'.
"""

import json
import requests
from datetime import datetime
from tqdm import tqdm

# Configuration - Replace with your actual values
API_KEY = '<your-api-key>'
KNOWLEDGE_BASE_ID = '<your-knowledge-base-id>'   # 你的知識庫 ID
BASE_URL = 'https://api.maiagent.ai/api/v1/'

# Validation
assert API_KEY != '<your-api-key>', 'Please set your API key'
assert KNOWLEDGE_BASE_ID != '<your-knowledge-base-id>', 'Please set your knowledge base id'


class KnowledgeBaseStatusScanner:
    def __init__(self, api_key: str, knowledge_base_id: str, base_url: str = BASE_URL):
        self.api_key = api_key
        self.knowledge_base_id = knowledge_base_id
        self.base_url = base_url
        
    def scan_files_by_status(self, max_pages: int = None, page_size: int = 100):
        """
        Scan knowledge base files and categorize by status
        
        Args:
            max_pages: Maximum number of pages to scan (None for all pages)
            page_size: Number of files per page (default: 100)
        """
        headers = {'Authorization': f'Api-Key {self.api_key}'}
        
        print("=" * 60)
        print("Knowledge Base File Status Scanner")
        print("=" * 60)
        
        # Status counters
        status_count = {
            'initial': [],
            'processing': [],
            'done': [],
            'failed': [],
            'other': []
        }
        
        page = 1
        total_scanned = 0
        
        # Get total count from first page
        url = f"{self.base_url}knowledge-bases/{self.knowledge_base_id}/files/?page=1&page_size={page_size}"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        total_count = data.get('count', 0)
        per_page = len(data.get('results', []))
        total_pages = (total_count // per_page) + (1 if total_count % per_page > 0 else 0) if per_page > 0 else 1
        
        scan_pages = min(max_pages or total_pages, total_pages)
        
        print(f"Knowledge Base ID: {self.knowledge_base_id}")
        print(f"Total files: {total_count:,}")
        print(f"Total pages: {total_pages:,}")
        if max_pages:
            print(f"Will scan: {scan_pages:,} pages (limited)")
        else:
            print(f"Will scan: {scan_pages:,} pages (all)")
        print()
        
        with tqdm(total=scan_pages, desc="Scanning", unit="pages") as pbar:
            while page <= scan_pages:
                try:
                    url = f"{self.base_url}knowledge-bases/{self.knowledge_base_id}/files/?page={page}&page_size={page_size}"
                    response = requests.get(url, headers=headers, timeout=30)
                    response.raise_for_status()
                    data = response.json()
                    
                    if 'results' in data:
                        for file in data['results']:
                            status = file.get('status', 'unknown')
                            file_info = {
                                'id': file.get('id'),
                                'filename': file.get('filename'),
                                'status': status,
                                'created_at': file.get('createdAt')
                            }
                            
                            if status in status_count:
                                status_count[status].append(file_info)
                            else:
                                status_count['other'].append(file_info)
                            
                            total_scanned += 1
                    
                    pbar.update(1)
                    
                    if not data.get('next'):
                        break
                        
                    page += 1
                    
                except Exception as e:
                    print(f"\nError on page {page}: {e}")
                    break
        
        # Display and save results
        self._display_results(status_count, total_scanned)
        report_path = self._save_report(status_count, total_scanned)
        
        return status_count, report_path
    
    def _display_results(self, status_count: dict, total_scanned: int):
        """Display scan results"""
        print("\n" + "=" * 60)
        print("Scan Results:")
        print("=" * 60)
        print(f"Total scanned: {total_scanned:,} files")
        print(f"- Initial status: {len(status_count['initial']):,}")
        print(f"- Processing: {len(status_count['processing']):,}")
        print(f"- Done: {len(status_count['done']):,}")
        print(f"- Failed: {len(status_count['failed']):,}")
        print(f"- Other: {len(status_count['other']):,}")
        
        # Show problematic files
        problematic = status_count['initial'] + status_count['processing'] + status_count['failed']
        if problematic:
            print(f"\n📋 Files with issues ({len(problematic)} total):")
            print("-" * 40)
            for file in problematic[:10]:  # Show first 10
                created_time = self._format_timestamp(file['created_at'])
                print(f"• {file['filename']} ({file['status']}) - {created_time}")
            
            if len(problematic) > 10:
                print(f"... and {len(problematic) - 10} more files")
        else:
            print("\n✅ All scanned files are in 'done' status!")
    
    def _format_timestamp(self, timestamp):
        """Format timestamp for display"""
        if not timestamp:
            return "Unknown"
        try:
            if str(timestamp).isdigit():
                return datetime.fromtimestamp(int(timestamp) / 1000).strftime('%Y-%m-%d %H:%M:%S')
            return str(timestamp)
        except:
            return str(timestamp)
    
    def _save_report(self, status_count: dict, total_scanned: int):
        """Save detailed report to JSON file"""
        report = {
            'scan_time': datetime.now().isoformat(),
            'knowledge_base_id': self.knowledge_base_id,
            'total_scanned': total_scanned,
            'summary': {
                'initial': len(status_count['initial']),
                'processing': len(status_count['processing']),
                'done': len(status_count['done']),
                'failed': len(status_count['failed']),
                'other': len(status_count['other'])
            },
            'initial_files': status_count['initial'],
            'processing_files': status_count['processing'],
            'failed_files': status_count['failed'],
            'other_files': status_count['other']
        }
        
        report_path = f"status_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {report_path}")
        return report_path


def main():
    """
    Scan knowledge base file statuses
    
    This script will scan all files (or a limited number of pages) in your knowledge base
    and report the distribution of file statuses. It's useful for identifying files that
    are stuck in 'initial', 'processing', or 'failed' states.
    
    Usage:
    1. Set your API_KEY and KNOWLEDGE_BASE_ID at the top of this file
    2. Run: python scan_file_status.py
    
    Optional: Modify max_pages parameter to limit scanning to first N pages
    """
    scanner = KnowledgeBaseStatusScanner(API_KEY, KNOWLEDGE_BASE_ID)
    
    # Scan all pages (set max_pages=50 to limit to first 50 pages)
    status_count, report_path = scanner.scan_files_by_status(max_pages=None)
    
    # Print summary
    problematic_count = len(status_count['initial']) + len(status_count['processing']) + len(status_count['failed'])
    if problematic_count > 0:
        print(f"\n⚠️  Found {problematic_count} files that may need attention.")
        print(f"   Check the detailed report: {report_path}")
    else:
        print(f"\n✅ Knowledge base looks healthy!")


if __name__ == '__main__':
    main()
