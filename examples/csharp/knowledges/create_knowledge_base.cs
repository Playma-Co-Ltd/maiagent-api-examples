
using System;
using System.Diagnostics;
using Utils;

public static class create_knowledge_base {

    public static string API_KEY = "<your-api-key>";

    // 知識庫基本資訊
    public static string KNOWLEDGE_BASE_NAME = "My Knowledge Base";
    public static string KNOWLEDGE_BASE_DESCRIPTION = "This is a sample knowledge base for testing purposes.";

    // 可選設定
    public static object EMBEDDING_MODEL = null;  // 可設定為特定的嵌入模型 ID
    public static object RERANKER_MODEL = null;  // 可設定為特定的重新排序模型 ID
    public static object CHATBOTS = null;  // 可設定為聊天機器人 ID 列表，例如 [{'id': 'chatbot-id', 'name': 'chatbot-name'}]

    public static void main() {
        // 創建知識庫範例
        //
        // 展示如何使用新的知識庫 API 創建知識庫

        Debug.Assert(API_KEY != "<your-api-key>", "Please set your API key");

        var maiagent_helper = new MaiAgentHelper(API_KEY);

        try {
            // 創建知識庫
            var response = maiagent_helper.create_knowledge_base(
                name: KNOWLEDGE_BASE_NAME,
                description: KNOWLEDGE_BASE_DESCRIPTION,
                embedding_model: EMBEDDING_MODEL,
                reranker_model: RERANKER_MODEL,
                number_of_retrieved_chunks: 12,  // 預設值
                sentence_window_size: 2,  // 預設值
                enable_hyde: false,  // 預設值
                similarity_cutoff: 0.0,  // 預設值
                enable_rerank: true,  // 預設值
                chatbots: CHATBOTS
            );

            Console.WriteLine($"知識庫創建成功！");
            Console.WriteLine($"知識庫 ID: {response.get("id")}");
            Console.WriteLine($"知識庫名稱: {response.get("name")}");
            Console.WriteLine($"知識庫描述: {response.get("description")}");
            Console.WriteLine($"創建時間: {response.get("created_at")}");

        } catch (Exception e) {
            Console.WriteLine($"知識庫創建失敗：{e}");
        }
    }
}
