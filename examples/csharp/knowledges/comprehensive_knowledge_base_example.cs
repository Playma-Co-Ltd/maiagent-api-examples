using System;
using System.Diagnostics;
using System.Text.Json;
using System.Threading.Tasks;
using Utils;

namespace MaiAgentExamples.Knowledges
{
    public static class ComprehensiveKnowledgeBaseExample
    {
        public static string API_KEY = "<your-api-key>";

        public static async Task Main(string[] args)
        {
            // 綜合知識庫管理範例
            //
            // 展示知識庫 API 的完整使用流程：
            // 1. 創建知識庫
            // 2. 上傳檔案
            // 3. 創建標籤
            // 4. 創建 FAQ
            // 5. 搜尋內容
            // 6. 管理和清理

            Debug.Assert(API_KEY != "<your-api-key>", "Please set your API key");

            var maiagentHelper = new MaiAgentHelper(API_KEY);

            try
            {
                // 1. 創建知識庫
                Console.WriteLine(new string('=', 60));
                Console.WriteLine("1. 創建知識庫");
                Console.WriteLine(new string('=', 60));

                var kbResponseObj = await maiagentHelper.create_knowledge_base(
                    name: "測試知識庫",
                    description: "這是一個用於測試的知識庫"
                );

                var kbResponse = JsonSerializer.Deserialize<JsonElement>(kbResponseObj.ToString()!);
                var kbId = kbResponse.GetProperty("id").GetString();
                Console.WriteLine($"知識庫創建成功！ID: {kbId}");

                // 2. 創建標籤
                Console.WriteLine("\n" + new string('=', 60));
                Console.WriteLine("2. 創建標籤");
                Console.WriteLine(new string('=', 60));

                var labelResponseObj = await maiagentHelper.create_knowledge_base_label(
                    knowledgeBaseId: kbId!,
                    name: "技術文檔"
                );

                var labelResponse = JsonSerializer.Deserialize<JsonElement>(labelResponseObj.ToString()!);
                var labelId = labelResponse.GetProperty("id").GetString();
                Console.WriteLine($"標籤創建成功！ID: {labelId}");

                // 3. 上傳檔案 (需要實際檔案路徑)
                Console.WriteLine("\n" + new string('=', 60));
                Console.WriteLine("3. 上傳檔案");
                Console.WriteLine(new string('=', 60));

                // 注意：這裡需要實際的檔案路徑
                // var filePath = "path/to/your/file.pdf";
                // var fileResponse = await maiagentHelper.upload_knowledge_file(kbId, filePath);
                // Console.WriteLine($"檔案上傳成功！");
                Console.WriteLine("跳過檔案上傳 - 需要實際檔案路徑");

                // 4. 創建 FAQ
                Console.WriteLine("\n" + new string('=', 60));
                Console.WriteLine("4. 創建 FAQ");
                Console.WriteLine(new string('=', 60));

                var faqResponseObj = await maiagentHelper.create_knowledge_base_faq(
                    knowledgeBaseId: kbId!,
                    question: "這個知識庫的用途是什麼？",
                    answer: "這個知識庫用於存儲和管理技術文檔，幫助用戶快速找到所需信息。"
                );

                var faqResponse = JsonSerializer.Deserialize<JsonElement>(faqResponseObj.ToString()!);
                var faqId = faqResponse.GetProperty("id").GetString();
                Console.WriteLine($"FAQ 創建成功！ID: {faqId}");

                // 5. 搜尋知識庫
                Console.WriteLine("\n" + new string('=', 60));
                Console.WriteLine("5. 搜尋知識庫");
                Console.WriteLine(new string('=', 60));

                var searchResultsObj = await maiagentHelper.search_knowledge_base(
                    knowledgeBaseId: kbId!,
                    query: "技術文檔"
                );

                var searchResults = JsonSerializer.Deserialize<JsonElement>(searchResultsObj.ToString()!);
                int resultCount = 0;
                if (searchResults.ValueKind == JsonValueKind.Array)
                {
                    foreach (var _ in searchResults.EnumerateArray())
                    {
                        resultCount++;
                    }
                }
                Console.WriteLine($"搜尋結果數量: {resultCount}");

                // 6. 查看知識庫詳情
                Console.WriteLine("\n" + new string('=', 60));
                Console.WriteLine("6. 查看知識庫詳情");
                Console.WriteLine(new string('=', 60));

                var kbDetailObj = await maiagentHelper.get_knowledge_base(kbId!);
                var kbDetail = JsonSerializer.Deserialize<JsonElement>(kbDetailObj.ToString()!);
                Console.WriteLine($"知識庫名稱: {(kbDetail.TryGetProperty("name", out var name) ? name.GetString() : "N/A")}");
                Console.WriteLine($"知識庫描述: {(kbDetail.TryGetProperty("description", out var desc) ? desc.GetString() : "N/A")}");
                Console.WriteLine($"檔案數量: {(kbDetail.TryGetProperty("files_count", out var filesCount) ? filesCount.ToString() : "0")}");
                Console.WriteLine($"創建時間: {(kbDetail.TryGetProperty("created_at", out var createdAt) ? createdAt.GetString() : "N/A")}");

                // 7. 列出所有相關資源
                Console.WriteLine("\n" + new string('=', 60));
                Console.WriteLine("7. 列出所有相關資源");
                Console.WriteLine(new string('=', 60));

                // 列出標籤
                var labelsObj = await maiagentHelper.list_knowledge_base_labels(kbId!);
                var labels = JsonSerializer.Deserialize<JsonElement>(labelsObj.ToString()!);
                int labelsCount = 0;
                if (labels.TryGetProperty("results", out var labelsResults))
                {
                    foreach (var _ in labelsResults.EnumerateArray())
                    {
                        labelsCount++;
                    }
                }
                Console.WriteLine($"標籤數量: {labelsCount}");

                // 列出 FAQ
                var faqsObj = await maiagentHelper.list_knowledge_base_faqs(kbId!);
                var faqs = JsonSerializer.Deserialize<JsonElement>(faqsObj.ToString()!);
                int faqsCount = 0;
                if (faqs.TryGetProperty("results", out var faqsResults))
                {
                    foreach (var _ in faqsResults.EnumerateArray())
                    {
                        faqsCount++;
                    }
                }
                Console.WriteLine($"FAQ 數量: {faqsCount}");

                // 列出檔案
                var filesObj = await maiagentHelper.list_knowledge_base_files(kbId!);
                var files = JsonSerializer.Deserialize<JsonElement>(filesObj.ToString()!);
                int filesListCount = 0;
                if (files.TryGetProperty("results", out var filesResults))
                {
                    foreach (var _ in filesResults.EnumerateArray())
                    {
                        filesListCount++;
                    }
                }
                Console.WriteLine($"檔案數量: {filesListCount}");

                // 8. 清理資源 (可選)
                Console.WriteLine("\n" + new string('=', 60));
                Console.WriteLine("8. 清理資源");
                Console.WriteLine(new string('=', 60));

                // 取消註解以執行清理
                // Console.WriteLine("刪除 FAQ...");
                // await maiagentHelper.delete_knowledge_base_faq(kbId!, faqId!);
                //
                // Console.WriteLine("刪除標籤...");
                // await maiagentHelper.delete_knowledge_base_label(kbId!, labelId!);
                //
                // Console.WriteLine("刪除知識庫...");
                // await maiagentHelper.delete_knowledge_base(kbId!);
                //
                // Console.WriteLine("清理完成！");

                Console.WriteLine("跳過清理 - 取消註解以執行實際刪除");

                Console.WriteLine("\n" + new string('=', 60));
                Console.WriteLine("範例執行完成！");
                Console.WriteLine(new string('=', 60));

            }
            catch (Exception e)
            {
                Console.WriteLine($"操作失敗：{e}");
            }
        }
    }
}
