
using System;
using System.Collections.Generic;
using System.Diagnostics;
using Utils;

public static class manage_knowledge_base_files {

    public static string API_KEY = "<your-api-key>";
    public static string KNOWLEDGE_BASE_ID = "<your-knowledge-base-id>";   // 你的知識庫 ID

    public static void main() {
        // 知識庫檔案管理範例
        //
        // 展示如何使用新的知識庫 API 管理檔案

        Debug.Assert(API_KEY != "<your-api-key>", "Please set your API key");
        Debug.Assert(KNOWLEDGE_BASE_ID != "<your-knowledge-base-id>", "Please set your knowledge base id");

        var maiagent_helper = new MaiAgentHelper(API_KEY);

        try {
            // 1. 列出所有檔案
            Console.WriteLine("1. 列出知識庫中的所有檔案...");
            var files = maiagent_helper.list_knowledge_base_files(KNOWLEDGE_BASE_ID);

            List<object> file_list = null;
            if (files.ContainsKey("results")) {
                file_list = (List<object>)files["results"];
                Console.WriteLine($"找到 {file_list.Count} 個檔案：");
                foreach (var file in file_list) {
                    Console.WriteLine($"  ID: {file.get("id")}");
                    Console.WriteLine($"  檔名: {file.get("filename")}");
                    Console.WriteLine($"  檔案大小: {file.get("file_size", "N/A")} bytes");
                    Console.WriteLine($"  狀態: {file.get("status")}");
                    Console.WriteLine($"  上傳時間: {file.get("created_at")}");
                    Console.WriteLine(new string('-', 50));
                }
            }

            // 2. 獲取特定檔案詳情
            if (file_list != null && file_list.Count > 0) {
                var file_id = file_list[0].get("id");
                Console.WriteLine($"\n2. 獲取檔案詳情 (ID: {file_id})...");
                var file_detail = maiagent_helper.get_knowledge_base_file(KNOWLEDGE_BASE_ID, file_id);
                Console.WriteLine($"檔名: {file_detail.get("filename")}");
                Console.WriteLine($"檔案類型: {file_detail.get("file_type")}");
                Console.WriteLine($"處理狀態: {file_detail.get("status")}");
                Console.WriteLine($"標籤: {file_detail.get("labels", new List<object>())}");
            }

            // 3. 更新檔案元數據
            if (file_list != null && file_list.Count > 0) {
                var file_id = file_list[0].get("id");
                Console.WriteLine($"\n3. 更新檔案元數據 (ID: {file_id})...");

                // 先獲取知識庫的標籤列表
                var labels_response = maiagent_helper.list_knowledge_base_labels(KNOWLEDGE_BASE_ID);
                var labels_list = labels_response.get("results", new List<object>());

                // 如果有標籤，使用第一個標籤；否則不設定標籤
                object labels_to_set = null;
                if (labels_list.Count > 0) {
                    labels_to_set = new List<Dictionary<string, object>> {
                        new Dictionary<string, object> { {"id", labels_list[0]["id"]} }
                    };
                }

                var updated_file = maiagent_helper.update_knowledge_base_file_metadata(
                    knowledge_base_id: KNOWLEDGE_BASE_ID,
                    file_id: file_id,
                    labels: labels_to_set,
                    raw_user_define_metadata: new Dictionary<string, object> {
                        {"category", "documentation"},
                        {"priority", "high"}
                    }
                );
                Console.WriteLine("檔案元數據更新成功");
                if (labels_to_set != null) {
                    Console.WriteLine($"  已設定標籤: {updated_file.get("labels", new List<object>())}");
                }
                Console.WriteLine($"  已設定自定義元數據: {updated_file.get("rawUserDefineMetadata", new Dictionary<string, object>())}");
            }

            // 4. 批次操作範例
            //Console.WriteLine("\n4. 批次操作範例...");

            // 批次刪除檔案 (可選，取消註解以執行)
            // if (file_list != null && file_list.Count > 0) {
            //     var file_ids = file_list.Take(2).Select(f => f.get("id")).ToList();  // 選取前兩個檔案
            //     Console.WriteLine($"批次刪除檔案 IDs: {string.Join(", ", file_ids)}");
            //     maiagent_helper.batch_delete_knowledge_base_files(KNOWLEDGE_BASE_ID, file_ids);
            //     Console.WriteLine("批次刪除完成");
            // }

            // 批次重新解析檔案 (可選，取消註解以執行)
            // if (file_list != null && file_list.Count > 0) {
            //     var file_parsers = new List<Dictionary<string, object>> {
            //         new Dictionary<string, object> {{"id", file_list[0].get("id")}, {"parser", "pdf_parser"}},
            //         new Dictionary<string, object> {{"id", file_list[1].get("id")}, {"parser", "text_parser"}}
            //     };
            //     Console.WriteLine("批次重新解析檔案...");
            //     maiagent_helper.batch_reparse_knowledge_base_files(KNOWLEDGE_BASE_ID, file_parsers);
            //     Console.WriteLine("批次重新解析完成");
            // }

        } catch (Exception e) {
            Console.WriteLine($"檔案管理失敗：{e}");
        }
    }
}
