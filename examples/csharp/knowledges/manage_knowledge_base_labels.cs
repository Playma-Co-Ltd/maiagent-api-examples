using System;
using System.Diagnostics;
using System.Text.Json;
using System.Threading.Tasks;
using Utils;

namespace MaiAgentExamples.Knowledges
{
    public static class ManageKnowledgeBaseLabels
    {
        public static string API_KEY = "<your-api-key>";
        public static string KNOWLEDGE_BASE_ID = "<your-knowledge-base-id>";  // 你的知識庫 ID

        public static async Task Main(string[] args)
        {
            // 知識庫標籤管理範例
            //
            // 展示如何使用新的知識庫 API 管理標籤

            Debug.Assert(API_KEY != "<your-api-key>", "Please set your API key");
            Debug.Assert(KNOWLEDGE_BASE_ID != "<your-knowledge-base-id>", "Please set your knowledge base id");

            var maiagentHelper = new MaiAgentHelper(API_KEY);

            try
            {
                // 1. 創建標籤
                Console.WriteLine("1. 創建標籤...");
                var labelName = $"測試標籤_{DateTimeOffset.Now.ToUnixTimeSeconds()}";  // 使用時間戳避免重複
                var newLabelResponse = await maiagentHelper.create_knowledge_base_label(
                    knowledgeBaseId: KNOWLEDGE_BASE_ID,
                    name: labelName,
                    color: "#FF5733"
                );

                var newLabel = JsonSerializer.Deserialize<JsonElement>(newLabelResponse.ToString()!);
                var labelId = newLabel.GetProperty("id").GetString();
                Console.WriteLine($"標籤創建成功，ID: {labelId}");

                // 2. 列出所有標籤
                Console.WriteLine("\n2. 列出所有標籤...");
                var labelsResponse = await maiagentHelper.list_knowledge_base_labels(KNOWLEDGE_BASE_ID);
                var labels = JsonSerializer.Deserialize<JsonElement>(labelsResponse.ToString()!);

                if (labels.TryGetProperty("results", out var resultsElement))
                {
                    var labelList = resultsElement.EnumerateArray();
                    Console.WriteLine($"找到標籤：");
                    foreach (var label in labelList)
                    {
                        Console.WriteLine($"  ID: {label.GetProperty("id").GetString()}");
                        Console.WriteLine($"  名稱: {label.GetProperty("name").GetString()}");
                        Console.WriteLine(new string('-', 30));
                    }
                }

                // 3. 更新標籤
                if (labelId != null)
                {
                    Console.WriteLine($"\n3. 更新標籤 (ID: {labelId})...");
                    var updatedName = $"{labelName} - 更新版";
                    var updatedLabelResponse = await maiagentHelper.update_knowledge_base_label(
                        knowledgeBaseId: KNOWLEDGE_BASE_ID,
                        labelId: labelId,
                        name: updatedName,
                        color: "#00FF00"
                    );
                    Console.WriteLine("標籤更新成功");
                }

                // 4. 獲取特定標籤
                if (labelId != null)
                {
                    Console.WriteLine($"\n4. 獲取標籤詳情 (ID: {labelId})...");
                    var labelDetailResponse = await maiagentHelper.get_knowledge_base_label(KNOWLEDGE_BASE_ID, labelId);
                    var labelDetail = JsonSerializer.Deserialize<JsonElement>(labelDetailResponse.ToString()!);
                    Console.WriteLine($"標籤名稱: {labelDetail.GetProperty("name").GetString()}");
                }

                // 5. 刪除標籤 (可選，取消註解以執行)
                // if (labelId != null)
                // {
                //     Console.WriteLine($"\n5. 刪除標籤 (ID: {labelId})...");
                //     await maiagentHelper.delete_knowledge_base_label(KNOWLEDGE_BASE_ID, labelId);
                //     Console.WriteLine("標籤刪除成功");
                // }

            }
            catch (Exception e)
            {
                Console.WriteLine($"標籤管理失敗：{e}");
            }
        }
    }
}
