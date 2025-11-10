
using System;
using System.Collections.Generic;
using System.Diagnostics;
using Utils;

public static class comprehensive_knowledge_base_example {

    public static string API_KEY = "<your-api-key>";

    public static void main() {
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

        var maiagent_helper = new MaiAgentHelper(API_KEY);

        try {
            // 1. 創建知識庫
            Console.WriteLine(new string('=', 60));
            Console.WriteLine("1. 創建知識庫");
            Console.WriteLine(new string('=', 60));

            var kb_response = maiagent_helper.create_knowledge_base(
                name: "測試知識庫",
                description: "這是一個用於測試的知識庫",
                number_of_retrieved_chunks: 10,
                sentence_window_size: 3,
                enable_hyde: true,
                similarity_cutoff: 0.1,
                enable_rerank: true
            );

            var kb_id = kb_response.get("id");
            Console.WriteLine($"知識庫創建成功！ID: {kb_id}");

            // 2. 創建標籤
            Console.WriteLine("\n" + new string('=', 60));
            Console.WriteLine("2. 創建標籤");
            Console.WriteLine(new string('=', 60));

            var label_response = maiagent_helper.create_knowledge_base_label(
                knowledge_base_id: kb_id,
                name: "技術文檔"
            );

            var label_id = label_response.get("id");
            Console.WriteLine($"標籤創建成功！ID: {label_id}");

            // 3. 上傳檔案 (需要實際檔案路徑)
            Console.WriteLine("\n" + new string('=', 60));
            Console.WriteLine("3. 上傳檔案");
            Console.WriteLine(new string('=', 60));

            // 注意：這裡需要實際的檔案路徑
            // var file_path = "path/to/your/file.pdf";
            // var file_response = maiagent_helper.upload_knowledge_file(kb_id, file_path);
            // Console.WriteLine($"檔案上傳成功！");
            Console.WriteLine("跳過檔案上傳 - 需要實際檔案路徑");

            // 4. 創建 FAQ
            Console.WriteLine("\n" + new string('=', 60));
            Console.WriteLine("4. 創建 FAQ");
            Console.WriteLine(new string('=', 60));

            var faq_response = maiagent_helper.create_knowledge_base_faq(
                knowledge_base_id: kb_id,
                question: "這個知識庫的用途是什麼？",
                answer: "這個知識庫用於存儲和管理技術文檔，幫助用戶快速找到所需信息。",
                labels: new List<Dictionary<string, object>> {
                    new Dictionary<string, object> {{"id", label_id}, {"name", "技術文檔"}}
                }
            );

            var faq_id = faq_response.get("id");
            Console.WriteLine($"FAQ 創建成功！ID: {faq_id}");

            // 5. 搜尋知識庫
            Console.WriteLine("\n" + new string('=', 60));
            Console.WriteLine("5. 搜尋知識庫");
            Console.WriteLine(new string('=', 60));

            var search_results = maiagent_helper.search_knowledge_base(
                knowledge_base_id: kb_id,
                query: "技術文檔"
            );

            var result_count = search_results is List<object> ? ((List<object>)search_results).Count : 0;
            Console.WriteLine($"搜尋結果數量: {result_count}");

            // 6. 查看知識庫詳情
            Console.WriteLine("\n" + new string('=', 60));
            Console.WriteLine("6. 查看知識庫詳情");
            Console.WriteLine(new string('=', 60));

            var kb_detail = maiagent_helper.get_knowledge_base(kb_id);
            Console.WriteLine($"知識庫名稱: {kb_detail.get("name")}");
            Console.WriteLine($"知識庫描述: {kb_detail.get("description")}");
            Console.WriteLine($"檔案數量: {kb_detail.get("files_count", 0)}");
            Console.WriteLine($"創建時間: {kb_detail.get("created_at")}");

            // 7. 列出所有相關資源
            Console.WriteLine("\n" + new string('=', 60));
            Console.WriteLine("7. 列出所有相關資源");
            Console.WriteLine(new string('=', 60));

            // 列出標籤
            var labels = maiagent_helper.list_knowledge_base_labels(kb_id);
            Console.WriteLine($"標籤數量: {labels.get("results", new List<object>()).Count}");

            // 列出 FAQ
            var faqs = maiagent_helper.list_knowledge_base_faqs(kb_id);
            Console.WriteLine($"FAQ 數量: {faqs.get("results", new List<object>()).Count}");

            // 列出檔案
            var files = maiagent_helper.list_knowledge_base_files(kb_id);
            Console.WriteLine($"檔案數量: {files.get("results", new List<object>()).Count}");

            // 8. 清理資源 (可選)
            Console.WriteLine("\n" + new string('=', 60));
            Console.WriteLine("8. 清理資源");
            Console.WriteLine(new string('=', 60));

            // 取消註解以執行清理
            // Console.WriteLine("刪除 FAQ...");
            // maiagent_helper.delete_knowledge_base_faq(kb_id, faq_id);
            //
            // Console.WriteLine("刪除標籤...");
            // maiagent_helper.delete_knowledge_base_label(kb_id, label_id);
            //
            // Console.WriteLine("刪除知識庫...");
            // maiagent_helper.delete_knowledge_base(kb_id);
            //
            // Console.WriteLine("清理完成！");

            Console.WriteLine("跳過清理 - 取消註解以執行實際刪除");

            Console.WriteLine("\n" + new string('=', 60));
            Console.WriteLine("範例執行完成！");
            Console.WriteLine(new string('=', 60));

        } catch (Exception e) {
            Console.WriteLine($"操作失敗：{e}");
        }
    }
}
