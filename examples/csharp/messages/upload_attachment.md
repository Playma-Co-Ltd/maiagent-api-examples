# MaiAgent API 檔案上傳功能說明

本文檔說明如何使用 MaiAgent API 的檔案上傳功能。[upload_attachment.cs](upload_attachment.cs) 腳本提供了一個簡單的示例，展示如何與 API 進行互動。

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

### C# 使用示例 - 方法 1：使用 MaiAgentHelper

最簡單的方式是使用 `MaiAgentHelper` 類別：

```csharp
using System;
using System.Threading.Tasks;
using Utils;

namespace MaiAgentExamples.Messages
{
    class UploadAttachmentExample
    {
        static async Task Main(string[] args)
        {
            var apiKey = "your_api_key_here";
            var filePath = "path/to/your/file.jpg";

            var helper = new MaiAgentHelper(apiKey);

            try
            {
                // 方法 1: 不需要對話 ID（適用於聊天機器人 API）
                var attachment = await helper.UploadAttachmentWithoutConversationAsync(
                    filePath: filePath,
                    type: "image"  // 可選：image, audio, video, document, text
                );

                var attachmentId = attachment.GetProperty("id").GetString();
                var attachmentType = attachment.GetProperty("type").GetString();
                var filename = attachment.GetProperty("filename").GetString();
                var fileUrl = attachment.GetProperty("file").GetString();

                Console.WriteLine($"檔案上傳成功！");
                Console.WriteLine($"ID: {attachmentId}");
                Console.WriteLine($"類型: {attachmentType}");
                Console.WriteLine($"檔名: {filename}");
                Console.WriteLine($"URL: {fileUrl}");

                // 方法 2: 需要對話 ID（適用於一般對話）
                // var conversationId = "your-conversation-id";
                // var attachment2 = await helper.UploadAttachmentAsync(
                //     conversationId: conversationId,
                //     filePath: filePath
                // );
            }
            catch (Exception ex)
            {
                Console.WriteLine($"上傳失敗: {ex.Message}");
            }
        }
    }
}
```

### C# 使用示例 - 方法 2：直接使用 HttpClient

如果您想要更細緻的控制，可以直接使用 `HttpClient`：

```csharp
using System;
using System.IO;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Text.Json;
using System.Threading.Tasks;

namespace MaiAgentExamples.Messages
{
    class UploadAttachmentManual
    {
        static async Task Main(string[] args)
        {
            var apiKey = "your_api_key_here";
            var baseUrl = "https://api.maiagent.ai/api/v1/";
            var filePath = "path/to/your/file.jpg";

            using var httpClient = new HttpClient();
            httpClient.DefaultRequestHeaders.Add("Authorization", $"Api-Key {apiKey}");

            try
            {
                // 準備 multipart/form-data
                using var form = new MultipartFormDataContent();
                using var fileStream = File.OpenRead(filePath);
                using var streamContent = new StreamContent(fileStream);

                // 設定 MIME 類型
                var mimeType = GetMimeType(filePath);
                streamContent.Headers.ContentType = new MediaTypeHeaderValue(mimeType);

                // 添加檔案到表單
                form.Add(streamContent, "file", Path.GetFileName(filePath));

                // 發送請求
                var response = await httpClient.PostAsync($"{baseUrl}attachments/", form);
                response.EnsureSuccessStatusCode();

                // 解析回應
                var jsonResponse = await response.Content.ReadAsStringAsync();
                var result = JsonSerializer.Deserialize<JsonElement>(jsonResponse);

                var attachmentId = result.GetProperty("id").GetString();
                var attachmentType = result.GetProperty("type").GetString();
                var filename = result.GetProperty("filename").GetString();
                var fileUrl = result.GetProperty("file").GetString();

                Console.WriteLine($"檔案上傳成功！");
                Console.WriteLine($"ID: {attachmentId}");
                Console.WriteLine($"類型: {attachmentType}");
                Console.WriteLine($"檔名: {filename}");
                Console.WriteLine($"URL: {fileUrl}");
            }
            catch (HttpRequestException ex)
            {
                Console.WriteLine($"網路錯誤: {ex.Message}");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"上傳失敗: {ex.Message}");
            }
        }

        static string GetMimeType(string filePath)
        {
            var extension = Path.GetExtension(filePath).ToLowerInvariant();
            return extension switch
            {
                ".jpg" or ".jpeg" => "image/jpeg",
                ".png" => "image/png",
                ".gif" => "image/gif",
                ".pdf" => "application/pdf",
                ".txt" => "text/plain",
                ".mp3" => "audio/mpeg",
                ".mp4" => "video/mp4",
                ".docx" => "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                ".xlsx" => "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                _ => "application/octet-stream"
            };
        }
    }
}
```

## 完整工作流程：上傳並使用附件

### 範例：上傳圖片並發送訊息

```csharp
using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using Utils;

namespace MaiAgentExamples.Messages
{
    class UploadAndSendExample
    {
        static async Task Main(string[] args)
        {
            var apiKey = "your-api-key";
            var webChatId = "your-web-chat-id";
            var imagePath = "path/to/image.jpg";

            var helper = new MaiAgentHelper(apiKey);

            try
            {
                // 1. 建立對話
                Console.WriteLine("建立對話...");
                var conversation = await helper.CreateConversationAsync(webChatId);
                var conversationId = conversation.GetProperty("id").GetString();
                Console.WriteLine($"對話 ID: {conversationId}");

                // 2. 上傳圖片
                Console.WriteLine("上傳圖片...");
                var attachment = await helper.UploadAttachmentAsync(
                    conversationId: conversationId!,
                    filePath: imagePath
                );

                var attachmentId = attachment.GetProperty("id").GetString();
                Console.WriteLine($"附件 ID: {attachmentId}");

                // 3. 發送帶附件的訊息
                Console.WriteLine("發送訊息...");
                var message = await helper.SendMessageAsync(
                    conversationId: conversationId!,
                    content: "請看這張圖片",
                    attachments: new List<string> { attachmentId! }
                );

                Console.WriteLine("訊息已發送！");
                Console.WriteLine($"訊息內容: {message.GetProperty("content").GetString()}");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"操作失敗: {ex.Message}");
            }
        }
    }
}
```

### 範例：使用聊天機器人 API 分析圖片

```csharp
using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using Utils;

namespace MaiAgentExamples.Messages
{
    class ChatbotImageAnalysis
    {
        static async Task Main(string[] args)
        {
            var apiKey = "your-api-key";
            var chatbotId = "your-chatbot-id";
            var imagePath = "path/to/image.jpg";

            var helper = new MaiAgentHelper(apiKey);

            try
            {
                // 1. 上傳圖片（不需要對話 ID）
                Console.WriteLine("上傳圖片...");
                var attachment = await helper.UploadAttachmentWithoutConversationAsync(
                    filePath: imagePath,
                    type: "image"
                );

                var attachmentId = attachment.GetProperty("id").GetString();
                var filename = attachment.GetProperty("filename").GetString();
                var fileUrl = attachment.GetProperty("file").GetString();

                Console.WriteLine($"圖片上傳成功！ID: {attachmentId}");

                // 2. 準備附件資訊
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

                // 3. 使用串流模式分析圖片
                Console.WriteLine("\n正在分析圖片...");
                Console.Write("AI: ");

                await foreach (var chunk in helper.CreateChatbotCompletionStreamAsync(
                    chatbotId: chatbotId,
                    message: "請詳細描述這張圖片",
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
            catch (Exception ex)
            {
                Console.WriteLine($"操作失敗: {ex.Message}");
            }
        }
    }
}
```

## 支援的檔案類型

MaiAgent API 支援多種檔案類型：

### 圖片
- JPEG (.jpg, .jpeg)
- PNG (.png)
- GIF (.gif)
- BMP (.bmp)
- WebP (.webp)

### 音訊
- MP3 (.mp3)
- WAV (.wav)
- OGG (.ogg)
- M4A (.m4a)

### 影片
- MP4 (.mp4)
- AVI (.avi)
- MOV (.mov)
- WMV (.wmv)

### 文件
- PDF (.pdf)
- Word (.doc, .docx)
- Excel (.xls, .xlsx)
- PowerPoint (.ppt, .pptx)
- 純文字 (.txt)
- Markdown (.md)

## 注意事項

1. **檔案大小限制**
   - 確保檔案大小不超過 API 限制
   - 建議參考 API 文檔了解具體限制

2. **API 金鑰安全**
   - 確保您已獲取有效的 API 金鑰
   - API 金鑰應妥善保管，不要提交到版本控制系統

3. **檔案路徑**
   - 檔案路徑必須是有效且可讀取的
   - 建議使用絕對路徑或相對於執行目錄的路徑

4. **MIME 類型**
   - 系統會自動根據檔案副檔名判斷 MIME 類型
   - 也可以手動指定 MIME 類型

5. **錯誤處理**
   - 建議加入完善的錯誤處理機制
   - 檢查 HTTP 狀態碼和回應內容

6. **上傳模式選擇**
   - **有對話 ID**：使用 `UploadAttachmentAsync()` - 適用於一般對話
   - **無對話 ID**：使用 `UploadAttachmentWithoutConversationAsync()` - 適用於聊天機器人 API

## 相關方法

### MaiAgentHelper 提供的方法

```csharp
// 方法 1: 不需要對話 ID
public async Task<JsonElement> UploadAttachmentWithoutConversationAsync(
    string filePath,
    string type = "image"
)

// 方法 2: 需要對話 ID
public async Task<JsonElement> UploadAttachmentAsync(
    string conversationId,
    string filePath
)
```

## 相關文檔

- [MaiAgentHelper 使用文檔](../utils/maiagent.md)
- [Chatbot Completion API 說明](chatbot_completion.md)
- [發送訊息範例](README.md)
- [MaiAgent API 官方文檔](https://docs.maiagent.ai/)
