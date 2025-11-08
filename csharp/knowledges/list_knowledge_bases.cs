
using System;
using System.Diagnostics;
using Utils;

public static class list_knowledge_bases {

    public static string API_KEY = "<your-api-key>";

    public static void main() {
        // 列出知識庫範例
        //
        // 展示如何使用新的知識庫 API 列出所有知識庫

        Debug.Assert(API_KEY != "<your-api-key>", "Please set your API key");

        var maiagent_helper = new MaiAgentHelper(API_KEY);

        try {
            // 列出所有知識庫
            var response = maiagent_helper.list_knowledge_bases();

            if (response.ContainsKey("results")) {
                var knowledge_bases = response["results"];
                Console.WriteLine($"找到 {knowledge_bases.Count} 個知識庫：");
                Console.WriteLine(new string('-', 50));

                foreach (var kb in knowledge_bases) {
                    Console.WriteLine($"知識庫 ID: {kb.get("id")}");
                    Console.WriteLine($"名稱: {kb.get("name")}");
                    Console.WriteLine($"描述: {kb.get("description", "無描述")}");
                    Console.WriteLine($"檔案數量: {kb.get("files_count", 0)}");
                    Console.WriteLine($"創建時間: {kb.get("created_at")}");
                    Console.WriteLine($"更新時間: {kb.get("updated_at")}");
                    Console.WriteLine(new string('-', 50));
                }
            } else {
                Console.WriteLine("沒有找到知識庫");
            }

        } catch (Exception e) {
            Console.WriteLine($"列出知識庫失敗：{e}");
        }
    }
}
