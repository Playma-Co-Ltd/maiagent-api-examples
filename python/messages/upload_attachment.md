# 檔案上傳功能說明

本文檔說明如何使用 `upload_attachment.py` 腳本上傳檔案附件到 MaiAgent API。

## 功能概述

`upload_attachment.py` 是一個用於將檔案上傳到 MaiAgent API 的工具。它支援各種類型的檔案，如圖片、音訊、影片和文件等。上傳後，您可以獲取檔案的 ID，用於在訊息中引用該檔案。

## 前置需求

1. 已安裝 Python 3.11 或更高版本
2. 已安裝必要的依賴套件（可通過 `requirements.txt` 安裝）
3. 已設定 MaiAgent API 金鑰和基礎 URL（在 `.env` 檔案中）

## 使用方法

### 基本用法

```python
from messages.upload_attachment import main as upload_attachment

# 上傳檔案並獲取回應
response = upload_attachment('path/to/your/file.jpg')
print(response)  # 包含檔案 ID 和其他資訊的字典
```

### 命令列用法

您也可以直接從命令列執行腳本：

```bash
# 在 python 目錄下執行
python -m messages.upload_attachment
```

預設情況下，腳本會上傳在 `TEST_IMAGE_PATH` 變數中指定的測試檔案（`test_files/天氣真好.mp3`）。

### 自訂檔案路徑

若要上傳自訂檔案，您可以修改腳本中的 `TEST_IMAGE_PATH` 變數，或在程式碼中直接呼叫 `main()` 函數並傳入檔案路徑：

```python
if __name__ == '__main__':
    main('path/to/your/custom/file.jpg')
```

## 程式碼說明

腳本的主要功能由 `main()` 函數提供：

1. 檢查檔案是否存在
2. 設定 API 請求標頭，包含 API 金鑰
3. 猜測檔案的 MIME 類型
4. 開啟檔案並以二進位模式讀取
5. 使用 `requests` 庫將檔案上傳到 API
6. 返回 API 的 JSON 回應

## API 端點

上傳檔案使用的 API 端點為：

```
POST {BASE_URL}attachments/
```

## 請求格式

請求需要包含以下內容：

- **標頭**：
  - `Authorization`: 包含 API 金鑰的認證標頭
  
- **檔案**：
  - 使用 multipart/form-data 格式上傳檔案
  - 檔案欄位名稱為 `file`

## 回應格式

成功上傳後，API 會返回類似以下的 JSON 回應：

```json
{
  "id": "att_f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "type": "audio",
  "filename": "天氣真好.mp3",
  "file": "https://storage.example.com/path/to/file.mp3"
}
```

其中：
- `id`: 檔案的唯一識別碼，可用於後續操作引用此檔案
- `type`: 檔案類型（如 audio、image、video、document 等）
- `filename`: 原始檔案名稱
- `file`: 檔案的存取 URL

## 錯誤處理

腳本會處理以下錯誤情況：

- 檔案不存在：拋出 `FileNotFoundError` 異常
- API 請求失敗：返回 API 的錯誤回應

可能的 API 錯誤回應包括：
- 401: 未授權（API 金鑰無效）
- 413: 檔案太大
- 415: 不支援的檔案類型
- 500: 伺服器內部錯誤

## 注意事項

1. 確保您的 `.env` 檔案中已正確設定 `MAIAGENT_API_KEY` 和 `MAIAGENT_BASE_URL`
2. 檔案大小可能受到 API 限制，請參考 API 文檔了解具體限制
3. 支援的檔案類型可能有所限制，請參考 API 文檔了解支援的檔案類型 