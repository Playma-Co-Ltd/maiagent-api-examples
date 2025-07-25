# 批量上傳工具 (Batch Upload Tool)

這是一個高效能的批量檔案上傳工具，專門用於將大量檔案批次上傳至 MaiAgent 知識庫。

## 功能特色

### 🚀 高效能上傳
- **異步並發上傳**：同時處理多個檔案，顯著提升上傳速度
- **可調整並發數**：可根據網路環境調整同時上傳的檔案數量
- **智慧速度控制**：自動調整上傳速度以獲得最佳效能

### 🔄 斷點續傳
- **自動恢復機制**：程式中斷後可從上次停止的位置繼續
- **固定 Checkpoint**：使用單一檔案累積記錄，避免重複上傳
- **Knowledge File ID 追蹤**：記錄每個檔案的知識庫 ID，確保完整性
- **進度持久化**：定期儲存進度，確保資料不遺失

### 📊 視覺化進度追蹤
- **tqdm 進度條**：美觀的進度條顯示上傳進度
- **即時統計資訊**：顯示成功/失敗數量、上傳速率
- **完整日誌記錄**：記錄所有上傳過程和錯誤訊息
- **詳細報告生成**：產生包含統計資訊的 JSON 報告

### 🔍 完整性檢查
- **自動完整性驗證**：上傳完成後自動比對知識庫內容
- **漏傳檔案檢測**：識別可能失敗或被刪除的檔案
- **重複檔案提醒**：發現可能重複上傳的檔案
- **詳細分析報告**：產生完整的完整性檢查報告

### 🛡️ 錯誤處理
- **自動重試機制**：失敗檔案會自動重試，可設定重試次數
- **錯誤分類記錄**：詳細記錄每個失敗檔案的錯誤原因
- **優雅中斷處理**：支援 Ctrl+C 中斷，會先儲存進度再退出

### 📁 智慧檔案管理
- **獨立輸出目錄**：根據來源資料夾和知識庫 ID 創建唯一目錄
- **分類檔案存放**：Checkpoint、日誌、報告分別存放在不同資料夾
- **自動過濾檔案**：自動跳過隱藏檔案和系統檔案

## 檔案結構

```
batch_upload/
├── batch_upload_advanced.py    # 主程式
├── README.md                   # 說明文件
└── upload_outputs/             # 輸出目錄
    └── {資料夾名}_{知識庫ID}/
        ├── checkpoints/
        │   └── upload_checkpoint.json
        ├── logs/
        │   └── upload_log_YYYYMMDD_HHMMSS.log
        └── reports/
            ├── upload_report_YYYYMMDD_HHMMSS.json
            └── integrity_check_YYYYMMDD_HHMMSS.json
```

## 設定說明

### 必要設定
在 `batch_upload_advanced.py` 中修改以下參數：

```python
API_KEY = 'your-api-key-here'                    # MaiAgent API 金鑰
KNOWLEDGE_BASE_ID = 'your-knowledge-base-id'     # 目標知識庫 ID
FILES_DIRECTORY = '/path/to/your/files'          # 要上傳的檔案目錄
```

### 進階設定
可調整 `UploadConfig` 參數：

```python
config = UploadConfig(
    max_concurrent_uploads=10,   # 最大並發上傳數
    max_retries=3,              # 失敗重試次數
    retry_delay=2.0,            # 重試間隔（秒）
    timeout_seconds=300,        # 請求超時時間
)
```

## 使用方法

### 1. 安裝依賴套件
```bash
pip install aiohttp aiofiles tqdm requests
```

### 2. 設定參數
編輯 `batch_upload_advanced.py`，填入你的 API 金鑰、知識庫 ID 和檔案目錄路徑。

### 3. 執行上傳
```bash
cd /path/to/batch_upload/
python batch_upload_advanced.py
```

### 4. 監控進度
程式會顯示 tqdm 進度條：
```
Uploading files: 1500/10000 15% |████▊                     | [02:30<14:10, 8.5files/s]
```

### 5. 處理中斷
如果程式被中斷（Ctrl+C 或其他原因），再次執行即可從斷點繼續：
```bash
python batch_upload_advanced.py
```
程式會自動載入 checkpoint 並跳過已完成的檔案。

## 輸出檔案說明

### Checkpoint 檔案 (`upload_checkpoint.json`)
記錄上傳進度和檔案 ID 映射，格式如下：
```json
{
  "timestamp": "2025-07-25T12:00:00.000000",
  "completed_files": [
    "/path/to/file1.json",
    "/path/to/file2.json"
  ],
  "file_id_mapping": {
    "/path/to/file1.json": "knowledge-file-id-1",
    "/path/to/file2.json": "knowledge-file-id-2"
  },
  "failed_files": [
    ["/path/to/failed_file.json", "Connection timeout"]
  ],
  "pending_files": [
    "/path/to/pending_file.json"
  ]
}
```

### 日誌檔案 (`upload_log_*.log`)
詳細記錄所有操作過程，包括：
- 程式啟動和設定資訊
- 檔案掃描結果
- 上傳進度更新
- 錯誤訊息和重試記錄
- 完整性檢查結果
- 最終統計結果

### 上傳報告檔案 (`upload_report_*.json`)
完整的上傳統計報告：
```json
{
  "summary": {
    "total_files": 10000,
    "successful_uploads": 9850,
    "failed_uploads": 150,
    "average_upload_time": 1.25
  },
  "successful_files": [
    {
      "file_path": "/path/to/file.json",
      "file_size": 2048,
      "upload_time": 1.2
    }
  ],
  "failed_files": [
    {
      "file_path": "/path/to/failed.json",
      "error": "Connection timeout",
      "retry_count": 3
    }
  ]
}
```

### 完整性檢查報告 (`integrity_check_*.json`)
上傳完成後的完整性驗證報告：
```json
{
  "timestamp": "2025-07-25T12:00:00.000000",
  "summary": {
    "total_kb_files": 10000,
    "total_uploaded_files": 9850,
    "total_uploaded_ids": 9850,
    "missing": 5,
    "extra": 150
  },
  "missing_files": [
    {
      "filename": "missing_file.json",
      "filepath": "/path/to/missing_file.json",
      "knowledge_file_id": "missing-id-123"
    }
  ],
  "extra_files": [
    {
      "filename": "extra_file.json",
      "knowledge_file_id": "extra-id-456",
      "created_at": "2025-07-25T10:30:00"
    }
  ]
}
```

## 上傳流程詳解

### 1. 初始化階段
- 建立輸出目錄結構
- 設定日誌系統
- 註冊中斷信號處理器

### 2. 檔案掃描
- 遞迴掃描指定目錄
- 過濾隱藏檔案
- 建立上傳任務列表

### 3. 斷點恢復
- 檢查是否存在 checkpoint
- 載入已完成檔案列表和 ID 映射
- 排除已上傳的檔案

### 4. 批量上傳
每個檔案的上傳包含三個步驟：
1. **獲取上傳 URL**：向 API 請求預簽名上傳 URL
2. **上傳到 S3**：使用 multipart/form-data 格式上傳檔案
3. **註冊到知識庫**：將檔案關聯到指定知識庫並記錄 Knowledge File ID

### 5. 進度管理
- tqdm 進度條即時顯示
- 定期儲存 checkpoint 和 ID 映射
- 記錄成功和失敗的檔案

### 6. 完整性檢查
- 獲取知識庫中所有檔案
- 比對 checkpoint 記錄的 Knowledge File ID
- 識別漏傳和多餘檔案
- 生成詳細分析報告

### 7. 完成處理
- 生成最終統計報告
- 清理暫存資源
- 顯示完整結果

## 效能調優建議

### 網路環境良好
```python
config = UploadConfig(
    max_concurrent_uploads=20,
    max_retries=3,
    retry_delay=1.0,
    timeout_seconds=180,
)
```

### 網路環境一般
```python
config = UploadConfig(
    max_concurrent_uploads=10,
    max_retries=5,
    retry_delay=2.0,
    timeout_seconds=300,
)
```

### 網路環境較差
```python
config = UploadConfig(
    max_concurrent_uploads=5,
    max_retries=5,
    retry_delay=5.0,
    timeout_seconds=600,
)
```

## 常見問題

### Q: 程式運行中可以中斷嗎？
A: 可以。使用 Ctrl+C 中斷程式會觸發優雅關閉，自動儲存當前進度和檔案 ID 映射。

### Q: 如何處理大量失敗的檔案？
A: 檢查日誌檔案了解失敗原因，調整網路設定或重試參數後重新運行。

### Q: 完整性檢查發現 missing files 怎麼辦？
A: Missing files 可能是上傳後被刪除或上傳失敗。檢查完整性報告中的具體檔案，可以重新上傳這些檔案。

### Q: 如何處理 extra files？
A: Extra files 可能是重複上傳或透過其他方式上傳的檔案。可以根據檔案名稱和創建時間判斷是否需要刪除。

### Q: 可以同時上傳到不同的知識庫嗎？
A: 需要分別執行程式，每次指定不同的知識庫 ID。程式會自動為不同的知識庫創建獨立的輸出目錄。

### Q: 支援哪些檔案格式？
A: 程式本身不限制檔案格式，但 MaiAgent 知識庫可能對特定格式有要求。建議參考 MaiAgent 官方文件。

### Q: 如何查看詳細的錯誤資訊？
A: 檢查 `logs/` 目錄下的日誌檔案，包含所有詳細的錯誤訊息和堆疊追蹤。

## 技術規格

- **Python 版本**：3.7+
- **主要依賴**：aiohttp, aiofiles, tqdm, requests
- **並發模型**：異步 I/O (asyncio)
- **記憶體使用**：低記憶體佔用，適合處理大量檔案
- **平台支援**：跨平台 (Windows, macOS, Linux)

---

如有任何問題或建議，請聯繫開發團隊。