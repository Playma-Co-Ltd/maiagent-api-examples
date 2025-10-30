# MaiAgent API 檔案上傳功能說明

本文檔說明如何使用 MaiAgent API 的檔案上傳功能。`upload_attachment.py` 腳本提供了一個簡單的示例，展示如何與 API 進行互動。

## API 功能概述

MaiAgent API 的檔案上傳功能允許您將各種類型的檔案（如圖片、音訊、影片和文件等）上傳到 MaiAgent 平台。上傳後，您可以獲取檔案的 ID，用於在訊息中引用該檔案。

## API 端點

上傳檔案使用的 API 端點為：

```
POST {BASE_URL}attachments/
```

## 請求格式

請求需要包含以下內容：

- **標頭**：
  - `Authorization`: 包含 API 金鑰的認證標頭，格式為 `Api-Key {YOUR_API_KEY}`
  
- **檔案**：
  - 使用 multipart/form-data 格式上傳檔案
  - 檔案欄位名稱為 `file`

## 回應格式

成功上傳後，API 會返回類似以下的 JSON 回應：

```json
{
  "id": "att_f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "type": "text",
  "filename": "異型介紹.txt",
  "file": "https://storage.example.com/path/to/file.txt"
}
```

其中：
- `id`: 檔案的唯一識別碼，可用於後續操作引用此檔案
- `type`: 檔案類型（如 audio、image、video、document、text 等）
- `filename`: 原始檔案名稱
- `file`: 檔案的存取 URL


## 使用示例

### Python 使用示例

```python
# 使用 API 上傳檔案
import requests
import mimetypes
from pathlib import Path

# 設定 API 認證和端點
API_KEY = "your_api_key_here"
BASE_URL = "https://api.maiagent.com/"

# 上傳檔案
def upload_attachment(file_path):
    file_path = Path(file_path)
    
    headers = {'Authorization': f'Api-Key {API_KEY}'}
    mime_type, _ = mimetypes.guess_type(file_path)

    with open(file_path, 'rb') as file:
        files = {'file': (file_path.name, file, mime_type)}
        response = requests.post(f'{BASE_URL}attachments/', headers=headers, files=files)
    
    return response.json()

# 使用範例
result = upload_attachment('path/to/your/file.jpg')
print(result)
```


## 注意事項

1. 確保您已獲取有效的 API 金鑰
2. 檔案大小可能受到 API 限制，請參考 API 文檔了解具體限制
3. 支援的檔案類型可能有所限制，請參考 API 文檔了解支援的檔案類型
4. 上傳的檔案 ID 可用於在發送訊息時引用附件 