using System;
using System.Diagnostics;
using System.Text.Json;
using System.Threading.Tasks;
using Utils;

namespace MaiAgentExamples.Knowledges
{
    public static class SearchKnowledgeBase
    {
        public static string API_KEY = "<your-api-key>";
        public static string KNOWLEDGE_BASE_ID = "<your-knowledge-base-id>";   // 你的知識庫 ID
        public static string SEARCH_QUERY = "高鐵";

        public static async Task Main(string[] args)
        {
            // 搜尋知識庫範例
            //
            // 展示如何使用新的知識庫 API 搜尋知識庫內容

            Debug.Assert(API_KEY != "<your-api-key>", "Please set your API key");
            Debug.Assert(KNOWLEDGE_BASE_ID != "<your-knowledge-base-id>", "Please set your knowledge base id");
            Debug.Assert(SEARCH_QUERY != "<your-search-query>", "Please set your search query");

            var maiagentHelper = new MaiAgentHelper(API_KEY);

            try
            {
                // 搜尋知識庫內容
                var searchResponse = await maiagentHelper.search_knowledge_base(KNOWLEDGE_BASE_ID, SEARCH_QUERY);
                var response = JsonSerializer.Deserialize<JsonElement>(searchResponse.ToString()!);

                Console.WriteLine($"搜尋查詢：{SEARCH_QUERY}");
                Console.WriteLine(new string('-', 50));

                if (response.ValueKind == JsonValueKind.Array)
                {
                    var searchResults = response.EnumerateArray();
                    int idx = 0;
                    foreach (var result in searchResults)
                    {
                        idx++;
                        Console.WriteLine($"結果 {idx}:");
                        Console.WriteLine($"內容: {(result.TryGetProperty("text", out var text) ? text.GetString() : "無內容")}");
                        Console.WriteLine($"相似度分數: {(result.TryGetProperty("score", out var score) ? score.ToString() : "N/A")}");

                        if (result.TryGetProperty("chatbot_file", out var chatbotFile) &&
                            chatbotFile.TryGetProperty("filename", out var filename))
                        {
                            Console.WriteLine($"檔案名稱: {filename.GetString()}");
                        }
                        else
                        {
                            Console.WriteLine($"檔案名稱: Unknown");
                        }

                        Console.WriteLine($"頁碼: {(result.TryGetProperty("page_number", out var pageNum) ? pageNum.ToString() : "N/A")}");
                        Console.WriteLine(new string('-', 50));
                    }

                    Console.WriteLine($"找到 {idx} 個相關結果");
                }
                else
                {
                    Console.WriteLine("搜尋結果格式不正確");
                }

            }
            catch (Exception e)
            {
                Console.WriteLine($"搜尋知識庫失敗：{e}");
            }
        }
    }
}
