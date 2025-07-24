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


API_KEY = 'CU5SHADu.FLs7wkEU79apxgszcXuSVwZQyEfUqB6m'
KNOWLEDGE_BASE_ID = '94398788-64e7-46a8-8f1e-a8654585960d'
FILES_DIRECTORY = '/Users/hgtffue/Downloads/json_files'

@dataclass
class UploadConfig:
    batch_size: int = 100
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


class ProgressTracker:
    def __init__(self, total_files: int):
        self.total_files = total_files
        self.completed = 0
        self.failed = 0
        self.start_time = time.time()
        self.last_update = time.time()
        
    def update(self, success: bool = True):
        if success:
            self.completed += 1
        else:
            self.failed += 1
        
        current_time = time.time()
        if current_time - self.last_update >= 1:
            self.print_progress()
            self.last_update = current_time
    
    def print_progress(self):
        elapsed = time.time() - self.start_time
        processed = self.completed + self.failed
        rate = processed / elapsed if elapsed > 0 else 0
        eta = (self.total_files - processed) / rate if rate > 0 else 0
        
        print(f"\rProgress: {processed}/{self.total_files} "
              f"({processed/self.total_files*100:.1f}%) | "
              f"Success: {self.completed} | Failed: {self.failed} | "
              f"Rate: {rate:.1f} files/s | ETA: {eta:.0f}s", end='')


class BatchFileUploaderAdvanced:
    def __init__(self, api_key: str, knowledge_base_id: str, config: UploadConfig, source_directory: str = None):
        self.api_key = api_key
        self.knowledge_base_id = knowledge_base_id
        self.config = config
        self.base_url = 'https://autox-api-dev.playma.app/api/v1/'
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
        
        checkpoint_data = {
            'timestamp': datetime.now().isoformat(),
            'completed_files': list(all_completed),
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
                await self.register_file(session, file_key, original_filename)
                
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
    
    async def upload_batch_async(self, tasks: List[FileUploadTask], progress: ProgressTracker):
        """異步批量上傳"""
        semaphore = asyncio.Semaphore(self.config.max_concurrent_uploads)
        
        async def upload_with_semaphore(task):
            async with semaphore:
                return await self.upload_single_file(session, task)
        
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
                    progress.update(success=False)
                elif result.status == UploadStatus.SUCCESS:
                    # 成功的任務已經在 upload_single_file 中添加到 completed_tasks 並儲存了 checkpoint
                    progress.update(success=True)
                else:
                    self.failed_tasks.append(result)
                    progress.update(success=False)
    
    async def get_existing_files(self) -> set:
        """獲取知識庫中已存在的檔案名稱"""
        existing_files = set()
        page = 1
        
        try:
            import requests
            while True:
                url = f"{self.base_url}knowledge-bases/{self.knowledge_base_id}/files/?page={page}"
                headers = {'Authorization': f'Api-Key {self.api_key}'}
                
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                data = response.json()
                
                if 'results' in data:
                    for file in data['results']:
                        filename = file.get('filename', '')
                        if filename:
                            existing_files.add(filename)
                    
                    if not data.get('next'):  # 沒有下一頁
                        break
                    page += 1
                else:
                    break
                    
            self.logger.info(f"Found {len(existing_files)} existing files in knowledge base")
            return existing_files
            
        except Exception as e:
            self.logger.warning(f"Failed to get existing files: {e}")
            return existing_files
    
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
        
        # 獲取知識庫中已存在的檔案
        existing_files = await self.get_existing_files()
        
        all_tasks = self.scan_files(directory)
        
        checkpoint = self.load_checkpoint()
        if checkpoint:
            self.logger.info("Found checkpoint, resuming upload...")
            completed_files = set(checkpoint.get('completed_files', []))
            all_tasks = [task for task in all_tasks if task.file_path not in completed_files]
        
        # 進一步排除知識庫中已存在的檔案
        if existing_files:
            before_count = len(all_tasks)
            all_tasks = [task for task in all_tasks 
                         if os.path.basename(task.file_path) not in existing_files]
            excluded_count = before_count - len(all_tasks)
            if excluded_count > 0:
                self.logger.info(f"Excluded {excluded_count} files that already exist in knowledge base")
        
        total_files = len(all_tasks)
        self.logger.info(f"Found {total_files} files to upload")
        
        if total_files == 0:
            self.logger.info("No files to upload")
            return
        
        self.tasks_queue = deque(all_tasks)
        progress = ProgressTracker(total_files)
        
        while self.tasks_queue and not self._shutdown:
            batch_size = min(self.config.batch_size, len(self.tasks_queue))
            batch_tasks = [self.tasks_queue.popleft() for _ in range(batch_size)]
            
            await self.upload_batch_async(batch_tasks, progress)
            
            # checkpoint 現在在每個檔案上傳成功後立即儲存，不需要在這裡處理
            
            await asyncio.sleep(0.5)
        
        print()
        self.logger.info("Upload process completed")
        self.logger.info(f"Total files: {total_files}")
        self.logger.info(f"Successfully uploaded: {len(self.completed_tasks)}")
        self.logger.info(f"Failed uploads: {len(self.failed_tasks)}")
        
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
        batch_size=100,
        max_concurrent_uploads=10,
        max_retries=3,
        retry_delay=2.0,
        timeout_seconds=300
    )
    
    uploader = BatchFileUploaderAdvanced(API_KEY, KNOWLEDGE_BASE_ID, config, FILES_DIRECTORY)
    await uploader.run_upload(FILES_DIRECTORY)


if __name__ == '__main__':
    asyncio.run(main())
