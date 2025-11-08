
using System;
using System.Diagnostics;
using Utils;

public static class delete_knowledge_file {

    public static string API_KEY = "<your-api-key>";

    public static string KNOWLEDGE_BASE_ID = "<your-knowledge-base-id>";  // 你的知識庫 ID
    public static string FILE_ID = "<your-file-id>"; // 你先前上傳的檔案 ID

    public static void main() {
        // 刪除知識庫檔案範例
        //
        // 使用新的知識庫 API 刪除檔案

        Debug.Assert(API_KEY != "<your-api-key>", "Please set your API key");
        Debug.Assert(KNOWLEDGE_BASE_ID != "<your-knowledge-base-id>", "Please set your knowledge base id");
        Debug.Assert(FILE_ID != "<your-file-id>", "Please set your file id");

        var maiagent_helper = new MaiAgentHelper(API_KEY);

        try {
            var result = maiagent_helper.delete_knowledge_file(KNOWLEDGE_BASE_ID, FILE_ID);
            // 只有當沒有拋出異常時才顯示成功訊息
            if (result) {  // delete_knowledge_file 成功時返回 True
                Console.WriteLine($"檔案刪除成功,檔案 ID: {FILE_ID}");
            }
        } catch (Exception e) {
            Console.WriteLine($"檔案刪除失敗：{e}");
        }
    }
}
