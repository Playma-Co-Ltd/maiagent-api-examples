using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Text.Json;
using System.Threading.Tasks;
using Utils;

namespace MaiAgentExamples.Knowledges
{
    public static class ManageKnowledgeBaseFiles
    {
        public static string API_KEY = "<your-api-key>";
        public static string KNOWLEDGE_BASE_ID = "<your-knowledge-base-id>";   // 你的知識庫 ID

        public static async Task Main(string[] args)
        {
            // 知識庫檔案管理範例
            //
            // 展示如何使用新的知識庫 API 管理檔案

            Debug.Assert(API_KEY != "<your-api-key>", "Please set your API key");
            Debug.Assert(KNOWLEDGE_BASE_ID != "<your-knowledge-base-id>", "Please set your knowledge base id");

            var maiagentHelper = new MaiAgentHelper(API_KEY);

            try
            {
                // 1. 列出所有檔案
                Console.WriteLine("1. 列出知識庫中的所有檔案...");
                var filesResponse = await maiagentHelper.list_knowledge_base_files(KNOWLEDGE_BASE_ID);
                var files = JsonSerializer.Deserialize<JsonElement>(filesResponse.ToString()!);

                JsonElement.ArrayEnumerator? fileListEnumerator = null;
                string? firstFileId = null;

                if (files.TryGetProperty("results", out var resultsElement))
                {
                    fileListEnumerator = resultsElement.EnumerateArray();
                    Console.WriteLine($"找到檔案：");
                    foreach (var file in fileListEnumerator.Value)
                    {
                        if (firstFileId == null && file.TryGetProperty("id", out var idProp))
                        {
                            firstFileId = idProp.GetString();
                        }

                        Console.WriteLine($"  ID: {(file.TryGetProperty("id", out var id) ? id.GetString() : "N/A")}");
                        Console.WriteLine($"  檔名: {(file.TryGetProperty("filename", out var filename) ? filename.GetString() : "N/A")}");
                        Console.WriteLine($"  檔案大小: {(file.TryGetProperty("file_size", out var size) ? size.ToString() : "N/A")} bytes");
                        Console.WriteLine($"  狀態: {(file.TryGetProperty("status", out var status) ? status.GetString() : "N/A")}");
                        Console.WriteLine($"  上傳時間: {(file.TryGetProperty("created_at", out var createdAt) ? createdAt.GetString() : "N/A")}");
                        Console.WriteLine(new string('-', 50));
                    }
                }

                // 2. 獲取特定檔案詳情
                if (firstFileId != null)
                {
                    Console.WriteLine($"\n2. 獲取檔案詳情 (ID: {firstFileId})...");
                    var fileDetailResponse = await maiagentHelper.get_knowledge_base_file(KNOWLEDGE_BASE_ID, firstFileId);
                    var fileDetail = JsonSerializer.Deserialize<JsonElement>(fileDetailResponse.ToString()!);
                    Console.WriteLine($"檔名: {(fileDetail.TryGetProperty("filename", out var fn) ? fn.GetString() : "N/A")}");
                    Console.WriteLine($"檔案類型: {(fileDetail.TryGetProperty("file_type", out var ft) ? ft.GetString() : "N/A")}");
                    Console.WriteLine($"處理狀態: {(fileDetail.TryGetProperty("status", out var st) ? st.GetString() : "N/A")}");
                    if (fileDetail.TryGetProperty("labels", out var labels))
                    {
                        Console.WriteLine($"標籤: {labels}");
                    }
                }

                // 3. 更新檔案元數據
                if (firstFileId != null)
                {
                    Console.WriteLine($"\n3. 更新檔案元數據 (ID: {firstFileId})...");

                    // 先獲取知識庫的標籤列表
                    var labelsResponse = await maiagentHelper.list_knowledge_base_labels(KNOWLEDGE_BASE_ID);
                    var labelsData = JsonSerializer.Deserialize<JsonElement>(labelsResponse.ToString()!);

                    // 如果有標籤，使用第一個標籤；否則不設定標籤
                    List<string>? labelsToSet = null;
                    if (labelsData.TryGetProperty("results", out var labelsResults) && labelsResults.GetArrayLength() > 0)
                    {
                        var firstLabel = labelsResults.EnumerateArray().First();
                        if (firstLabel.TryGetProperty("id", out var labelId))
                        {
                            labelsToSet = new List<string> { labelId.GetString()! };
                        }
                    }

                    if (labelsToSet != null)
                    {
                        var updatedFileResponse = await maiagentHelper.update_knowledge_base_file_metadata(
                            knowledgeBaseId: KNOWLEDGE_BASE_ID,
                            fileId: firstFileId,
                            labels: labelsToSet
                        );
                        Console.WriteLine("檔案元數據更新成功");
                        var updatedFile = JsonSerializer.Deserialize<JsonElement>(updatedFileResponse.ToString()!);
                        if (updatedFile.TryGetProperty("labels", out var updatedLabels))
                        {
                            Console.WriteLine($"  已設定標籤: {updatedLabels}");
                        }
                    }
                    else
                    {
                        Console.WriteLine("沒有可用的標籤，跳過元數據更新");
                    }
                }

                // 4. 批次操作範例
                //Console.WriteLine("\n4. 批次操作範例...");

                // 批次刪除檔案 (可選，取消註解以執行)
                // if (firstFileId != null)
                // {
                //     Console.WriteLine($"批次刪除檔案 ID: {firstFileId}");
                //     await maiagentHelper.batch_delete_knowledge_base_files(KNOWLEDGE_BASE_ID, new List<string> { firstFileId });
                //     Console.WriteLine("批次刪除完成");
                // }

            }
            catch (Exception e)
            {
                Console.WriteLine($"檔案管理失敗：{e}");
            }
        }
    }
}
