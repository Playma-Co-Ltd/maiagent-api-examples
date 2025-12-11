using System;
using System.Diagnostics;
using System.Text.Json;
using System.Threading.Tasks;
using Utils;

namespace MaiAgentExamples.Knowledges
{
    public static class ManageKnowledgeBaseFAQ
    {
        public static string API_KEY = "<your-api-key>";
        public static string KNOWLEDGE_BASE_ID = "<your-knowledge-base-id>";   // 你的知識庫 ID

        public static async Task Main(string[] args)
        {
            // 知識庫 FAQ 管理範例
            //
            // 展示如何使用新的知識庫 API 管理 FAQ

            Debug.Assert(API_KEY != "<your-api-key>", "Please set your API key");
            Debug.Assert(KNOWLEDGE_BASE_ID != "<your-knowledge-base-id>", "Please set your knowledge base id");

            var maiagentHelper = new MaiAgentHelper(API_KEY);

            try
            {
                // 1. 創建 FAQ
                Console.WriteLine("1. 創建 FAQ...");
                var labels = new List<Dictionary<string, string>>
                {
                    new Dictionary<string, string> { {"id", "label-id"}, {"name", "general"} }
                };
                var newFaqResponse = await maiagentHelper.create_knowledge_base_faq(
                    knowledgeBaseId: KNOWLEDGE_BASE_ID,
                    question: "什麼是 MaiAgent？",
                    answer: "MaiAgent 是一個強大的 AI 助手平台，幫助您建立智能聊天機器人。",
                    labels: labels  // 可選標籤
                );

                var newFaq = JsonSerializer.Deserialize<JsonElement>(newFaqResponse.ToString()!);
                var faqId = newFaq.GetProperty("id").GetString();
                Console.WriteLine($"FAQ 創建成功，ID: {faqId}");

                // 2. 列出所有 FAQ
                Console.WriteLine("\n2. 列出所有 FAQ...");
                var faqsResponse = await maiagentHelper.list_knowledge_base_faqs(KNOWLEDGE_BASE_ID);
                var faqs = JsonSerializer.Deserialize<JsonElement>(faqsResponse.ToString()!);

                if (faqs.TryGetProperty("results", out var resultsElement))
                {
                    var faqList = resultsElement.EnumerateArray();
                    Console.WriteLine($"找到 FAQ：");
                    foreach (var faq in faqList)
                    {
                        Console.WriteLine($"  ID: {(faq.TryGetProperty("id", out var id) ? id.GetString() : "N/A")}");
                        Console.WriteLine($"  問題: {(faq.TryGetProperty("question", out var q) ? q.GetString() : "N/A")}");
                        Console.WriteLine($"  答案: {(faq.TryGetProperty("answer", out var a) ? a.GetString() : "N/A")}");
                        if (faq.TryGetProperty("labels", out var labels))
                        {
                            Console.WriteLine($"  標籤: {labels}");
                        }
                        Console.WriteLine(new string('-', 30));
                    }
                }

                // 3. 更新 FAQ
                if (faqId != null)
                {
                    Console.WriteLine($"\n3. 更新 FAQ (ID: {faqId})...");
                    var updatedFaqResponse = await maiagentHelper.update_knowledge_base_faq(
                        knowledgeBaseId: KNOWLEDGE_BASE_ID,
                        faqId: faqId,
                        question: "什麼是 MaiAgent AI 助手？",
                        answer: "MaiAgent 是一個進階的 AI 助手平台，專為企業和個人提供智能聊天機器人解決方案。"
                    );
                    Console.WriteLine("FAQ 更新成功");
                }

                // 4. 獲取特定 FAQ
                if (faqId != null)
                {
                    Console.WriteLine($"\n4. 獲取 FAQ 詳情 (ID: {faqId})...");
                    var faqDetailResponse = await maiagentHelper.get_knowledge_base_faq(KNOWLEDGE_BASE_ID, faqId);
                    var faqDetail = JsonSerializer.Deserialize<JsonElement>(faqDetailResponse.ToString()!);
                    Console.WriteLine($"問題: {(faqDetail.TryGetProperty("question", out var q) ? q.GetString() : "N/A")}");
                    Console.WriteLine($"答案: {(faqDetail.TryGetProperty("answer", out var a) ? a.GetString() : "N/A")}");
                }

                // 5. 刪除 FAQ (可選，取消註解以執行)
                // if (faqId != null)
                // {
                //     Console.WriteLine($"\n5. 刪除 FAQ (ID: {faqId})...");
                //     await maiagentHelper.delete_knowledge_base_faq(KNOWLEDGE_BASE_ID, faqId);
                //     Console.WriteLine("FAQ 刪除成功");
                // }

            }
            catch (Exception e)
            {
                Console.WriteLine($"FAQ 管理失敗：{e}");
            }
        }
    }
}
