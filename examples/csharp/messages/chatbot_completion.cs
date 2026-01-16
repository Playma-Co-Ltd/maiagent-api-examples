using System;
using System.Collections.Generic;
using System.IO;
using System.Text.Json;
using System.Threading.Tasks;
using Utils;

namespace MaiAgentExamples.Messages
{
    public static class ChatbotCompletion
    {
        public static string TEST_IMAGE_PATH = Path.Combine(
            Directory.GetParent(Directory.GetCurrentDirectory())?.Parent?.Parent?.FullName ?? "",
            "inputs",
            "cat.jpg"
        );

        public static string TEST_PDF_PATH = Path.Combine(
            Directory.GetParent(Directory.GetCurrentDirectory())?.Parent?.Parent?.FullName ?? "",
            "inputs",
            "sample.pdf"
        );

        public static Dictionary<string, string> TEST_PROMPTS = new()
        {
            { "streaming", "使用串流模式測試：請給我一個笑話" },
            { "non_streaming", "不使用串流模式測試：請給我一個笑話" },
            { "conversation_first", "你好，請記住我說我叫小明" },
            { "conversation_second", "我剛才說我叫什麼名字？" },
            { "image_analysis", "請描述這張圖片的內容" },
            { "pdf_analysis", "請分析這個PDF文件的內容並總結主要信息" }
        };

        public static string SEPARATOR_LINE = new string('=', 50);

        // 獲取 MaiAgent 幫助器實例
        private static MaiAgentHelper GetMaiAgentHelper()
        {
            // storageUrl 不再需要，上傳 URL 會從 API response 自動取得
            return new MaiAgentHelper(Config.API_KEY, Config.BASE_URL);
        }

        // 打印分隔線和標題
        private static void PrintSeparator(string title)
        {
            Console.WriteLine($"\n{SEPARATOR_LINE}");
            Console.WriteLine($"測試場景: {title}");
            Console.WriteLine($"{SEPARATOR_LINE}\n");
        }

        // 創建附件數據
        private static async Task<List<Dictionary<string, string>>?> CreateAttachmentAsync(
            MaiAgentHelper maiagentHelper,
            string imagePath)
        {
            if (string.IsNullOrEmpty(imagePath))
            {
                return new List<Dictionary<string, string>>();
            }

            Console.WriteLine($"正在上傳圖片: {imagePath}");
            var uploadResponse = await maiagentHelper.UploadAttachmentWithoutConversationAsync(imagePath, "image");
            Console.WriteLine($"上傳響應: {JsonSerializer.Serialize(uploadResponse)}");

            if (uploadResponse.ValueKind == JsonValueKind.Undefined)
            {
                return null;
            }

            var attachments = new List<Dictionary<string, string>>
            {
                new()
                {
                    { "id", uploadResponse.GetProperty("id").GetString()! },
                    { "type", "image" },
                    { "filename", uploadResponse.GetProperty("filename").GetString()! },
                    { "file", uploadResponse.GetProperty("file").GetString()! }
                }
            };

            Console.WriteLine($"附件數據準備完成: {JsonSerializer.Serialize(attachments)}");
            return attachments;
        }

        // 處理串流響應
        private static void HandleStreamingResponse(JsonElement data)
        {
            if (data.TryGetProperty("content", out var content) &&
                data.TryGetProperty("done", out var done) &&
                !done.GetBoolean())
            {
                Console.Write(content.GetString());
            }
        }

        /// <summary>
        /// 測試場景1: 使用串流模式與聊天機器人對話
        ///
        /// 流程:
        /// 1. 調用 create_chatbot_completion API，設置 isStreaming=True
        /// 2. 逐步接收並顯示串流響應
        /// </summary>
        private static async Task TestWithStreamingAsync()
        {
            PrintSeparator("使用串流模式");
            var maiagentHelper = GetMaiAgentHelper();

            try
            {
                await foreach (var data in maiagentHelper.CreateChatbotCompletionStreamAsync(
                    Config.CHATBOT_ID,
                    TEST_PROMPTS["streaming"]))
                {
                    HandleStreamingResponse(data);
                }
                Console.WriteLine();
            }
            catch (Exception e)
            {
                Console.WriteLine($"錯誤: {e.Message}");
            }
        }

        /// <summary>
        /// 測試場景2: 使用非串流模式與聊天機器人對話
        /// </summary>
        private static async Task TestWithoutStreamingAsync()
        {
            PrintSeparator("不使用串流模式");
            var maiagentHelper = GetMaiAgentHelper();

            try
            {
                var response = await maiagentHelper.CreateChatbotCompletionAsync(
                    Config.CHATBOT_ID,
                    TEST_PROMPTS["non_streaming"]);
                Console.WriteLine($"回應: {JsonSerializer.Serialize(response, new JsonSerializerOptions { WriteIndented = true })}");
            }
            catch (Exception e)
            {
                Console.WriteLine($"錯誤: {e.Message}");
            }
        }

        /// <summary>
        /// 測試場景3: 測試對話上下文功能
        ///
        /// 流程:
        /// 1. 第一次調用 API 不帶 conversationId
        /// 2. 從響應中獲取 conversationId
        /// 3. 第二次調用帶上 conversationId 進行對話
        /// </summary>
        private static async Task TestConversationFlowAsync()
        {
            PrintSeparator("對話流程測試");
            var maiagentHelper = GetMaiAgentHelper();

            try
            {
                // 第一次對話，不帶 conversationId
                Console.WriteLine("第一次對話（無 conversationId）:");
                var firstResponse = await maiagentHelper.CreateChatbotCompletionAsync(
                    Config.CHATBOT_ID,
                    TEST_PROMPTS["conversation_first"]);

                if (firstResponse.ValueKind != JsonValueKind.Object)
                {
                    Console.WriteLine($"錯誤：收到非預期的回應類型: {firstResponse.ValueKind}");
                    return;
                }

                Console.WriteLine($"第一次響應: {JsonSerializer.Serialize(firstResponse, new JsonSerializerOptions { WriteIndented = true })}");

                // 從響應中獲取 conversationId
                if (!firstResponse.TryGetProperty("conversationId", out var conversationIdElement))
                {
                    Console.WriteLine("錯誤：回應中沒有 conversationId");
                    return;
                }

                var conversationId = conversationIdElement.GetString();
                Console.WriteLine($"\n獲取到的 conversationId: {conversationId}\n");

                // 第二次對話，使用獲取到的 conversationId
                Console.WriteLine("第二次對話（帶 conversationId）:");
                await foreach (var data in maiagentHelper.CreateChatbotCompletionStreamAsync(
                    Config.CHATBOT_ID,
                    TEST_PROMPTS["conversation_second"],
                    conversationId))
                {
                    HandleStreamingResponse(data);
                }
                Console.WriteLine();
            }
            catch (Exception e)
            {
                Console.WriteLine($"錯誤: {e.Message}");
            }
        }

        /// <summary>
        /// 測試場景4: 測試帶附件的對話功能
        /// </summary>
        private static async Task TestConversationWithImageAttachmentAsync()
        {
            PrintSeparator("帶附件的對話測試");
            var maiagentHelper = GetMaiAgentHelper();

            try
            {
                // 準備附件
                var attachments = await CreateAttachmentAsync(maiagentHelper, TEST_IMAGE_PATH);
                if (attachments == null)
                {
                    Console.WriteLine("附件準備失敗");
                    return;
                }

                Console.WriteLine("\n開始分析圖片...");
                await foreach (var data in maiagentHelper.CreateChatbotCompletionStreamAsync(
                    Config.CHATBOT_ID,
                    TEST_PROMPTS["image_analysis"],
                    attachments: attachments))
                {
                    HandleStreamingResponse(data);
                }
                Console.WriteLine();
            }
            catch (Exception e)
            {
                Console.WriteLine($"錯誤: {e.Message}");
            }
        }

        /// <summary>
        /// 測試場景5: 測試帶PDF附件的對話功能
        /// </summary>
        private static async Task TestConversationWithPdfAttachmentAsync()
        {
            PrintSeparator("帶PDF附件的對話測試");
            var maiagentHelper = GetMaiAgentHelper();

            try
            {
                // 準備附件
                Console.WriteLine($"正在上傳PDF文件: {TEST_PDF_PATH}");
                var uploadResponse = await maiagentHelper.UploadAttachmentWithoutConversationAsync(TEST_PDF_PATH, "other");
                Console.WriteLine($"上傳響應: {JsonSerializer.Serialize(uploadResponse)}");

                if (uploadResponse.ValueKind == JsonValueKind.Undefined)
                {
                    Console.WriteLine("PDF附件準備失敗");
                    return;
                }

                // 創建PDF附件數據
                var attachments = new List<Dictionary<string, string>>
                {
                    new()
                    {
                        { "id", uploadResponse.GetProperty("id").GetString()! },
                        { "type", "other" },
                        { "filename", uploadResponse.GetProperty("filename").GetString()! },
                        { "file", uploadResponse.GetProperty("file").GetString()! }
                    }
                };

                Console.WriteLine($"PDF附件數據準備完成: {JsonSerializer.Serialize(attachments)}");
                Console.WriteLine("\n開始分析PDF文件...");

                var response = await maiagentHelper.CreateChatbotCompletionAsync(
                    Config.CHATBOT_ID,
                    TEST_PROMPTS["pdf_analysis"],
                    attachments: attachments);

                Console.WriteLine($"回應: {JsonSerializer.Serialize(response, new JsonSerializerOptions { WriteIndented = true })}");
            }
            catch (Exception e)
            {
                Console.WriteLine($"錯誤: {e.Message}");
            }
        }

        // 主函數：運行所有測試場景
        public static async Task Main(string[] args)
        {
            await TestWithStreamingAsync();
            await TestWithoutStreamingAsync();
            await TestConversationFlowAsync();
            await TestConversationWithImageAttachmentAsync();
            await TestConversationWithPdfAttachmentAsync();
        }
    }
}
