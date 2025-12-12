# 上傳與下載 批次 QA 檔案範例

這個範例展示如何使用 MaiAgent API 上傳與下載批次 QA 檔案。

## 檔案說明

1. [upload_batch_qa_file.cs](upload_batch_qa_file.cs): 用於向 MaiAgent API 上傳批次 QA 檔案的程式碼。
2. [download_batch_qa_excel.cs](download_batch_qa_excel.cs): 用於向 MaiAgent API 下載批次 QA Excel 檔案的程式碼。

## 使用方式

### 1. 上傳批次 QA 檔案

在 [upload_batch_qa_file.cs](upload_batch_qa_file.cs:10-12) 中設定您的 API 金鑰和 WebChat ID：

```csharp
public static string API_KEY = "<your-api-key>";
public static string WEB_CHAT_ID = "<your-web-chat-id>";
public static string FILE_PATH = "<your-file-path>";
```

執行上傳批次 QA 檔案：

**方法 1：修改 Program.cs**

編輯 [Program.cs](../Program.cs)，在 Main 方法中呼叫上傳範例：

```csharp
static async Task Main(string[] args)
{
    await MaiAgentExamples.BatchQA.UploadBatchQAFile.Main(args);
}
```

然後執行：

```bash
cd examples/csharp
dotnet run
```

**方法 2：使用 dotnet script（需安裝 dotnet-script）**

```bash
dotnet script batch_qa/upload_batch_qa_file.cs
```

### 2. 下載批次 QA Excel 檔案

**重要提醒**：在上傳批次 QA 檔案後，系統需要一些時間來處理檔案。您需要等待處理完成後才能下載對應的 Excel 檔案。處理時間可能因檔案大小和系統負載而有所不同，通常需要幾分鐘到幾十分鐘不等。建議您在上傳後稍等片刻，再執行下載操作。若是提早下載，可能會下載到尚未處理完成的檔案，導致下載的內容不完整。

下載的 Excel 檔案將包含以下內容：

- **問題**：使用者訊息的內容
- **型態**：指示訊息是對話中的「新問題」還是「後續問題」
- **回覆**：AI 助理的回應內容

這些資訊可以幫助您分析對話的流程，評估 AI 助理的回答品質，並找出可能需要改進的地方。

在 [download_batch_qa_excel.cs](download_batch_qa_excel.cs:10-12) 中設定您的 API 金鑰和 WebChat ID：

```csharp
public static string API_KEY = "<your-api-key>";
public static string WEB_CHAT_ID = "<your-web-chat-id>";
public static string BATCH_QA_FILE_ID = "<your-batch-qa-file-id>";
```

執行下載批次 QA Excel 檔案：

**方法 1：修改 Program.cs**

```csharp
static async Task Main(string[] args)
{
    await MaiAgentExamples.BatchQA.DownloadBatchQAExcel.Main(args);
}
```

然後執行：

```bash
cd examples/csharp
dotnet run
```

**方法 2：使用 dotnet script**

```bash
dotnet script batch_qa/download_batch_qa_excel.cs
```

## 完整工作流程範例

```csharp
using System;
using System.Threading.Tasks;
using Utils;

namespace MaiAgentExamples.BatchQA
{
    class Example
    {
        static async Task Main(string[] args)
        {
            var apiKey = "<your-api-key>";
            var webChatId = "<your-web-chat-id>";
            var filePath = "path/to/qa_file.xlsx";

            var helper = new MaiAgentHelper(apiKey);

            // 1. 上傳批次 QA 檔案
            Console.WriteLine("正在上傳批次 QA 檔案...");
            var uploadInfo = await helper.GetUploadUrlAsync(filePath, "batch-qa", "file");
            if (!uploadInfo.HasValue)
            {
                Console.WriteLine("獲取上傳 URL 失敗");
                return;
            }

            var fileKey = await helper.UploadFileToS3Async(filePath, uploadInfo.Value);
            var batchQaResponse = await helper.UploadBatchQAFileAsync(
                webChatId,
                fileKey,
                Path.GetFileName(filePath)
            );

            var batchQaFileId = batchQaResponse.GetProperty("id").GetString();
            Console.WriteLine($"上傳成功！批次 QA 檔案 ID: {batchQaFileId}");

            // 2. 等待處理（建議等待幾分鐘）
            Console.WriteLine("請等待系統處理完成...");
            await Task.Delay(TimeSpan.FromMinutes(5)); // 等待 5 分鐘

            // 3. 下載結果
            Console.WriteLine("正在下載結果...");
            var filename = await helper.DownloadBatchQAExcelAsync(webChatId, batchQaFileId!);
            Console.WriteLine($"下載成功！檔案已儲存為: {filename}");
        }
    }
}
```

## 注意事項

1. **API 金鑰設定**：請確保已正確設定 API 金鑰
2. **檔案格式**：上傳的檔案必須符合 MaiAgent 批次 QA 的格式要求
3. **處理時間**：批次 QA 處理需要時間，請耐心等待
4. **錯誤處理**：建議在實際使用中加入完善的錯誤處理機制
5. **檔案大小限制**：請注意 API 對檔案大小的限制

## 相關文檔

- [MaiAgentHelper 使用文檔](../utils/maiagent.md)
- [MaiAgent API 官方文檔](https://docs.maiagent.ai/)
