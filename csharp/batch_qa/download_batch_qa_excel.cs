
using os;

using Utils;

using System.Diagnostics;

public static class download_batch_qa_excel {
    
    public static string API_KEY = "<your-api-key>";
    
    public static string WEB_CHAT_ID = "<your-web-chat-id>";
    
    public static string BATCH_QA_FILE_ID = "<your-batch-qa-file-id>";
    
    public static void main() {
        var maiagent_helper = MaiAgentHelper(API_KEY);
        var downloaded_file = maiagent_helper.download_batch_qa_excel(WEB_CHAT_ID, BATCH_QA_FILE_ID);
        if (downloaded_file) {
            Console.WriteLine($"File saved as: {os.path.abspath(downloaded_file)}");
        }
    }
    
    static download_batch_qa_excel() {
        main();
    }
    
    static download_batch_qa_excel() {
        Debug.Assert(API_KEY != "<your-api-key>");
        Debug.Assert("Please set your API key");
        Debug.Assert(WEB_CHAT_ID != "<your-web-chat-id>");
        Debug.Assert("Please set your web-chat id");
        Debug.Assert(BATCH_QA_FILE_ID != "<your-batch-qa-file-id>");
        Debug.Assert("Please set your batch qa file id");
        if (@__name__ == "__main__") {
        }
    }
}
