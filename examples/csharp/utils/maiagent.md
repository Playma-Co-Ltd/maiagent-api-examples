# MaiAgentHelper 類別文檔

`MaiAgentHelper` 是一個用於與 MaiAgent API 互動的 C# 輔助類別，提供了一系列方便的方法來處理對話、訊息、檔案上傳和知識庫管理等功能。

## 類別初始化

```csharp
using Utils;

var helper = new MaiAgentHelper(
    apiKey: "your_api_key_here",
    baseUrl: "https://api.maiagent.ai/api/v1/",  // 選填
    storageUrl: "{storage_url}/{bucket_name}"  // 選填，請務必替換 {storage_url} 和 {bucket_name}
);
```

### 參數說明
- `apiKey` (string): MaiAgent API 金鑰
- `baseUrl` (string, 選填): API 基礎 URL，預設為 'https://api.maiagent.ai/api/v1/'
- `storageUrl` (string, 選填): 儲存服務的 URL，用於檔案上傳和存取
  - 格式: `{storage_url}/{bucket_name}`
  - `{storage_url}`: 儲存服務的基礎 URL (例如: https://s3.ap-northeast-1.amazonaws.com)
  - `{bucket_name}`: 儲存桶名稱
  - 預設值: 'https://s3.ap-northeast-1.amazonaws.com/whizchat-media-prod-django.playma.app'

## 主要方法

### 對話管理

#### CreateConversationAsync
建立新的對話。

```csharp
var conversation = await helper.CreateConversationAsync("your_web_chat_id");
```

**參數：**
- `webChatId` (string): 網頁聊天 ID

**回傳：**
- `Task<JsonElement>`: 包含新建對話資訊的 JSON 元素

### 訊息處理

#### SendMessageAsync
發送訊息到指定對話。

```csharp
var message = await helper.SendMessageAsync(
    conversationId: "your_conversation_id",
    content: "Hello, world!",
    attachments: null  // 選填
);
```

**參數：**
- `conversationId` (string): 對話 ID
- `content` (string): 訊息內容
- `attachments` (List<string>, 選填): 附件 ID 列表

**回傳：**
- `Task<JsonElement>`: 包含已發送訊息資訊的 JSON 元素

### 檔案上傳

#### GetUploadUrlAsync
獲取檔案上傳的預簽署 URL。

```csharp
var uploadUrl = await helper.GetUploadUrlAsync(
    filePath: "path/to/file",
    modelName: "model_name",
    fieldName: "file"  // 選填
);
```

**參數：**
- `filePath` (string): 檔案路徑
- `modelName` (string): 模型名稱
- `fieldName` (string, 選填): 欄位名稱，預設為 'file'

**回傳：**
- `Task<JsonElement?>`: 上傳 URL 資訊

#### UploadFileToS3Async
將檔案上傳到 S3 儲存空間。

```csharp
if (uploadUrl.HasValue)
{
    var fileKey = await helper.UploadFileToS3Async(
        filePath: "path/to/file",
        uploadData: uploadUrl.Value
    );
}
```

**參數：**
- `filePath` (string): 檔案路徑
- `uploadData` (JsonElement): 上傳資料（從 GetUploadUrlAsync 獲得）

**回傳：**
- `Task<string>`: 檔案金鑰

### 附件管理

#### UpdateAttachmentAsync
更新對話中的附件資訊。

```csharp
var attachment = await helper.UpdateAttachmentAsync(
    conversationId: "your_conversation_id",
    fileId: "file_key",
    originalFilename: "filename.jpg"
);
```

**參數：**
- `conversationId` (string): 對話 ID
- `fileId` (string): 檔案 ID
- `originalFilename` (string): 原始檔案名稱

#### UploadAttachmentAsync
上傳附件（包含獲取 URL、上傳到 S3 和更新附件資訊）。

```csharp
var attachment = await helper.UploadAttachmentAsync(
    conversationId: "your_conversation_id",
    filePath: "path/to/image.jpg"
);
```

#### UploadAttachmentWithoutConversationAsync
不需要對話 ID 的附件上傳。

```csharp
var attachment = await helper.UploadAttachmentWithoutConversationAsync(
    filePath: "path/to/image.jpg",
    type: "image"
);
```

**參數：**
- `filePath` (string): 檔案路徑
- `type` (string, 選填): 附件類型，預設為 "image"

### 知識庫管理

#### UploadKnowledgeFileAsync
上傳知識庫檔案。

```csharp
var knowledgeFile = await helper.UploadKnowledgeFileAsync(
    chatbotId: "your_chatbot_id",
    filePath: "path/to/knowledge.pdf"
);
```

**參數：**
- `chatbotId` (string): 聊天機器人 ID
- `filePath` (string): 檔案路徑

#### DeleteKnowledgeFileAsync
刪除知識庫檔案。

```csharp
await helper.DeleteKnowledgeFileAsync(
    chatbotId: "your_chatbot_id",
    fileId: "your_file_id"
);
```

#### 知識庫 CRUD 方法

```csharp
// 建立知識庫
var kb = await helper.create_knowledge_base("知識庫名稱", "描述", "zh-TW");

// 列出所有知識庫
var kbList = await helper.list_knowledge_bases();

// 獲取特定知識庫
var kbDetail = await helper.get_knowledge_base("knowledge_base_id");

// 搜尋知識庫
var searchResults = await helper.search_knowledge_base("knowledge_base_id", "查詢關鍵字");

// 上傳檔案到知識庫
var file = await helper.upload_knowledge_file("chatbot_id", "path/to/file.pdf");

// 列出知識庫檔案
var files = await helper.list_knowledge_base_files("knowledge_base_id");

// 獲取特定檔案
var fileDetail = await helper.get_knowledge_base_file("knowledge_base_id", "file_id");

// 更新檔案元資料
await helper.update_knowledge_base_file_metadata("knowledge_base_id", "file_id", new List<string> { "label1", "label2" });

// 刪除檔案
await helper.delete_knowledge_file("chatbot_id", "file_id");
```

#### 知識庫標籤管理

```csharp
// 建立標籤
var label = await helper.create_knowledge_base_label("knowledge_base_id", "標籤名稱", "#FF5733");

// 列出所有標籤
var labels = await helper.list_knowledge_base_labels("knowledge_base_id");

// 獲取特定標籤
var labelDetail = await helper.get_knowledge_base_label("knowledge_base_id", "label_id");

// 更新標籤
await helper.update_knowledge_base_label("knowledge_base_id", "label_id", "新名稱", "#00FF00");
```

#### 知識庫 FAQ 管理

```csharp
// 建立 FAQ
var faq = await helper.create_knowledge_base_faq("knowledge_base_id", "問題", "答案");

// 列出所有 FAQ
var faqs = await helper.list_knowledge_base_faqs("knowledge_base_id");

// 獲取特定 FAQ
var faqDetail = await helper.get_knowledge_base_faq("knowledge_base_id", "faq_id");

// 更新 FAQ
await helper.update_knowledge_base_faq("knowledge_base_id", "faq_id", "新問題", "新答案");
```

### 批次問答管理

#### UploadBatchQAFileAsync
上傳批次問答檔案。

```csharp
var batchQa = await helper.UploadBatchQAFileAsync(
    webChatId: "your_web_chat_id",
    fileKey: "your_file_key",
    originalFilename: "qa_file.xlsx"
);
```

**參數：**
- `webChatId` (string): 網頁聊天 ID
- `fileKey` (string): 檔案金鑰
- `originalFilename` (string): 原始檔案名稱

#### DownloadBatchQAExcelAsync
下載批次問答 Excel 檔案。

```csharp
var filename = await helper.DownloadBatchQAExcelAsync(
    webChatId: "your_web_chat_id",
    batchQaFileId: "your_batch_qa_file_id"
);
```

### 收件匣管理

#### GetInboxItemsAsync
獲取所有收件匣項目。

```csharp
var inboxItems = await helper.GetInboxItemsAsync();
```

**回傳：**
- `Task<JsonElement[]>`: 收件匣項目陣列

#### DisplayInboxItems
顯示收件匣項目資訊。

```csharp
helper.DisplayInboxItems(inboxItems);
```

### 聊天機器人對話

#### CreateChatbotCompletionAsync
建立聊天機器人回應（非串流模式）。

```csharp
var response = await helper.CreateChatbotCompletionAsync(
    chatbotId: "your_chatbot_id",
    message: "What is the weather today?",
    conversationId: null,  // 選填
    attachments: null  // 選填
);
```

**參數：**
- `chatbotId` (string): 聊天機器人 ID
- `message` (string): 訊息內容
- `conversationId` (string?, 選填): 對話 ID
- `attachments` (List<Dictionary<string, string>>?, 選填): 附件列表

**回傳：**
- `Task<JsonElement>`: 包含回應內容的 JSON 元素

#### CreateChatbotCompletionStreamAsync
建立聊天機器人回應（串流模式）。

```csharp
await foreach (var chunk in helper.CreateChatbotCompletionStreamAsync(
    chatbotId: "your_chatbot_id",
    message: "Tell me a long story",
    conversationId: null,
    attachments: null
))
{
    if (chunk.TryGetProperty("content", out var content))
    {
        Console.Write(content.GetString());
    }
}
```

**參數：**
- `chatbotId` (string): 聊天機器人 ID
- `message` (string): 訊息內容
- `conversationId` (string?, 選填): 對話 ID
- `attachments` (List<Dictionary<string, string>>?, 選填): 附件列表

**回傳：**
- `IAsyncEnumerable<JsonElement>`: 非同步串流，產生串流回應

## 錯誤處理

所有非同步方法都包含基本的錯誤處理機制：
- 使用 `try-catch` 捕獲異常
- 檢查 HTTP 回應狀態（使用 `EnsureSuccessStatusCode()`）
- 處理請求異常並輸出錯誤訊息
- 適當地重新拋出異常以便上層處理

## 使用範例

### 完整工作流程範例

```csharp
using System;
using System.Threading.Tasks;
using Utils;

class Program
{
    static async Task Main(string[] args)
    {
        var helper = new MaiAgentHelper("your_api_key");

        try
        {
            // 1. 建立對話
            var conversation = await helper.CreateConversationAsync("web_chat_id");
            var conversationId = conversation.GetProperty("id").GetString();

            // 2. 上傳附件
            var attachment = await helper.UploadAttachmentAsync(conversationId!, "path/to/image.jpg");
            var attachmentId = attachment.GetProperty("id").GetString();

            // 3. 發送訊息
            var message = await helper.SendMessageAsync(
                conversationId!,
                "請看這張圖片",
                new List<string> { attachmentId! }
            );

            Console.WriteLine("訊息已發送！");
        }
        catch (Exception ex)
        {
            Console.WriteLine($"錯誤: {ex.Message}");
        }
    }
}
```

### 串流模式範例

```csharp
var helper = new MaiAgentHelper("your_api_key");

await foreach (var chunk in helper.CreateChatbotCompletionStreamAsync(
    "chatbot_id",
    "講一個故事"))
{
    if (chunk.TryGetProperty("content", out var content) &&
        chunk.TryGetProperty("done", out var done) &&
        !done.GetBoolean())
    {
        Console.Write(content.GetString());
    }
}
Console.WriteLine();
```

## 注意事項

1. 使用前請確保已設定正確的 API 金鑰
2. 所有檔案操作方法都是非同步的，請使用 `await` 關鍵字
3. 檔案上傳時請確認檔案存在且可讀取
4. 串流模式回應需要使用 `await foreach` 來處理
5. 所有 API 呼叫都需要網路連線
6. JsonElement 類型的回傳值需要使用適當的方法（如 `GetProperty()`, `GetString()` 等）來存取資料
7. 建議在 production 環境中實作更完善的錯誤處理和重試機制

## 命名慣例

- **C# 風格方法**（PascalCase）：新增的方法，如 `CreateConversationAsync`, `SendMessageAsync`
- **Python 風格方法**（snake_case）：為了相容性保留的方法，如 `create_knowledge_base`, `list_knowledge_bases`

建議使用 C# 風格的方法（PascalCase），Python 風格的方法主要是為了向後相容。
