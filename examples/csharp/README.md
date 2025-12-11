# C# 範例

這個範例展示如何使用 MaiAgent API 管理助理、發送訊息、管理知識庫、管理常見問題。

## 範例資料夾說明

- [assistants](assistants/): 管理助理的範例
- [messages](messages/): 發送訊息的範例
  - [chatbot_completion.md](messages/chatbot_completion.md): 聊天機器人 API 使用說明
  - [send_message.cs](messages/send_message.cs): 發送訊息範例
  - [send_image_message.cs](messages/send_image_message.cs): 發送圖片訊息範例
  - [webhook_server.cs](messages/webhook_server.cs): Webhook 伺服器範例
- [knowledges](knowledges/): 管理知識庫的範例
- [faqs](faqs/): 管理常見問題的範例
- [batch_qa](batch_qa/): 發送批次問答的範例
- [others](others/): 其他有用的範例

# 使用 MaiAgentHelper

MaiAgentHelper 是一個用於與 MaiAgent API 互動的輔助類別，提供了一系列方便的方法來處理對話、訊息、檔案上傳和知識庫管理等功能。

- 請參考 [utils/maiagent.md](utils/maiagent.md) 了解 MaiAgentHelper 的完整功能和使用方法。

## 設置步驟

1. 安裝 .NET SDK：

建議使用 .NET 8.0 或更新版本

```bash
# Windows (使用 winget)
winget install Microsoft.DotNet.SDK.8

# macOS (使用 Homebrew)
brew install dotnet

# Linux (請參考官方文檔)
# https://learn.microsoft.com/dotnet/core/install/linux
```

2. 還原 NuGet 套件：

```bash
cd examples/csharp
dotnet restore
```

3. 設置環境變數或直接修改程式碼中的 API 金鑰：

在每個範例檔案中，找到以下行並替換為您的 API 金鑰：

```csharp
public static string API_KEY = "<your-api-key>";
```

4. 編譯專案：

```bash
dotnet build
```

5. 執行特定範例：

```bash
# 方法 1: 使用 dotnet run 並指定要執行的類別
dotnet run

# 方法 2: 直接執行編譯後的程式
dotnet run --project MaiAgentExamples.csproj
```

由於專案包含多個 Main 方法，您需要在對應的範例檔案中呼叫其 Main 方法，或者直接修改 [Program.cs](Program.cs:1-52) 來指定要執行的範例。

## 執行範例的方式

本專案採用多 Main 方法設計，每個範例都有自己的 `Main` 方法。您可以透過以下方式執行特定範例：

### 方法 1：修改 Program.cs

編輯 [Program.cs](Program.cs:1-52)，在 Main 方法中呼叫您想執行的範例：

```csharp
static async Task Main(string[] args)
{
    // 執行發送訊息範例
    await MaiAgentExamples.Messages.SendMessage.Main(args);

    // 或執行其他範例
    // await MaiAgentExamples.BatchQA.UploadBatchQAFile.Main(args);
    // await MaiAgentExamples.Knowledges.CreateKnowledgeBase.Main(args);
}
```

然後執行：

```bash
dotnet run
```

### 方法 2：使用 C# 腳本模式（如果已安裝 dotnet-script）

```bash
# 安裝 dotnet-script
dotnet tool install -g dotnet-script

# 執行特定檔案
dotnet script messages/send_message.cs
```

### 方法 3：建立個別專案

為特定範例建立獨立的 .csproj 檔案並執行。

## 專案結構

```
csharp/
├── Program.cs                          # 主程式進入點
├── MaiAgentExamples.csproj            # 專案檔案
├── utils/
│   ├── maiagent.cs                    # MaiAgentHelper 工具類別
│   └── maiagent.md                    # MaiAgentHelper 使用文檔
├── messages/                          # 訊息相關範例
│   ├── send_message.cs
│   ├── send_image_message.cs
│   ├── upload_attachment.cs
│   ├── chatbot_completion.cs
│   └── webhook_server.cs
├── batch_qa/                          # 批次問答範例
│   ├── upload_batch_qa_file.cs
│   └── download_batch_qa_excel.cs
├── knowledges/                        # 知識庫管理範例
│   ├── create_knowledge_base.cs
│   ├── list_knowledge_bases.cs
│   ├── upload_knowledge_file.cs
│   ├── delete_knowledge_file.cs
│   ├── search_knowledge_base.cs
│   ├── manage_knowledge_base_labels.cs
│   ├── manage_knowledge_base_files.cs
│   ├── manage_knowledge_base_faq.cs
│   ├── comprehensive_knowledge_base_example.cs
│   └── batch_upload/                  # 批量上傳工具
│       ├── batch_upload_advanced.cs
│       ├── scan_file_status.cs
│       ├── delete_duplicate_files.cs
│       ├── fix_failed_files.cs
│       └── upload_missing_files.cs
├── faqs/                              # FAQ 管理範例
│   └── add_faq.cs
├── assistants/                        # 助手管理範例
│   ├── create_assistant.cs
│   └── update_assistant.cs
└── others/                            # 其他範例
    └── get_inboxes.cs
```

## 注意事項

1. 請確保您已經取得 MaiAgent API 金鑰
2. 所有範例都需要在程式碼中設定 API_KEY 等必要參數
3. 範例使用 async/await 模式，需要 .NET 8.0 或更新版本
4. 檔案上傳功能需要指定實際存在的檔案路徑
5. Webhook 伺服器範例需要設定正確的監聽埠

## 常見 API 操作

### 建立對話並發送訊息

```csharp
using Utils;

var helper = new MaiAgentHelper("your_api_key");

// 建立對話
var conversation = await helper.CreateConversationAsync("web_chat_id");
var conversationId = conversation.GetProperty("id").GetString();

// 發送訊息
var message = await helper.SendMessageAsync(
    conversationId: conversationId!,
    content: "你好！",
    attachments: null
);
```

### 上傳檔案到知識庫

```csharp
using Utils;

var helper = new MaiAgentHelper("your_api_key");

// 上傳知識檔案
var result = await helper.UploadKnowledgeFileAsync(
    chatbotId: "your_chatbot_id",
    filePath: "path/to/file.pdf"
);
```

### 使用聊天機器人 API（串流模式）

```csharp
using Utils;

var helper = new MaiAgentHelper("your_api_key");

// 串流模式對話
await foreach (var chunk in helper.CreateChatbotCompletionStreamAsync(
    chatbotId: "your_chatbot_id",
    message: "講一個故事"
))
{
    if (chunk.TryGetProperty("content", out var content))
    {
        Console.Write(content.GetString());
    }
}
```

## Python 與 C# 對照

本專案包含 Python 和 C# 兩種語言的範例：

- Python 範例位於 `python/` 資料夾
- C# 範例位於 `csharp/` 資料夾（本資料夾）

兩者功能相同，可根據您的開發需求選擇使用。

### 主要語法差異

| 功能 | Python | C# |
|------|--------|-----|
| 變數宣告 | `api_key = "xxx"` | `var apiKey = "xxx";` 或 `string apiKey = "xxx";` |
| 函數呼叫 | `helper.send_message(...)` | `await helper.SendMessageAsync(...)` |
| 錯誤處理 | `try: ... except Exception as e:` | `try { ... } catch (Exception e) { ... }` |
| 字典/物件 | `response["id"]` | `response.GetProperty("id").GetString()` |
| 陣列遍歷 | `for item in items:` | `foreach (var item in items) { ... }` |
| 非同步 | `async def func():` | `async Task FuncAsync() { ... }` |
| 等待非同步 | `await func()` | `await FuncAsync()` |

## 取得協助

如需更多協助，請參考：
- [MaiAgentHelper 文檔](utils/maiagent.md)
- [MaiAgent API 官方文檔](https://docs.maiagent.ai/)
- 或在 GitHub 提出 Issue
