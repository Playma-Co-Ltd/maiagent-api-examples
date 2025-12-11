using System;
using System.IO;
using System.Diagnostics;
using Utils;

namespace MaiAgentExamples.BatchQA
{
    public static class UploadBatchQAFile
    {
        public static string API_KEY = "<your-api-key>";
        public static string WEB_CHAT_ID = "<your-web-chat-id>";
        public static string FILE_PATH = "<your-file-path>";

        public static async Task Main(string[] args)
        {
            Debug.Assert(API_KEY != "<your-api-key>", "Please set your API key");
            Debug.Assert(WEB_CHAT_ID != "<your-web-chat-id>", "Please set your web-chat id");
            Debug.Assert(FILE_PATH != "<your-file-path>", "Please set your file path");

            var maiagentHelper = new MaiAgentHelper(API_KEY);
            var originalFilename = Path.GetFileName(FILE_PATH);

            var uploadInfo = await maiagentHelper.GetUploadUrlAsync(FILE_PATH, "batch-qa", "file");
            if (!uploadInfo.HasValue)
            {
                Console.WriteLine("Failed to get upload URL");
                return;
            }

            var fileKey = await maiagentHelper.UploadFileToS3Async(FILE_PATH, uploadInfo.Value);
            var batchQaResponse = await maiagentHelper.UploadBatchQAFileAsync(WEB_CHAT_ID, fileKey, originalFilename);

            if (batchQaResponse.ValueKind == System.Text.Json.JsonValueKind.Object &&
                batchQaResponse.TryGetProperty("id", out var idProperty))
            {
                Console.WriteLine($"Batch QA File ID: {idProperty.GetString()}");
            }
        }
    }
}
