using System;
using System.Diagnostics;
using System.Threading.Tasks;
using Utils;

namespace MaiAgentExamples.Knowledges
{
    public static class DeleteKnowledgeFile
    {
        public static string API_KEY = "<your-api-key>";
        public static string KNOWLEDGE_BASE_ID = "<your-knowledge-base-id>";  // 你的知識庫 ID
        public static string FILE_ID = "<your-file-id>"; // 你先前上傳的檔案 ID

        public static async Task Main(string[] args)
        {
            // 刪除知識庫檔案範例
            //
            // 使用新的知識庫 API 刪除檔案

            Debug.Assert(API_KEY != "<your-api-key>", "Please set your API key");
            Debug.Assert(KNOWLEDGE_BASE_ID != "<your-knowledge-base-id>", "Please set your knowledge base id");
            Debug.Assert(FILE_ID != "<your-file-id>", "Please set your file id");

            var maiagentHelper = new MaiAgentHelper(API_KEY);

            try
            {
                await maiagentHelper.delete_knowledge_file(KNOWLEDGE_BASE_ID, FILE_ID);
                Console.WriteLine($"檔案刪除成功,檔案 ID: {FILE_ID}");
            }
            catch (Exception e)
            {
                Console.WriteLine($"檔案刪除失敗：{e}");
            }
        }
    }
}
