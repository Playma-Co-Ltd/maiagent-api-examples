using System;
using System.Diagnostics;
using System.Text.Json;
using System.Threading.Tasks;
using Utils;

namespace MaiAgentExamples.Knowledges
{
    public static class ListKnowledgeBases
    {
        public static string API_KEY = "<your-api-key>";

        public static async Task Main(string[] args)
        {
            // 列出知識庫範例
            //
            // 展示如何使用新的知識庫 API 列出所有知識庫

            Debug.Assert(API_KEY != "<your-api-key>", "Please set your API key");

            var maiagentHelper = new MaiAgentHelper(API_KEY);

            try
            {
                // 列出所有知識庫
                var listResponse = await maiagentHelper.list_knowledge_bases();
                var response = JsonSerializer.Deserialize<JsonElement>(listResponse.ToString()!);

                if (response.TryGetProperty("results", out var resultsElement))
                {
                    var knowledgeBases = resultsElement.EnumerateArray();
                    int count = 0;

                    Console.WriteLine($"知識庫列表：");
                    Console.WriteLine(new string('-', 50));

                    foreach (var kb in knowledgeBases)
                    {
                        count++;
                        Console.WriteLine($"知識庫 ID: {(kb.TryGetProperty("id", out var id) ? id.GetString() : "N/A")}");
                        Console.WriteLine($"名稱: {(kb.TryGetProperty("name", out var name) ? name.GetString() : "N/A")}");
                        Console.WriteLine($"描述: {(kb.TryGetProperty("description", out var desc) ? desc.GetString() : "無描述")}");
                        Console.WriteLine($"檔案數量: {(kb.TryGetProperty("files_count", out var filesCount) ? filesCount.ToString() : "0")}");
                        Console.WriteLine($"創建時間: {(kb.TryGetProperty("created_at", out var createdAt) ? createdAt.GetString() : "N/A")}");
                        Console.WriteLine($"更新時間: {(kb.TryGetProperty("updated_at", out var updatedAt) ? updatedAt.GetString() : "N/A")}");
                        Console.WriteLine(new string('-', 50));
                    }

                    Console.WriteLine($"找到 {count} 個知識庫");
                }
                else
                {
                    Console.WriteLine("沒有找到知識庫");
                }

            }
            catch (Exception e)
            {
                Console.WriteLine($"列出知識庫失敗：{e}");
            }
        }
    }
}
