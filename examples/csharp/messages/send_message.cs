using System;
using System.Diagnostics;
using System.Text.Json;
using Utils;

namespace MaiAgentExamples.Messages
{
    public static class SendMessage
    {
        public static string API_KEY = "<your-api-key>";
        public static string WEB_CHAT_ID = "<your-webchat-id>";
        public static string TEXT_MESSAGE = "<your-text-message>";

        public static async Task Main(string[] args)
        {
            Debug.Assert(API_KEY != "<your-api-key>", "Please set your API key");
            Debug.Assert(WEB_CHAT_ID != "<your-webchat-id>", "Please set your webchat id");
            Debug.Assert(TEXT_MESSAGE != "<your-text-message>", "Please set your text message");

            var maiagentHelper = new MaiAgentHelper(API_KEY);

            // 建立對話
            var createConversationResponse = await maiagentHelper.CreateConversationAsync(WEB_CHAT_ID);
            var conversationId = createConversationResponse.GetProperty("id").GetString();

            // 發送訊息
            var response = await maiagentHelper.SendMessageAsync(conversationId!, TEXT_MESSAGE);

            // 此處是直接回傳訊息建立的 response，訊息處理完成後，會以 webhook 通知
            Console.WriteLine(JsonSerializer.Serialize(response, new JsonSerializerOptions { WriteIndented = true }));

            // Webhook 網址請於 MaiAgent 後台「AI 助理」設定
            // 訊息回傳格式如下
            // - 訊息內容位於 content 欄位
            // - 引用資料位於 citations 欄位
            /*
            {
                "id": "d26451d6-e2a2-462d-af49-42058e936cb5",
                "conversation": "<conversation-id>",
                "sender": {
                    "id": "<sender-id>",
                    "name": "<user-id>",
                    "avatar": "<avatar-url>",
                },
                "type": "outgoing",
                "content": "<response-message>",
                "feedback": null,
                "createdAt": "1728181396000",
                "attachments": [],
                "citations": [
                    {
                        "id": "<file-id>",
                        "filename": "<filename>",
                        "file": "<file-url>",
                        "fileType": "jsonl",
                        "size": 174632,
                        "status": "done",
                        "document": "<document-id>",
                        "createdAt": "1728104372000"
                    },
                    ...
                ]
            }
            */
        }
    }
}
