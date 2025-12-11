using System;
using System.Diagnostics;
using System.Text.Json;
using System.Threading.Tasks;
using Utils;

namespace MaiAgentExamples.Knowledges
{
    public static class CreateKnowledgeBase
    {
        public static string API_KEY = "<your-api-key>";

        // 知識庫基本資訊
        public static string KNOWLEDGE_BASE_NAME = "My Knowledge Base";
        public static string KNOWLEDGE_BASE_DESCRIPTION = "This is a sample knowledge base for testing purposes.";
        public static string KNOWLEDGE_BASE_LANGUAGE = "zh-TW";

        public static async Task Main(string[] args)
        {
            // 創建知識庫範例
            //
            // 展示如何使用新的知識庫 API 創建知識庫

            Debug.Assert(API_KEY != "<your-api-key>", "Please set your API key");

            var maiagentHelper = new MaiAgentHelper(API_KEY);

            try
            {
                // 創建知識庫
                var createResponse = await maiagentHelper.create_knowledge_base(
                    name: KNOWLEDGE_BASE_NAME,
                    description: KNOWLEDGE_BASE_DESCRIPTION,
                    language: KNOWLEDGE_BASE_LANGUAGE
                );

                var response = JsonSerializer.Deserialize<JsonElement>(createResponse.ToString()!);

                Console.WriteLine($"知識庫創建成功！");
                Console.WriteLine($"知識庫 ID: {(response.TryGetProperty("id", out var id) ? id.GetString() : "N/A")}");
                Console.WriteLine($"知識庫名稱: {(response.TryGetProperty("name", out var name) ? name.GetString() : "N/A")}");
                Console.WriteLine($"知識庫描述: {(response.TryGetProperty("description", out var desc) ? desc.GetString() : "N/A")}");
                Console.WriteLine($"創建時間: {(response.TryGetProperty("created_at", out var createdAt) ? createdAt.GetString() : "N/A")}");

            }
            catch (Exception e)
            {
                Console.WriteLine($"知識庫創建失敗：{e}");
            }
        }
    }
}
