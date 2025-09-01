# 知識庫檔案下載功能

這個功能可以幫助您下載 MaiAgent 知識庫中的所有檔案到本地。

## 新增的功能

我們為 `MaiAgentHelper` 類別新增了兩個方法：

### 1. download_knowledge_base_file()
下載知識庫中的單個檔案。

```python
file_path = helper.download_knowledge_base_file(
    knowledge_base_id="your-kb-id",
    file_id="your-file-id", 
    download_dir="downloads"  # 可選，預設為 "downloads"
)
```

### 2. download_all_knowledge_base_files()
下載知識庫中的所有檔案（支持分頁）。

```python
result = helper.download_all_knowledge_base_files(
    knowledge_base_id="your-kb-id",
    download_dir="downloads",  # 可選，預設為 "downloads"
    page_size=100  # 可選，每頁檔案數量，預設為 100
)
```

**回傳值：**
```python
{
    'downloaded': [  # 成功下載的檔案
        {
            'id': 'file-id',
            'filename': 'example.pdf',
            'path': '/path/to/downloads/example.pdf',
            'size': 12345
        }
    ],
    'failed': [  # 下載失敗的檔案
        {
            'id': 'file-id',
            'filename': 'failed.doc',
            'error': 'error message'
        }
    ],
    'total': 10,  # 總檔案數
    'download_dir': '/absolute/path/to/downloads'  # 下載目錄的絕對路徑
}
```

## 範例檔案

### 1. 簡單範例 - `simple_download_example.py`
```python
from utils import MaiAgentHelper

# 設定
API_KEY = 'your-api-key'
KNOWLEDGE_BASE_ID = 'your-knowledge-base-id'

# 初始化
helper = MaiAgentHelper(API_KEY)

# 下載所有檔案
result = helper.download_all_knowledge_base_files(KNOWLEDGE_BASE_ID)
print(f"成功下載 {len(result['downloaded'])} 個檔案")
```

### 2. 完整範例 - `download_knowledge_base_files.py`
包含互動式介面，顯示檔案統計並讓用戶選擇下載所有檔案或取消。

## 使用步驟

1. **設定 API Key 和知識庫 ID**：
```python
API_KEY = 'your-actual-api-key'
KNOWLEDGE_BASE_ID = 'your-actual-knowledge-base-id'
```

2. **執行簡單範例**：
```bash
cd python
python -m knowledges.simple_download_example
```

3. **執行完整範例**：
```bash
cd python  
python -m knowledges.download_knowledge_base_files
```

## 功能特點

- ✅ **分頁支援**：自動處理大量檔案的分頁下載
- ✅ **批次下載**：一次下載知識庫中的所有檔案
- ✅ **錯誤處理**：詳細的錯誤訊息和失敗統計
- ✅ **進度顯示**：顯示收集檔案和下載進度
- ✅ **自動建目錄**：自動建立下載目錄
- ✅ **檔案資訊**：保留原始檔名和檔案資訊
- ✅ **大小統計**：顯示檔案大小統計
- ✅ **簡化操作**：只需選擇下載或取消，無複雜選項

## 注意事項

1. **API Key**：請確保設定正確的 API Key
2. **知識庫 ID**：請確保知識庫 ID 正確且有權限存取
3. **網路連線**：下載需要穩定的網路連線
4. **存儲空間**：請確保有足夠的本地存儲空間
5. **檔案權限**：請確保有寫入下載目錄的權限

## 錯誤排除

- **403 Forbidden**：檢查 API Key 是否正確
- **404 Not Found**：檢查知識庫 ID 是否正確
- **網路錯誤**：檢查網路連線
- **權限錯誤**：檢查下載目錄的寫入權限
