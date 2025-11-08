
using System;
using System.Collections.Generic;
using System.Diagnostics;
using Utils;

public static class search_knowledge_base {

    public static string API_KEY = "<your-api-key>";
    public static string KNOWLEDGE_BASE_ID = "<your-knowledge-base-id>";   // 你的知識庫 ID
    public static string SEARCH_QUERY = "高鐵";

    public static void main() {
        // 搜尋知識庫範例
        //
        // 展示如何使用新的知識庫 API 搜尋知識庫內容

        Debug.Assert(API_KEY != "<your-api-key>", "Please set your API key");
        Debug.Assert(KNOWLEDGE_BASE_ID != "<your-knowledge-base-id>", "Please set your knowledge base id");
        Debug.Assert(SEARCH_QUERY != "<your-search-query>", "Please set your search query");

        var maiagent_helper = new MaiAgentHelper(API_KEY);

        try {
            // 搜尋知識庫內容
            var response = maiagent_helper.search_knowledge_base(KNOWLEDGE_BASE_ID, SEARCH_QUERY);

            if (response is List<object>) {
                var search_results = (List<object>)response;
                Console.WriteLine($"搜尋查詢：{SEARCH_QUERY}");
                Console.WriteLine($"找到 {search_results.Count} 個相關結果：");
                Console.WriteLine(new string('-', 50));

                for (int idx = 0; idx < search_results.Count; idx++) {
                    var result = search_results[idx];
                    Console.WriteLine($"結果 {idx + 1}:");
                    Console.WriteLine($"內容: {result.get("text", "無內容")}");
                    Console.WriteLine($"相似度分數: {result.get("score", "N/A")}");
                    Console.WriteLine($"檔案名稱: {result.get("chatbot_file", new Dictionary<string, object>()).get("filename", "Unknown")}");
                    Console.WriteLine($"頁碼: {result.get("page_number", "N/A")}");
                    Console.WriteLine(new string('-', 50));
                }
            } else {
                Console.WriteLine("搜尋結果格式不正確");
            }

        } catch (Exception e) {
            Console.WriteLine($"搜尋知識庫失敗：{e}");
        }
    }
}
