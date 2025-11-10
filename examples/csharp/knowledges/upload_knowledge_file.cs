
using System;
using System.Diagnostics;
using Utils;

public static class upload_knowledge_file {

    public static string API_KEY = "<your-api-key>";

    public static string KNOWLEDGE_BASE_ID = "<your-knowledge-base-id>";   // 你的知識庫 ID
    public static string FILE_PATH = "../../../inputs/台灣高鐵FAQ.xlsx";  // 使用存在的檔案

    public static void main() {
        // 上傳檔案到知識庫範例
        //
        // 使用新的知識庫 API 上傳檔案

        Debug.Assert(API_KEY != "<your-api-key>", "Please set your API key");
        Debug.Assert(KNOWLEDGE_BASE_ID != "<your-knowledge-base-id>", "Please set your knowledge base id");
        // Debug.Assert(FILE_PATH != "<your-file-path>", "Please set your file path");

        var maiagent_helper = new MaiAgentHelper(API_KEY);

        try {
            var response = maiagent_helper.upload_knowledge_file(KNOWLEDGE_BASE_ID, FILE_PATH);
            Console.WriteLine($"檔案上傳成功：{response}");
        } catch (Exception e) {
            Console.WriteLine($"檔案上傳失敗：{e}");
        }
    }
}
