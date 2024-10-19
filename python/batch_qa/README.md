# 上傳與下載 批次 QA 檔案範例

這個範例展示如何使用 MaiAgent API 上傳與下載批次 QA 檔案。

## 檔案說明

1. [`upload_batch_qa_file.py`](upload_batch_qa_file.py): 用於向 MaiAgent API 上傳批次 QA 檔案的程式碼。
2. [`download_batch_qa_excel.py`](download_batch_qa_excel.py): 用於向 MaiAgent API 下載批次 QA Excel 檔案的程式碼。

## 使用方式

1. 上傳批次 QA 檔案：

在 `upload_batch_qa_file.py` 中設定您的 API 金鑰和 WebChat ID：

```python
API_KEY = '您的 API 金鑰'
WEB_CHAT_ID = '您的 WebChat ID'
FILE_PATH = '您的批次 QA 檔案路徑'
```

執行上傳批次 QA 檔案的腳本：
```bash
python -m batch_qa.upload_batch_qa_file
```

2. 下載批次 QA Excel 檔案：

在 `download_batch_qa_excel.py` 中設定您的 API 金鑰和 WebChat ID：

```python
API_KEY = '您的 API 金鑰'
WEB_CHAT_ID = '您的 WebChat ID'
BATCH_QA_FILE_ID = '您的批次 QA 檔案 ID'
```

執行下載批次 QA Excel 檔案的腳本：

```bash
python -m batch_qa.download_batch_qa_excel
```

