
using os;

using MaiAgentHelper = utils.MaiAgentHelper;

using System.Diagnostics;

public static class upload_batch_qa_file {
    
    public static string API_KEY = "<your-api-key>";
    
    public static string WEB_CHAT_ID = "<your-web-chat-id>";
    
    public static string FILE_PATH = "<your-file-path>";
    
    public static void main() {
        var maiagent_helper = MaiAgentHelper(API_KEY);
        var original_filename = os.path.basename(FILE_PATH);
        var upload_info = maiagent_helper.get_upload_url(file_path: FILE_PATH, model_name: "batch-qa", field_name: "file");
        var file_key = maiagent_helper.upload_file_to_s3(FILE_PATH, upload_info);
        var batch_qa_response = maiagent_helper.upload_batch_qa_file(web_chat_id: WEB_CHAT_ID, file_key: file_key, original_filename: original_filename);
        if (batch_qa_response && batch_qa_response.Contains("id")) {
            Console.WriteLine($"Batch QA File ID: {batch_qa_response[\"id\"]}");
        }
    }
    
    static upload_batch_qa_file() {
        main();
    }
    
    static upload_batch_qa_file() {
        Debug.Assert(API_KEY != "<your-api-key>");
        Debug.Assert("Please set your API key");
        Debug.Assert(WEB_CHAT_ID != "<your-web-chat-id>");
        Debug.Assert("Please set your web-chat id");
        Debug.Assert(FILE_PATH != "<your-file-path>");
        Debug.Assert("Please set your file path");
        if (@__name__ == "__main__") {
        }
    }
}
