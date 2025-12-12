using System;
using System.IO;
using System.Diagnostics;
using Utils;

namespace MaiAgentExamples.BatchQA
{
    public static class DownloadBatchQAExcel
    {
        public static string API_KEY = "<your-api-key>";
        public static string WEB_CHAT_ID = "<your-web-chat-id>";
        public static string BATCH_QA_FILE_ID = "<your-batch-qa-file-id>";

        public static async Task Main(string[] args)
        {
            Debug.Assert(API_KEY != "<your-api-key>", "Please set your API key");
            Debug.Assert(WEB_CHAT_ID != "<your-web-chat-id>", "Please set your web-chat id");
            Debug.Assert(BATCH_QA_FILE_ID != "<your-batch-qa-file-id>", "Please set your batch qa file id");

            var maiagentHelper = new MaiAgentHelper(API_KEY);
            var downloadedFile = await maiagentHelper.DownloadBatchQAExcelAsync(WEB_CHAT_ID, BATCH_QA_FILE_ID);

            if (!string.IsNullOrEmpty(downloadedFile))
            {
                Console.WriteLine($"File saved as: {Path.GetFullPath(downloadedFile)}");
            }
        }
    }
}
