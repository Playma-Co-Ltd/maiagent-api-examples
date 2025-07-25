import os
import time
import json
import asyncio
import aiohttp
import aiofiles
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import logging
from collections import deque
import signal
import sys
import threading
from tqdm import tqdm


API_KEY = '<your-api-key>'
KNOWLEDGE_BASE_ID = '<your-knowledge-base-id>'   # 你的知識庫 ID
FILES_DIRECTORY = '<your-files-directory>'    # 你要上傳的檔案目錄 

@dataclass
class UploadConfig:
    max_concurrent_uploads: int = 10
    max_retries: int = 3
    retry_delay: float = 2.0
    timeout_seconds: int = 300
    
    
class UploadStatus(Enum):
    PENDING = "pending"
    UPLOADING = "uploading"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class FileUploadTask:
    file_path: str
    file_size: int
    status: UploadStatus = UploadStatus.PENDING
    error_message: Optional[str] = None
    upload_time: Optional[float] = None
    retry_count: int = 0
    knowledge_file_id: Optional[str] = None  # 記錄上傳後的 knowledge file ID


# ProgressTracker 已經被 tqdm 取代，不再需要此類別


class BatchFileUploaderAdvanced:
    def __init__(self, api_key: str, knowledge_base_id: str, config: UploadConfig, source_directory: str = None):
        self.api_key = api_key
        self.knowledge_base_id = knowledge_base_id
        self.config = config
        self.base_url = 'https://api.maiagent.ai/api/v1/'
        self.source_directory = source_directory
        
        # 使用線程鎖來防止並發寫入 checkpoint 的問題
        self._checkpoint_lock = threading.Lock()
        self._completed_lock = threading.Lock()
        
        # 設定輸出資料夾結構 - 使用來源資料夾名稱和知識庫ID組合
        if source_directory:
            folder_name = os.path.basename(os.path.normpath(source_directory))
        else:
            folder_name = 'default'
        
        # 創建唯一的輸出目錄：資料夾名稱_知識庫ID
        unique_dir_name = f"{folder_name}_{knowledge_base_id[:8]}"
        # 輸出到與程式同一目錄下
        self.output_dir = os.path.join(os.path.dirname(__file__), 'upload_outputs', unique_dir_name)
        self.checkpoint_dir = os.path.join(self.output_dir, 'checkpoints')
        self.log_dir = os.path.join(self.output_dir, 'logs')
        self.report_dir = os.path.join(self.output_dir, 'reports')
        
        # 建立所有必要的資料夾
        os.makedirs(self.checkpoint_dir, exist_ok=True)
        os.makedirs(self.log_dir, exist_ok=True)
        os.makedirs(self.report_dir, exist_ok=True)
        
        self.tasks_queue = deque()
        self.completed_tasks = []
        self.failed_tasks = []
        # 使用固定的 checkpoint 檔名
        self.checkpoint_file = os.path.join(self.checkpoint_dir, "upload_checkpoint.json")
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(os.path.join(self.log_dir, f"upload_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        self._shutdown = False
        signal.signal(signal.SIGINT, self._signal_handler)
        
    def _signal_handler(self, signum, frame):
        self.logger.info("Received interrupt signal. Saving checkpoint...")
        self._shutdown = True
        self.save_checkpoint()
        sys.exit(0)
    
    def scan_files(self, directory: str) -> List[FileUploadTask]:
        """掃描目錄並建立上傳任務列表"""
        tasks = []
        for root, _, files in os.walk(directory):
            for file in files:
                if not file.startswith('.'):
                    file_path = os.path.join(root, file)
                    try:
                        file_size = os.path.getsize(file_path)
                        tasks.append(FileUploadTask(file_path, file_size))
                    except OSError as e:
                        self.logger.warning(f"Cannot access file {file_path}: {e}")
        
        return tasks
    
    def load_checkpoint(self) -> Optional[Dict[str, Any]]:
        """載入檢查點以恢復中斷的上傳"""
        if not os.path.exists(self.checkpoint_file):
            return None
            
        try:
            with open(self.checkpoint_file, 'r') as f:
                checkpoint_data = json.load(f)
                completed_count = len(checkpoint_data.get('completed_files', []))
                self.logger.info(f"Loaded checkpoint with {completed_count} completed files")
                return checkpoint_data
        except Exception as e:
            self.logger.error(f"Failed to load checkpoint: {e}")
            return None
    
    def save_checkpoint(self):
        """儲存當前進度 - 累積更新已完成檔案"""
        with self._checkpoint_lock:
            # 載入現有的 checkpoint（如果存在）
            existing_completed = set()
            existing_failed = []
        
        if os.path.exists(self.checkpoint_file):
            try:
                with open(self.checkpoint_file, 'r') as f:
                    existing_data = json.load(f)
                    existing_completed = set(existing_data.get('completed_files', []))
                    existing_failed = existing_data.get('failed_files', [])
            except Exception as e:
                self.logger.warning(f"Could not read existing checkpoint: {e}")
        
        # 合併新的已完成檔案
        all_completed = existing_completed
        all_completed.update([task.file_path for task in self.completed_tasks])
        
        # 合併失敗檔案（去除重複）
        failed_paths = set(item[0] if isinstance(item, (list, tuple)) else item for item in existing_failed)
        for task in self.failed_tasks:
            if task.file_path not in failed_paths:
                existing_failed.append((task.file_path, task.error_message))
                failed_paths.add(task.file_path)
        
        # 載入現有的 file_id_mapping（如果存在）
        existing_file_id_mapping = {}
        if os.path.exists(self.checkpoint_file):
            try:
                with open(self.checkpoint_file, 'r') as f:
                    existing_data = json.load(f)
                    existing_file_id_mapping = existing_data.get('file_id_mapping', {})
            except Exception as e:
                self.logger.warning(f"Could not read existing file_id_mapping: {e}")
        
        # 合併新的 file_id_mapping
        file_id_mapping = existing_file_id_mapping.copy()
        for task in self.completed_tasks:
            if task.knowledge_file_id:
                file_id_mapping[task.file_path] = task.knowledge_file_id
        
        checkpoint_data = {
            'timestamp': datetime.now().isoformat(),
            'completed_files': list(all_completed),
            'file_id_mapping': file_id_mapping,  # 新增：檔案路徑到 knowledge_file_id 的映射
            'failed_files': existing_failed,
            'pending_files': [task.file_path for task in self.tasks_queue]
        }
        
        with open(self.checkpoint_file, 'w') as f:
            json.dump(checkpoint_data, f, indent=2)
        
        total_completed = len(all_completed)
        # 只在整百時顯示日誌，減少輸出
        if total_completed % 100 == 0:
            self.logger.info(f"Checkpoint saved with {total_completed} total completed files")
    
    async def get_upload_url(self, session: aiohttp.ClientSession, file_path: str) -> Dict[str, Any]:
        """獲取預簽名上傳 URL"""
        url = f"{self.base_url}upload-presigned-url/"
        headers = {
            'Authorization': f'Api-Key {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        file_size = os.path.getsize(file_path)
        filename = os.path.basename(file_path)
        
        payload = {
            'filename': filename,
            'modelName': 'chatbot-file',  # 知識庫檔案使用 chatbot-file
            'fieldName': 'file',
            'fileSize': file_size
        }
        
        # 移除詳細調試輸出，只在錯誤時顯示
        
        async with session.post(url, headers=headers, json=payload) as response:
            response.raise_for_status()
            return await response.json()
    
    async def upload_to_s3(self, session: aiohttp.ClientSession, file_path: str, upload_info: Dict[str, Any]) -> str:
        """上傳檔案到 S3"""
        async with aiofiles.open(file_path, 'rb') as f:
            file_data = await f.read()
        
        # 準備 multipart form data
        data = aiohttp.FormData()
        
        # 添加所有必要的 fields
        for key, value in upload_info['fields'].items():
            data.add_field(key, value)
        
        # 添加檔案（必須在其他欄位之後）
        data.add_field('file', file_data, 
                      filename=os.path.basename(file_path),
                      content_type='application/octet-stream')
        
        # 使用正確的 URL
        upload_url = upload_info.get('url', self.base_url.replace('/api/v1/', ''))
        
        async with session.post(upload_url, data=data) as response:
            if response.status == 204:
                return upload_info['fields']['key']
            else:
                error_text = await response.text()
                raise Exception(f"S3 upload failed: {response.status} - {error_text}")
    
    async def register_file(self, session: aiohttp.ClientSession, file_key: str, original_filename: str) -> Dict[str, Any]:
        """註冊檔案到知識庫"""
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
    
    async def upload_single_file(self, session: aiohttp.ClientSession, task: FileUploadTask) -> FileUploadTask:
        """上傳單個檔案的完整流程"""
        start_time = time.time()
        
        for retry in range(self.config.max_retries):
            try:
                task.status = UploadStatus.UPLOADING
                
                upload_info = await self.get_upload_url(session, task.file_path)
                
                file_key = await self.upload_to_s3(session, task.file_path, upload_info)
                
                original_filename = os.path.basename(task.file_path)
                response = await self.register_file(session, file_key, original_filename)
                
                # 從響應中提取 knowledge_file_id (響應是一個陣列)
                if response and isinstance(response, list) and len(response) > 0 and 'id' in response[0]:
                    task.knowledge_file_id = response[0]['id']
                
                task.status = UploadStatus.SUCCESS
                task.upload_time = time.time() - start_time
                
                # 使用線程鎖來確保安全地添加到完成列表
                with self._completed_lock:
                    # 再次檢查是否已經在完成列表中
                    if not any(t.file_path == task.file_path for t in self.completed_tasks):
                        self.completed_tasks.append(task)
                        self.save_checkpoint()
                
                return task
                
            except Exception as e:
                task.retry_count = retry + 1
                if retry < self.config.max_retries - 1:
                    await asyncio.sleep(self.config.retry_delay * (retry + 1))
                else:
                    task.status = UploadStatus.FAILED
                    task.error_message = str(e)
                    self.logger.error(f"Failed to upload {task.file_path}: {e}")
        
        return task
    
    async def upload_batch_async(self, tasks: List[FileUploadTask], progress_bar: tqdm):
        """異步批量上傳，使用 tqdm 顯示進度"""
        semaphore = asyncio.Semaphore(self.config.max_concurrent_uploads)
        
        async def upload_with_semaphore(task):
            async with semaphore:
                result = await self.upload_single_file(session, task)
                # 從待處理佇列中移除已處理的任務
                if result.status == UploadStatus.SUCCESS:
                    with self._completed_lock:
                        # 從 tasks_queue 中移除已完成的任務
                        try:
                            self.tasks_queue.remove(task)
                        except ValueError:
                            pass  # 任務可能已被移除
                
                # 更新進度條
                progress_bar.update(1)
                if result.status == UploadStatus.SUCCESS:
                    progress_bar.set_postfix(success=progress_bar.n - len(self.failed_tasks), 
                                           failed=len(self.failed_tasks), 
                                           refresh=True)
                return result
        
        connector = aiohttp.TCPConnector(limit=self.config.max_concurrent_uploads)
        timeout = aiohttp.ClientTimeout(total=self.config.timeout_seconds)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            upload_tasks = []
            
            for task in tasks:
                if self._shutdown:
                    break
                upload_tasks.append(upload_with_semaphore(task))
            
            results = await asyncio.gather(*upload_tasks, return_exceptions=True)
            
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    tasks[i].status = UploadStatus.FAILED
                    tasks[i].error_message = str(result)
                    self.failed_tasks.append(tasks[i])
                    # 從待處理佇列中移除失敗的任務
                    with self._completed_lock:
                        try:
                            self.tasks_queue.remove(tasks[i])
                        except ValueError:
                            pass
                elif result.status == UploadStatus.SUCCESS:
                    # 成功的任務已經在 upload_single_file 中添加到 completed_tasks 並儲存了 checkpoint
                    pass
                else:
                    self.failed_tasks.append(result)
                    # 從待處理佇列中移除失敗的任務
                    with self._completed_lock:
                        try:
                            self.tasks_queue.remove(result)
                        except ValueError:
                            pass
    
    async def get_all_knowledge_files(self) -> Dict[str, Dict[str, Any]]:
        """獲取知識庫中所有檔案的詳細資訊，返回以 id 為 key 的字典"""
        all_files = {}
        page = 1
        
        try:
            import requests
            from tqdm.contrib.logging import logging_redirect_tqdm
            import datetime
            
            self.logger.info("Fetching knowledge base files...")
            
            # 先獲取第一頁來了解總數
            url = f"{self.base_url}knowledge-bases/{self.knowledge_base_id}/files/?page=1"
            headers = {'Authorization': f'Api-Key {self.api_key}'}
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            first_page = response.json()
            
            # 估算總頁數（如果有 count 欄位）
            total_count = first_page.get('count', 0)
            per_page = len(first_page.get('results', []))
            estimated_pages = (total_count // per_page) + (1 if total_count % per_page > 0 else 0) if per_page > 0 else 1
            
            self.logger.info(f"Estimated {total_count} files across {estimated_pages} pages")
            
            # 使用 tqdm 顯示分頁進度
            with logging_redirect_tqdm():
                with tqdm(total=estimated_pages, desc="Fetching KB pages", unit="pages") as pbar:
                    
                    # 處理第一頁
                    if 'results' in first_page:
                        for file in first_page['results']:
                            file_id = file.get('id', '')
                            filename = file.get('filename', '')
                            if file_id:
                                # createdAt 是時間戳，轉換為可讀格式
                                created_at = file.get('createdAt', '')
                                if created_at and str(created_at).isdigit():
                                    created_at = datetime.datetime.fromtimestamp(int(created_at) / 1000).isoformat()
                                
                                all_files[file_id] = {
                                    'id': file_id,
                                    'filename': filename,
                                    'created_at': created_at,
                                    'status': file.get('status', '')
                                }
                    pbar.update(1)
                    
                    # 處理後續頁面
                    page = 2
                    while first_page.get('next'):
                        url = f"{self.base_url}knowledge-bases/{self.knowledge_base_id}/files/?page={page}"
                        response = requests.get(url, headers=headers, timeout=30)
                        response.raise_for_status()
                        data = response.json()
                        
                        if 'results' in data:
                            for file in data['results']:
                                file_id = file.get('id', '')
                                filename = file.get('filename', '')
                                if file_id:
                                    created_at = file.get('createdAt', '')
                                    if created_at and str(created_at).isdigit():
                                        created_at = datetime.datetime.fromtimestamp(int(created_at) / 1000).isoformat()
                                    
                                    all_files[file_id] = {
                                        'id': file_id,
                                        'filename': filename,
                                        'created_at': created_at,
                                        'status': file.get('status', '')
                                    }
                        
                        pbar.update(1)
                        
                        if not data.get('next'):
                            break
                        page += 1
                        first_page = data  # 更新用於檢查 next
            
            self.logger.info(f"Successfully fetched {len(all_files)} files from knowledge base")
            return all_files
            
        except Exception as e:
            self.logger.error(f"Failed to get knowledge base files: {e}")
            return all_files
    
    async def check_upload_integrity(self):
        """檢查上傳完整性，識別重複和漏傳的檔案"""
        self.logger.info("Checking upload integrity...")
        
        # 獲取知識庫中所有檔案 (以 ID 為 key)
        kb_files = await self.get_all_knowledge_files()
        kb_file_ids = set(kb_files.keys())
        
        # 從 checkpoint 載入所有已上傳的檔案
        checkpoint = self.load_checkpoint()
        if not checkpoint:
            self.logger.warning("No checkpoint found for integrity check")
            return
            
        uploaded_files = set(checkpoint.get('completed_files', []))
        file_id_mapping = checkpoint.get('file_id_mapping', {})
        
        # 從 checkpoint 中獲取所有上傳的 file IDs
        uploaded_file_ids = set(file_id_mapping.values())
        
        # 檢查漏傳（在 checkpoint 但不在知識庫中的 ID）
        missing_ids = uploaded_file_ids - kb_file_ids
        missing_files = []
        for filepath, file_id in file_id_mapping.items():
            if file_id in missing_ids:
                missing_files.append({
                    'filename': os.path.basename(filepath),
                    'filepath': filepath,
                    'knowledge_file_id': file_id
                })
        
        # 檢查額外檔案（在知識庫但不在 checkpoint 記錄中）
        extra_ids = kb_file_ids - uploaded_file_ids
        extra_files = []
        for file_id in extra_ids:
            if file_id in kb_files:
                extra_files.append({
                    'filename': kb_files[file_id]['filename'],
                    'knowledge_file_id': file_id,
                    'created_at': kb_files[file_id]['created_at']
                })
        
        # 輸出結果
        if missing_files:
            self.logger.warning(f"Found {len(missing_files)} missing files (uploaded but not in KB):")
            self.logger.warning("These files may have been uploaded but later deleted by user, or upload failed:")
            for file in missing_files[:10]:  # 只顯示前10個
                self.logger.warning(f"  - {file['filename']} (ID: {file['knowledge_file_id']})")
            if len(missing_files) > 10:
                self.logger.warning(f"  ... and {len(missing_files) - 10} more missing files")
        
        if extra_files:
            self.logger.info(f"Found {len(extra_files)} extra files in KB (not in upload records):")
            self.logger.info("These files may be duplicates or uploaded by other methods:")
            for file in extra_files[:10]:
                self.logger.info(f"  - {file['filename']} (ID: {file['knowledge_file_id']})")
        
        # 儲存完整性檢查報告
        integrity_report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_kb_files': len(kb_files),
                'total_uploaded_files': len(uploaded_files),
                'total_uploaded_ids': len(uploaded_file_ids),
                'missing': len(missing_files),
                'extra': len(extra_files)
            },
            'missing_files': missing_files,
            'extra_files': extra_files
        }
        
        report_file = os.path.join(self.report_dir, f"integrity_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(report_file, 'w') as f:
            json.dump(integrity_report, f, indent=2)
        
        self.logger.info(f"Integrity check report saved to {report_file}")
    
    async def run_upload(self, directory: str):
        """執行批量上傳主流程"""
        # 如果初始化時沒有設定來源目錄，在這裡更新
        if not self.source_directory:
            self.source_directory = directory
            # 重新設定輸出目錄
            folder_name = os.path.basename(os.path.normpath(directory))
            unique_dir_name = f"{folder_name}_{self.knowledge_base_id[:8]}"
            self.output_dir = os.path.join(os.path.dirname(__file__), 'upload_outputs', unique_dir_name)
            self.checkpoint_dir = os.path.join(self.output_dir, 'checkpoints')
            self.log_dir = os.path.join(self.output_dir, 'logs')
            self.report_dir = os.path.join(self.output_dir, 'reports')
            os.makedirs(self.checkpoint_dir, exist_ok=True)
            os.makedirs(self.log_dir, exist_ok=True)
            os.makedirs(self.report_dir, exist_ok=True)
            # 更新 checkpoint 檔案路徑
            self.checkpoint_file = os.path.join(self.checkpoint_dir, "upload_checkpoint.json")
        
        self.logger.info(f"Scanning directory: {directory}")
        self.logger.info(f"Output directory: {self.output_dir}")
        
        all_tasks = self.scan_files(directory)
        
        checkpoint = self.load_checkpoint()
        if checkpoint:
            self.logger.info("Found checkpoint, resuming upload...")
            completed_files = set(checkpoint.get('completed_files', []))
            all_tasks = [task for task in all_tasks if task.file_path not in completed_files]
        
        # 不再在開始時檢查已存在的檔案，改為最後比對
        
        total_files = len(all_tasks)
        self.logger.info(f"Found {total_files} files to upload")
        
        if total_files == 0:
            self.logger.info("No files to upload")
            return
        
        self.tasks_queue = deque(all_tasks)
        # 取得已完成的檔案數量（如果有 checkpoint）
        if checkpoint:
            completed_files = set(checkpoint.get('completed_files', []))
            initial_completed = len(completed_files)
        else:
            initial_completed = 0
        
        # Process all tasks at once
        # 不要清空 tasks_queue，讓 upload_batch_async 在處理完成後逐個移除
        all_upload_tasks = list(self.tasks_queue)
        
        if not self._shutdown:
            # 使用 tqdm 創建進度條，同時設置 logging 以避免衝突
            import sys
            from tqdm.contrib.logging import logging_redirect_tqdm
            
            with logging_redirect_tqdm():
                with tqdm(total=len(all_upload_tasks), 
                         desc="Uploading files",
                         unit="files",
                         ncols=120,
                         position=0,
                         leave=True,
                         file=sys.stdout) as progress_bar:
                    await self.upload_batch_async(all_upload_tasks, progress_bar)
        
        print()
        self.logger.info("Upload process completed")
        self.logger.info(f"Total files: {total_files}")
        self.logger.info(f"Successfully uploaded: {len(self.completed_tasks)}")
        self.logger.info(f"Failed uploads: {len(self.failed_tasks)}")
        
        # 在上傳完成後進行檔案比對
        await self.check_upload_integrity()
        
        self.save_final_report()
    
    def save_final_report(self):
        """儲存最終上傳報告"""
        report = {
            'summary': {
                'total_files': len(self.completed_tasks) + len(self.failed_tasks),
                'successful_uploads': len(self.completed_tasks),
                'failed_uploads': len(self.failed_tasks),
                'average_upload_time': sum(t.upload_time for t in self.completed_tasks if t.upload_time) / len(self.completed_tasks) if self.completed_tasks else 0
            },
            'successful_files': [
                {
                    'file_path': task.file_path,
                    'file_size': task.file_size,
                    'upload_time': task.upload_time
                }
                for task in self.completed_tasks
            ],
            'failed_files': [
                {
                    'file_path': task.file_path,
                    'error': task.error_message,
                    'retry_count': task.retry_count
                }
                for task in self.failed_tasks
            ]
        }
        
        report_file = os.path.join(self.report_dir, f"upload_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.logger.info(f"Final report saved to {report_file}")


async def main():
    assert API_KEY != '<your-api-key>', 'Please set your API key'
    assert KNOWLEDGE_BASE_ID != '<your-knowledge-base-id>', 'Please set your knowledge base id'
    assert FILES_DIRECTORY != '<your-files-directory>', 'Please set your files directory'
    
    config = UploadConfig(
        max_concurrent_uploads=10,
        max_retries=3,
        retry_delay=2.0,
        timeout_seconds=300
    )
    
    uploader = BatchFileUploaderAdvanced(API_KEY, KNOWLEDGE_BASE_ID, config, FILES_DIRECTORY)
    await uploader.run_upload(FILES_DIRECTORY)


if __name__ == '__main__':
    asyncio.run(main())
