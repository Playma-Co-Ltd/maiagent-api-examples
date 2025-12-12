# Chatbot Completion API 使用說明

這個範例展示如何使用 MaiAgent API 與聊天機器人進行對話，包含串流模式、非串流模式、多輪對話以及帶附件的對話等場景。

## 測試場景

### 1. 串流模式對話

使用串流模式即時獲取聊天機器人的回應。

```csharp
// C# 範例 - 串流模式
using Utils;

var helper = new MaiAgentHelper("your-api-key");

await foreach (var chunk in helper.CreateChatbotCompletionStreamAsync(
    chatbotId: "your-chatbot-id",
    message: "使用串流模式測試：請給我一個笑話",
    conversationId: null,
    attachments: null
))
{
    if (chunk.TryGetProperty("conversationId", out var convId))
    {
        Console.WriteLine($"Conversation ID: {convId.GetString()}");
    }

    if (chunk.TryGetProperty("content", out var content))
    {
        Console.Write(content.GetString());  // 逐步輸出內容
    }

    if (chunk.TryGetProperty("done", out var done) && done.GetBoolean())
    {
        Console.WriteLine("\n對話結束");
    }
}
```

**回應格式**：
```json
{
    "conversationId": "conv_xxx",
    "content": "從前有一隻",
    "done": false
}
{
    "conversationId": "conv_xxx",
    "content": "小狗在玩球",
    "done": false
}
{
    "conversationId": "conv_xxx",
    "content": "",
    "done": true
}
```

### 2. 非串流模式對話

一次性獲取完整的回應內容。

```csharp
// C# 範例 - 非串流模式
using Utils;

var helper = new MaiAgentHelper("your-api-key");

var response = await helper.CreateChatbotCompletionAsync(
    chatbotId: "your-chatbot-id",
    message: "不使用串流模式測試：請給我一個笑話",
    conversationId: null,
    attachments: null
);

var conversationId = response.GetProperty("conversationId").GetString();
var content = response.GetProperty("content").GetString();
var done = response.GetProperty("done").GetBoolean();

Console.WriteLine($"Conversation ID: {conversationId}");
Console.WriteLine($"Content: {content}");
Console.WriteLine($"Done: {done}");  // 非串流模式下永遠為 true
```

**回應格式**：
```json
{
    "conversationId": "conv_xxx",
    "content": "從前有一隻小狗在玩球...",
    "done": true
}
```

### 3. 多輪對話

使用 conversationId 維持對話上下文。

```csharp
// C# 範例 - 多輪對話
using Utils;

var helper = new MaiAgentHelper("your-api-key");
var chatbotId = "your-chatbot-id";

// 第一輪對話
Console.WriteLine("=== 第一輪對話 ===");
var response1 = await helper.CreateChatbotCompletionAsync(
    chatbotId: chatbotId,
    message: "你好，請記住我說我叫小明",
    conversationId: null
);

var conversationId = response1.GetProperty("conversationId").GetString();
var content1 = response1.GetProperty("content").GetString();
Console.WriteLine($"回應: {content1}");
Console.WriteLine($"Conversation ID: {conversationId}");

// 第二輪對話 - 使用相同的 conversationId
Console.WriteLine("\n=== 第二輪對話 ===");
var response2 = await helper.CreateChatbotCompletionAsync(
    chatbotId: chatbotId,
    message: "我剛才說我叫什麼名字？",
    conversationId: conversationId  // 延續對話需附上 conversationId
);

var content2 = response2.GetProperty("content").GetString();
Console.WriteLine($"回應: {content2}");  // 應該回答 "小明"
```

**第一次回應**：
```json
{
    "conversationId": "conv_xxx",
    "content": "好的，我記住了，你叫小明",
    "done": true
}
```

**第二次回應**：
```json
{
    "conversationId": "conv_xxx",
    "content": "你剛才說你叫小明",
    "done": true
}
```

### 4. 帶附件的對話

上傳圖片並進行分析。

#### 4.1 上傳並註冊附件

```csharp
// C# 範例 - 上傳附件
using Utils;

var helper = new MaiAgentHelper("your-api-key");
var imagePath = "path/to/Cat03.jpg";

// 方法 1: 使用 UploadAttachmentWithoutConversationAsync (不需要對話 ID)
var attachment = await helper.UploadAttachmentWithoutConversationAsync(
    filePath: imagePath,
    type: "image"
);

var attachmentId = attachment.GetProperty("id").GetString();
var attachmentType = attachment.GetProperty("type").GetString();
var filename = attachment.GetProperty("filename").GetString();
var fileUrl = attachment.GetProperty("file").GetString();

Console.WriteLine($"附件 ID: {attachmentId}");
Console.WriteLine($"類型: {attachmentType}");
Console.WriteLine($"檔名: {filename}");
Console.WriteLine($"URL: {fileUrl}");
```

#### 4.2 發送帶附件的訊息

```csharp
// C# 範例 - 發送帶附件的訊息
using Utils;
using System.Collections.Generic;

var helper = new MaiAgentHelper("your-api-key");
var chatbotId = "your-chatbot-id";

// 準備附件列表
var attachments = new List<Dictionary<string, string>>
{
    new Dictionary<string, string>
    {
        { "id", attachmentId },
        { "type", "image" },
        { "filename", filename },
        { "file", fileUrl }
    }
};

// 串流模式發送
Console.WriteLine("正在分析圖片...");
await foreach (var chunk in helper.CreateChatbotCompletionStreamAsync(
    chatbotId: chatbotId,
    message: "請描述這張圖片的內容",
    conversationId: null,
    attachments: attachments
))
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

**回應流**：
```json
{
    "conversationId": "conv_xxx",
    "content": "這張圖片顯示了一隻",
    "done": false
}
{
    "conversationId": "conv_xxx",
    "content": "可愛的貓咪",
    "done": false
}
{
    "conversationId": "conv_xxx",
    "content": "",
    "done": true
}
```

## 完整範例程式碼

### 範例 1：串流模式多輪對話

```csharp
using System;
using System.Threading.Tasks;
using Utils;

namespace MaiAgentExamples.Messages
{
    class ChatbotStreamExample
    {
        static async Task Main(string[] args)
        {
            var helper = new MaiAgentHelper("your-api-key");
            var chatbotId = "your-chatbot-id";
            string? conversationId = null;

            while (true)
            {
                Console.Write("\n你: ");
                var userMessage = Console.ReadLine();

                if (string.IsNullOrEmpty(userMessage) || userMessage.ToLower() == "exit")
                    break;

                Console.Write("AI: ");

                await foreach (var chunk in helper.CreateChatbotCompletionStreamAsync(
                    chatbotId: chatbotId,
                    message: userMessage,
                    conversationId: conversationId
                ))
                {
                    if (chunk.TryGetProperty("conversationId", out var convId))
                    {
                        conversationId = convId.GetString();
                    }

                    if (chunk.TryGetProperty("content", out var content))
                    {
                        Console.Write(content.GetString());
                    }
                }

                Console.WriteLine();
            }
        }
    }
}
```

### 範例 2：圖片分析

```csharp
using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using Utils;

namespace MaiAgentExamples.Messages
{
    class ImageAnalysisExample
    {
        static async Task Main(string[] args)
        {
            var helper = new MaiAgentHelper("your-api-key");
            var chatbotId = "your-chatbot-id";
            var imagePath = "path/to/image.jpg";

            // 1. 上傳圖片
            Console.WriteLine("正在上傳圖片...");
            var attachment = await helper.UploadAttachmentWithoutConversationAsync(
                filePath: imagePath,
                type: "image"
            );

            var attachmentId = attachment.GetProperty("id").GetString();
            var filename = attachment.GetProperty("filename").GetString();
            var fileUrl = attachment.GetProperty("file").GetString();

            Console.WriteLine($"圖片上傳成功！ID: {attachmentId}");

            // 2. 發送帶附件的訊息
            var attachments = new List<Dictionary<string, string>>
            {
                new Dictionary<string, string>
                {
                    { "id", attachmentId! },
                    { "type", "image" },
                    { "filename", filename! },
                    { "file", fileUrl! }
                }
            };

            Console.WriteLine("\n正在分析圖片...");
            Console.Write("AI: ");

            await foreach (var chunk in helper.CreateChatbotCompletionStreamAsync(
                chatbotId: chatbotId,
                message: "請詳細描述這張圖片的內容",
                conversationId: null,
                attachments: attachments
            ))
            {
                if (chunk.TryGetProperty("content", out var content))
                {
                    Console.Write(content.GetString());
                }
            }

            Console.WriteLine();
        }
    }
}
```

## 使用須知

### 1. 對話模式選擇

- **串流模式 (Streaming)**：適合需要即時顯示回應的場景
  - 使用 `CreateChatbotCompletionStreamAsync()`
  - 逐步接收內容，使用 `await foreach` 處理
  - 適合長文本生成

- **非串流模式 (Non-streaming)**：適合需要一次性獲取完整回應的場景
  - 使用 `CreateChatbotCompletionAsync()`
  - 一次性接收完整內容
  - 適合短文本或需要等待完整結果的場景

### 2. 多輪對話

- 使用 `conversationId` 維持對話上下文
- `conversationId` 為 `null` 時會開啟新對話
- 延續對話需附上相同的 `conversationId`

### 3. 附件上傳流程

1. 使用 `UploadAttachmentWithoutConversationAsync()` 上傳檔案
2. 獲取附件資訊（id, type, filename, file）
3. 將附件資訊組成 `List<Dictionary<string, string>>` 格式
4. 在訊息中包含 `attachments` 參數

### 4. 響應狀態說明

- `done=true`: 對話結束，content 可能為空字符串
- `done=false`: 對話進行中，content 包含部分內容

### 5. 錯誤處理

```csharp
try
{
    var response = await helper.CreateChatbotCompletionAsync(
        chatbotId: chatbotId,
        message: message
    );

    // 處理回應
}
catch (HttpRequestException e)
{
    Console.WriteLine($"網路錯誤: {e.Message}");
}
catch (Exception e)
{
    Console.WriteLine($"發生錯誤: {e.Message}");
}
```

## API 端點

- **POST** `/chatbots/{chatbot_id}/completions/`

## 請求格式

```json
{
    "conversation": "conv_xxx",  // 可選，null 表示新對話
    "message": {
        "content": "訊息內容",
        "attachments": [         // 可選
            {
                "id": "att_xxx",
                "type": "image",
                "filename": "image.jpg",
                "file": "https://..."
            }
        ]
    },
    "isStreaming": true          // 在請求主體中設置，不是 URL 參數
}
```

## 注意事項

1. **API 金鑰**：請確保已正確設定 API 金鑰
2. **Chatbot ID**：使用有效的聊天機器人 ID
3. **串流處理**：使用 `await foreach` 處理串流回應
4. **對話 ID**：保存 conversationId 以維持對話上下文
5. **附件格式**：附件必須先上傳並獲取 ID 才能在訊息中使用
6. **錯誤處理**：建議加入適當的錯誤處理機制

## 相關文檔

- [MaiAgentHelper 使用文檔](../utils/maiagent.md)
- [檔案上傳功能說明](upload_attachment.md)
- [MaiAgent API 官方文檔](https://docs.maiagent.ai/)
