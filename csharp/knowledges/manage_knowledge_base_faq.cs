
using System;
using System.Collections.Generic;
using System.Diagnostics;
using Utils;

public static class manage_knowledge_base_faq {

    public static string API_KEY = "<your-api-key>";
    public static string KNOWLEDGE_BASE_ID = "<your-knowledge-base-id>";   // 你的知識庫 ID

    public static void main() {
        // 知識庫 FAQ 管理範例
        //
        // 展示如何使用新的知識庫 API 管理 FAQ

        Debug.Assert(API_KEY != "<your-api-key>", "Please set your API key");
        Debug.Assert(KNOWLEDGE_BASE_ID != "<your-knowledge-base-id>", "Please set your knowledge base id");

        var maiagent_helper = new MaiAgentHelper(API_KEY);

        try {
            // 1. 創建 FAQ
            Console.WriteLine("1. 創建 FAQ...");
            var new_faq = maiagent_helper.create_knowledge_base_faq(
                knowledge_base_id: KNOWLEDGE_BASE_ID,
                question: "什麼是 MaiAgent？",
                answer: "MaiAgent 是一個強大的 AI 助手平台，幫助您建立智能聊天機器人。",
                labels: new List<Dictionary<string, object>> {
                    new Dictionary<string, object> {{"id", "label-id"}, {"name", "general"}}
                }  // 可選標籤
            );
            var faq_id = new_faq.get("id");
            Console.WriteLine($"FAQ 創建成功，ID: {faq_id}");

            // 2. 列出所有 FAQ
            Console.WriteLine("\n2. 列出所有 FAQ...");
            var faqs = maiagent_helper.list_knowledge_base_faqs(KNOWLEDGE_BASE_ID);

            if (faqs.ContainsKey("results")) {
                var faq_list = (List<object>)faqs["results"];
                Console.WriteLine($"找到 {faq_list.Count} 個 FAQ：");
                foreach (var faq in faq_list) {
                    Console.WriteLine($"  ID: {faq.get("id")}");
                    Console.WriteLine($"  問題: {faq.get("question")}");
                    Console.WriteLine($"  答案: {faq.get("answer")}");
                    Console.WriteLine($"  標籤: {faq.get("labels", new List<object>())}");
                    Console.WriteLine(new string('-', 30));
                }
            }

            // 3. 更新 FAQ
            if (faq_id != null) {
                Console.WriteLine($"\n3. 更新 FAQ (ID: {faq_id})...");
                var updated_faq = maiagent_helper.update_knowledge_base_faq(
                    knowledge_base_id: KNOWLEDGE_BASE_ID,
                    faq_id: faq_id,
                    question: "什麼是 MaiAgent AI 助手？",
                    answer: "MaiAgent 是一個進階的 AI 助手平台，專為企業和個人提供智能聊天機器人解決方案。"
                );
                Console.WriteLine("FAQ 更新成功");
            }

            // 4. 獲取特定 FAQ
            if (faq_id != null) {
                Console.WriteLine($"\n4. 獲取 FAQ 詳情 (ID: {faq_id})...");
                var faq_detail = maiagent_helper.get_knowledge_base_faq(KNOWLEDGE_BASE_ID, faq_id);
                Console.WriteLine($"問題: {faq_detail.get("question")}");
                Console.WriteLine($"答案: {faq_detail.get("answer")}");
            }

            // 5. 刪除 FAQ (可選，取消註解以執行)
            // if (faq_id != null) {
            //     Console.WriteLine($"\n5. 刪除 FAQ (ID: {faq_id})...");
            //     maiagent_helper.delete_knowledge_base_faq(KNOWLEDGE_BASE_ID, faq_id);
            //     Console.WriteLine("FAQ 刪除成功");
            // }

        } catch (Exception e) {
            Console.WriteLine($"FAQ 管理失敗：{e}");
        }
    }
}
