# 上傳與下載 批次 QA 檔案範例

這個範例展示如何使用 MaiAgent API 上傳與下載批次 QA 檔案。

## 檔案說明

1. [`upload_batch_qa_file.cs`](upload_batch_qa_file.cs): 用於向 MaiAgent API 上傳批次 QA 檔案的程式碼。
2. [`download_batch_qa_excel.cs`](download_batch_qa_excel.cs): 用於向 MaiAgent API 下載批次 QA Excel 檔案的程式碼。

## 使用方式

1. 上傳批次 QA 檔案：

在 `upload_batch_qa_file.cs` 中設定您的 API 金鑰和 WebChat ID：

```csharp
API_KEY = '您的 API 金鑰'
WEB_CHAT_ID = '您的 WebChat ID'
FILE_PATH = '您的批次 QA 檔案路徑'
```

執行上傳批次 QA 檔案的腳本：
```bash
csharp -m batch_qa.upload_batch_qa_file
```

2. 下載批次 QA Excel 檔案：

請注意：在上傳批次 QA 檔案後，系統需要一些時間來處理檔案。您需要等待處理完成後才能下載對應的 Excel 檔案。處理時間可能因檔案大小和系統負載而有所不同，通常需要幾分鐘到幾十分鐘不等。建議您在上傳後稍等片刻，再執行下載操作。若是提早下載，可能會下載到尚未處理完成的檔案，導致下載的內容不完整。

下載的 Excel 檔案將包含以下內容：

- 問題：使用者訊息的內容
- 型態：指示訊息是對話中的「新問題」還是「後續問題」
- 回覆：AI 助理的回應內容

這些資訊可以幫助您分析對話的流程，評估 AI 助理的回答品質，並找出可能需要改進的地方。

在 `download_batch_qa_excel.cs` 中設定您的 API 金鑰和 WebChat ID：

```csharp
API_KEY = '您的 API 金鑰'
WEB_CHAT_ID = '您的 WebChat ID'
BATCH_QA_FILE_ID = '您的批次 QA 檔案 ID'
```

執行下載批次 QA Excel 檔案的腳本：

```bash
csharp -m batch_qa.download_batch_qa_excel
```

