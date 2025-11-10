
using System;
using System.Collections.Generic;
using System.Diagnostics;
using Utils;

public static class manage_knowledge_base_labels {

    public static string API_KEY = "<your-api-key>";
    public static string KNOWLEDGE_BASE_ID = "<your-knowledge-base-id>";  // 你的知識庫 ID

    public static void main() {
        // 知識庫標籤管理範例
        //
        // 展示如何使用新的知識庫 API 管理標籤

        Debug.Assert(API_KEY != "<your-api-key>", "Please set your API key");
        Debug.Assert(KNOWLEDGE_BASE_ID != "<your-knowledge-base-id>", "Please set your knowledge base id");

        var maiagent_helper = new MaiAgentHelper(API_KEY);

        try {
            // 1. 創建標籤
            Console.WriteLine("1. 創建標籤...");
            var label_name = $"測試標籤_{DateTimeOffset.Now.ToUnixTimeSeconds()}";  // 使用時間戳避免重複
            var new_label = maiagent_helper.create_knowledge_base_label(
                knowledge_base_id: KNOWLEDGE_BASE_ID,
                name: label_name
            );
            var label_id = new_label.get("id");
            Console.WriteLine($"標籤創建成功，ID: {label_id}");

            // 2. 列出所有標籤
            Console.WriteLine("\n2. 列出所有標籤...");
            var labels = maiagent_helper.list_knowledge_base_labels(KNOWLEDGE_BASE_ID);

            if (labels.ContainsKey("results")) {
                var label_list = (List<object>)labels["results"];
                Console.WriteLine($"找到 {label_list.Count} 個標籤：");
                foreach (var label in label_list) {
                    Console.WriteLine($"  ID: {label.get("id")}");
                    Console.WriteLine($"  名稱: {label.get("name")}");
                    Console.WriteLine(new string('-', 30));
                }
            }

            // 3. 更新標籤
            if (label_id != null) {
                Console.WriteLine($"\n3. 更新標籤 (ID: {label_id})...");
                var updated_name = $"{label_name} - 更新版";
                var updated_label = maiagent_helper.update_knowledge_base_label(
                    knowledge_base_id: KNOWLEDGE_BASE_ID,
                    label_id: label_id,
                    name: updated_name
                );
                Console.WriteLine("標籤更新成功");
            }

            // 4. 獲取特定標籤
            if (label_id != null) {
                Console.WriteLine($"\n4. 獲取標籤詳情 (ID: {label_id})...");
                var label_detail = maiagent_helper.get_knowledge_base_label(KNOWLEDGE_BASE_ID, label_id);
                Console.WriteLine($"標籤名稱: {label_detail.get("name")}");
            }

            // 5. 刪除標籤 (可選，取消註解以執行)
            // if (label_id != null) {
            //     Console.WriteLine($"\n5. 刪除標籤 (ID: {label_id})...");
            //     maiagent_helper.delete_knowledge_base_label(KNOWLEDGE_BASE_ID, label_id);
            //     Console.WriteLine("標籤刪除成功");
            // }

        } catch (Exception e) {
            Console.WriteLine($"標籤管理失敗：{e}");
        }
    }
}
