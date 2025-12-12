# 發送訊息範例

這個範例展示如何使用 MaiAgent API 發送訊息、設置 webhook 伺服器接收回應。

## 檔案說明

1. [send_message.cs](send_message.cs): 用於向 MaiAgent API 建立對話、發送訊息的程式碼。
2. [send_image_message.cs](send_image_message.cs): 用於向 MaiAgent API 建立對話、發送圖片訊息的程式碼。
3. [webhook_server.cs](webhook_server.cs): 用於接收 webhook 通知的 ASP.NET Core 伺服器。
4. [upload_attachment.cs](upload_attachment.cs): 用於上傳檔案到 MaiAgent API 的程式碼。
5. [chatbot_completion.cs](chatbot_completion.cs): 用於與聊天機器人進行對話的程式碼（支援串流和非串流模式）。

## 設置步驟

### 1. 安裝 localtunnel（用於 webhook 測試）

```bash
npm install -g localtunnel
```

### 2. 設定 API 金鑰和參數

在每個範例檔案中設定您的 API 金鑰和相關參數：

**send_message.cs**:
```csharp
public static string API_KEY = "<your-api-key>";
public static string WEB_CHAT_ID = "<your-web-chat-id>";
public static string TEXT_MESSAGE = "你好！";
```

**send_image_message.cs**:
```csharp
public static string API_KEY = "<your-api-key>";
public static string WEB_CHAT_ID = "<your-web-chat-id>";
public static string IMAGE_PATH = "path/to/image.jpg";
public static string TEXT_MESSAGE = "請看這張圖片";
```

**chatbot_completion.cs**:
```csharp
public static string API_KEY = "<your-api-key>";
public static string CHATBOT_ID = "<your-chatbot-id>";
```

### 3. 執行 Webhook 伺服器（可選）

如果您需要接收 webhook 通知，請先啟動 webhook 伺服器：

**方法 1：修改 Program.cs**

編輯 [../Program.cs](../Program.cs)：

```csharp
static async Task Main(string[] args)
{
    await MaiAgentExamples.Messages.WebhookServer.Main(args);
}
```

然後執行：

```bash
cd examples/csharp
dotnet run
```

**方法 2：使用 dotnet script**

```bash
dotnet script messages/webhook_server.cs
```

伺服器將在 `http://0.0.0.0:6666` 上啟動。

### 4. 使用 localtunnel 暴露本地伺服器（可選）

在另一個終端視窗中執行：

```bash
lt --port 6666
```

這將提供一個公開 URL，例如：`https://random-name.loca.lt`

### 5. 在 MaiAgent 後台配置 webhook URL

將 localtunnel 提供的 URL 加上 `/webhook` 路徑配置到 MaiAgent 後台：

```
https://random-name.loca.lt/webhook
```

## 使用方式

### 1. 發送文字訊息

修改 [../Program.cs](../Program.cs)：

```csharp
static async Task Main(string[] args)
{
    await MaiAgentExamples.Messages.SendMessage.Main(args);
}
```

執行：

```bash
cd examples/csharp
dotnet run
```

此範例會建立一個對話並發送一則測試訊息。

### 2. 發送圖片訊息

修改 [../Program.cs](../Program.cs)：

```csharp
static async Task Main(string[] args)
{
    await MaiAgentExamples.Messages.SendImageMessage.Main(args);
}
```

執行：

```bash
cd examples/csharp
dotnet run
```

### 3. 上傳附件

修改 [../Program.cs](../Program.cs)：

```csharp
static async Task Main(string[] args)
{
    await MaiAgentExamples.Messages.UploadAttachment.Main(args);
}
```

執行：

```bash
cd examples/csharp
dotnet run
```

### 4. 使用聊天機器人 API

修改 [../Program.cs](../Program.cs)：

```csharp
static async Task Main(string[] args)
{
    await MaiAgentExamples.Messages.ChatbotCompletion.Main(args);
}
```

執行：

```bash
cd examples/csharp
dotnet run
```

## 完整範例：發送圖片訊息

```csharp
using System;
using System.Collections.Generic;
using System.IO;
using System.Threading.Tasks;
using Utils;

namespace MaiAgentExamples.Messages
{
    class Example
    {
        static async Task Main(string[] args)
        {
            var apiKey = "<your-api-key>";
            var webChatId = "<your-web-chat-id>";
            var imagePath = "path/to/image.jpg";

            var helper = new MaiAgentHelper(apiKey);

            // 1. 建立對話
            Console.WriteLine("建立對話...");
            var conversation = await helper.CreateConversationAsync(webChatId);
            var conversationId = conversation.GetProperty("id").GetString();
            Console.WriteLine($"對話 ID: {conversationId}");

            // 2. 上傳圖片附件
            Console.WriteLine("上傳圖片...");
            var attachment = await helper.UploadAttachmentAsync(conversationId!, imagePath);
            var attachmentId = attachment.GetProperty("id").GetString();
            Console.WriteLine($"附件 ID: {attachmentId}");

            // 3. 發送訊息
            Console.WriteLine("發送訊息...");
            var message = await helper.SendMessageAsync(
                conversationId: conversationId!,
                content: "請看這張圖片",
                attachments: new List<string> { attachmentId! }
            );

            Console.WriteLine("訊息已發送！");
            Console.WriteLine($"訊息內容: {message.GetProperty("content").GetString()}");
        }
    }
}
```

## 聊天機器人 API 範例

### 非串流模式

```csharp
using Utils;

var helper = new MaiAgentHelper("your-api-key");

var response = await helper.CreateChatbotCompletionAsync(
    chatbotId: "your-chatbot-id",
    message: "你好！",
    conversationId: null
);

Console.WriteLine(response.GetProperty("content").GetString());
```

### 串流模式

```csharp
using Utils;

var helper = new MaiAgentHelper("your-api-key");

await foreach (var chunk in helper.CreateChatbotCompletionStreamAsync(
    chatbotId: "your-chatbot-id",
    message: "講一個故事",
    conversationId: null
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

## Webhook 伺服器說明

Webhook 伺服器使用 ASP.NET Core 建立，監聽 POST 請求並顯示接收到的資料。

伺服器會：
1. 監聽 `http://0.0.0.0:6666/webhook`
2. 接收 JSON 格式的 webhook 通知
3. 在控制台顯示接收到的資料
4. 回應 200 OK 狀態碼

## 注意事項

1. **Webhook 伺服器**：
   - 在發送訊息之前，請確保 webhook 伺服器正在運作，以便接收回應
   - webhook 伺服器使用 `localtunnel` 將本機伺服器暴露給網際網路
   - 每次重新啟動伺服器時，請務必在 MaiAgent 後台更新 webhook URL

2. **API 金鑰**：
   - 請確保已設定正確的 API 金鑰
   - API 金鑰應該妥善保管，不要提交到版本控制系統

3. **檔案路徑**：
   - 圖片路徑必須是有效的檔案路徑
   - 支援常見的圖片格式（JPG、PNG、GIF 等）

4. **網路環境**：
   - 請確保已安裝 Node.js 和 npm，以便能夠安裝和使用 localtunnel
   - localtunnel 需要網路連線才能正常運作

5. **對話 ID**：
   - 對話 ID 可以用於多輪對話
   - 不帶 conversationId 參數會建立新對話

## 相關文檔

- [MaiAgentHelper 使用文檔](../utils/maiagent.md)
- [Chatbot Completion API 說明](chatbot_completion.md)
- [檔案上傳功能說明](upload_attachment.md)
- [MaiAgent API 官方文檔](https://docs.maiagent.ai/)
