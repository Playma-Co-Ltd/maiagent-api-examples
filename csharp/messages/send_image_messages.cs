using System;
using System.Threading.Tasks;
using MaiAgent.Utils;

public class SendImageMessage
{
    private const string API_KEY = "<your-api-key>";
    private const string WEB_CHAT_ID = "<your-webchat-id>";
    private const string TEXT_MESSAGE = "<your-text-message>";
    private const string IMAGE_PATH = "<your-image-path>";

    private readonly MaiAgentHelper _maiAgentHelper;

    public SendImageMessage()
    {
        if (API_KEY == "<your-api-key>")
            throw new ArgumentException("Please set your API key");
        if (WEB_CHAT_ID == "<your-webchat-id>")
            throw new ArgumentException("Please set your webchat id");
        if (TEXT_MESSAGE == "<your-text-message>")
            throw new ArgumentException("Please set your text message");
        if (IMAGE_PATH == "<your-image-path>")
            throw new ArgumentException("Please set your image path");

        _maiAgentHelper = new MaiAgentHelper(API_KEY);
    }

    public async Task RunAsync()
    {
        // 建立對話
        var createConversationResponse = await _maiAgentHelper.CreateConversationAsync(WEB_CHAT_ID);
        var conversationId = createConversationResponse.Id;

        // 上傳附件
        var uploadAttachmentResponse = await _maiAgentHelper.UploadAttachmentAsync(conversationId, IMAGE_PATH);

        // 發送訊息
        var response = await _maiAgentHelper.SendMessageAsync(
            conversationId,
            TEXT_MESSAGE,
            new[] 
            {
                new Attachment
                {
                    Id = uploadAttachmentResponse.Id,
                    Type = "image",
                    Filename = uploadAttachmentResponse.Filename,
                    File = uploadAttachmentResponse.File
                }
            });

        // 此處是直接回傳訊息建立的 response，訊息處理完成後，會以 webhook 通知
        Console.WriteLine(response);
    }

    public static async Task Main(string[] args)
    {
        var program = new SendImageMessage();
        await program.RunAsync();
    }
}

/* Webhook 回傳格式範例：
{
    "id": "d26451d6-e2a2-462d-af49-42058e936cb5",
    "conversation": "<conversation-id>",
    "sender": {
        "id": "<sender-id>",
        "name": "<user-id>",
        "avatar": "<avatar-url>"
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
        }
    ]
}
*/
