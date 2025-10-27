
using MaiAgentHelper = utils.MaiAgentHelper;

using API_KEY = utils.config.API_KEY;

using BASE_URL = utils.config.BASE_URL;

using CHATBOT_ID = utils.config.CHATBOT_ID;

using STORAGE_URL = utils.config.STORAGE_URL;

using sys;

using os;

using System.Collections.Generic;

public static class chatbot_completion {
    
    public static string TEST_IMAGE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(@__file__))), "inputs", "cat.jpg");
    
    public static string TEST_PDF_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(@__file__))), "inputs", "sample.pdf");
    
    public static Dictionary<string, string> TEST_PROMPTS = new Dictionary<object, object> {
        {
            "streaming",
            "使用串流模式測試：請給我一個笑話"},
        {
            "non_streaming",
            "不使用串流模式測試：請給我一個笑話"},
        {
            "conversation_first",
            "你好，請記住我說我叫小明"},
        {
            "conversation_second",
            "我剛才說我叫什麼名字？"},
        {
            "image_analysis",
            "請描述這張圖片的內容"},
        {
            "pdf_analysis",
            "請分析這個PDF文件的內容並總結主要信息"}};
    
    public static object SEPARATOR_LINE = "=" * 50;
    
    // 獲取 MaiAgent 幫助器實例
    public static object get_maiagent_helper() {
        return MaiAgentHelper(api_key: API_KEY, base_url: BASE_URL, storage_url: STORAGE_URL);
    }
    
    // 打印分隔線和標題
    public static void print_separator(string title) {
        Console.WriteLine($"\n{SEPARATOR_LINE}");
        Console.WriteLine($"測試場景: {title}");
        Console.WriteLine($"{SEPARATOR_LINE}\n");
    }
    
    // 創建附件數據
    public static object create_attachment(object maiagent_helper, string image_path) {
        if (!image_path) {
            return new List<object>();
        }
        Console.WriteLine($"正在上傳圖片: {image_path}");
        var upload_response = maiagent_helper.upload_attachment_without_conversation(file_path: image_path, type: "image");
        Console.WriteLine($"上傳響應: {upload_response}");
        if (!upload_response) {
            return null;
        }
        var attachments = new List<Dictionary<string, string>> {
            new Dictionary<object, object> {
                {
                    "id",
                    upload_response["id"]},
                {
                    "type",
                    "image"},
                {
                    "filename",
                    upload_response["filename"]},
                {
                    "file",
                    upload_response["file"]}}
        };
        Console.WriteLine($"附件數據準備完成: {attachments}");
        return attachments;
    }
    
    // 處理串流響應
    public static void handle_streaming_response(object data) {
        if (data.Contains("content") && object.ReferenceEquals(data.get("done"), false)) {
            sys.stdout.write(data["content"]);
            sys.stdout.flush();
        }
    }
    
    // 
    //     測試場景1: 使用串流模式與聊天機器人對話
    //     
    //     流程:
    //     1. 調用 create_chatbot_completion API，設置 isStreaming=True
    //     2. 逐步接收並顯示串流響應
    //     
    //     API 調用:
    //     POST /chatbots/{chatbot_id}/completions/
    //     
    //     Request Payload:
    //     {
    //         "conversation": null,
    //         "message": {
    //             "content": "使用串流模式測試：請給我一個笑話",
    //             "attachments": []
    //         },
    //         "isStreaming": true
    //     }
    //     
    public static object test_with_streaming() {
        print_separator("使用串流模式");
        var maiagent_helper = get_maiagent_helper();
        try {
            foreach (var data in maiagent_helper.create_chatbot_completion(CHATBOT_ID, TEST_PROMPTS["streaming"], is_streaming: true)) {
                handle_streaming_response(data);
            }
            Console.WriteLine();
        } catch (Exception) {
            Console.WriteLine($"錯誤: {str(e)}");
        }
    }
    
    // 
    //     測試場景2: 使用非串流模式與聊天機器人對話
    //     
    //     流程:
    //     1. 調用 create_chatbot_completion API，設置 isStreaming=False
    //     2. 一次性接收完整響應
    //     
    //     API 調用:
    //     POST /chatbots/{chatbot_id}/completions/
    //     
    //     Request Payload:
    //     {
    //         "conversation": null,
    //         "message": {
    //             "content": "不使用串流模式測試：請給我一個笑話",
    //             "attachments": []
    //         },
    //         "isStreaming": false # 可以省略，因為預設為 false
    //     }
    //     
    public static object test_without_streaming() {
        print_separator("不使用串流模式");
        var maiagent_helper = get_maiagent_helper();
        try {
            var response = maiagent_helper.create_chatbot_completion(CHATBOT_ID, TEST_PROMPTS["non_streaming"], is_streaming: false);
            Console.WriteLine($"回應: {response}");
        } catch (Exception) {
            Console.WriteLine($"錯誤: {str(e)}");
        }
    }
    
    // 
    //     測試場景3: 測試對話上下文功能
    //     
    //     流程:
    //     1. 第一次調用 API 不帶 conversationId
    //     2. 從響應中獲取 conversationId
    //     3. 第二次調用帶上 conversationId 進行對話
    //     
    //     API 調用:
    //     1. 第一次對話:
    //     POST /chatbots/{chatbot_id}/completions/
    //     
    //     Request Payload:
    //     {
    //         "conversation": null,
    //         "message": {
    //             "content": "你好，請記住我說我叫小明",
    //             "attachments": []
    //         },
    //         "isStreaming": false
    //     }
    //     
    //     2. 第二次對話:
    //     POST /chatbots/{chatbot_id}/completions/
    //     
    //     Request Payload:
    //     {
    //         "conversation": "<第一次對話獲取的conversationId>",
    //         "message": {
    //             "content": "我剛才說我叫什麼名字？",
    //             "attachments": []
    //         },
    //         "isStreaming": true
    //     }
    //     
    public static object test_conversation_flow() {
        print_separator("對話流程測試");
        var maiagent_helper = get_maiagent_helper();
        try {
            // 第一次對話，不帶 conversationId
            Console.WriteLine("第一次對話（無 conversationId）:");
            var first_response = maiagent_helper.create_chatbot_completion(CHATBOT_ID, TEST_PROMPTS["conversation_first"], is_streaming: false);
            if (!(first_response is dict)) {
                Console.WriteLine($"錯誤：收到非預期的回應類型: {type(first_response)}");
                return;
            }
            Console.WriteLine($"第一次響應: {first_response}");
            // 從響應中獲取 conversationId
            var conversation_id = first_response.get("conversationId");
            if (!conversation_id) {
                Console.WriteLine("錯誤：回應中沒有 conversationId");
                return;
            }
            Console.WriteLine($"\n獲取到的 conversationId: {conversation_id}\n");
            // 第二次對話，使用獲取到的 conversationId
            Console.WriteLine("第二次對話（帶 conversationId）:");
            foreach (var data in maiagent_helper.create_chatbot_completion(CHATBOT_ID, TEST_PROMPTS["conversation_second"], conversation_id: conversation_id, is_streaming: true)) {
                handle_streaming_response(data);
            }
            Console.WriteLine();
        } catch (Exception) {
            Console.WriteLine($"錯誤: {str(e)}");
        }
    }
    
    // 
    //     測試場景4: 測試帶附件的對話功能
    //     
    //     流程:
    //     1. 請求預簽名上傳 URL
    //     2. 上傳圖片
    //     3. 註冊附件
    //     4. 進行帶附件的對話
    //     
    //     API 調用:
    //     1. 請求預簽名上傳 URL:
    //     POST /upload-presigned-url/
    //     Request Payload:
    //     {
    //         "filename": "Cat03.jpg",
    //         "modelName": "attachment",
    //         "fieldName": "file",
    //         "fileSize": 123456
    //     }
    // 
    //     2. 上傳圖片:
    //     POST https://s3.ap-northeast-1.amazonaws.com/whizchat-media-prod-django.playma.app
    // 
    //     Request Payload:
    //     {
    //         "key": "<file_key>",
    //         "x-amz-algorithm": "AWS4-HMAC-SHA256",
    //         "x-amz-credential": "<aws_credential>",
    //         "x-amz-date": "<timestamp>",
    //         "policy": "<base64_encoded_policy>",
    //         "x-amz-signature": "<signature>",
    //         "file": "<file_content>"
    //     }
    //     
    //     3. 註冊附件:
    //     POST /attachments/
    // 
    //     Request Payload:
    //     {
    //         "file": "<file_key>",
    //         "filename": "Cat03.jpg",
    //         "type": "image"
    //     }
    //     
    //     2. 圖片分析:
    //     POST /chatbots/{chatbot_id}/completions/
    //     
    //     Request Payload:
    //     {
    //         "conversation": null,
    //         "message": {
    //             "content": "請描述這張圖片的內容",
    //             "attachments": [{
    //                 "id": "<attachment_id>",
    //                 "type": "image",
    //                 "filename": "<filename>",
    //                 "file": "<file_url>"
    //             }]
    //         },
    //         "isStreaming": true
    //     }
    //     
    public static object test_conversation_with_image_attachment() {
        print_separator("帶附件的對話測試");
        var maiagent_helper = get_maiagent_helper();
        try {
            // 準備附件
            var attachments = create_attachment(maiagent_helper, TEST_IMAGE_PATH);
            if (!attachments) {
                Console.WriteLine("附件準備失敗");
                return;
            }
            Console.WriteLine("\n開始分析圖片...");
            foreach (var data in maiagent_helper.create_chatbot_completion(CHATBOT_ID, TEST_PROMPTS["image_analysis"], attachments: attachments, is_streaming: true)) {
                handle_streaming_response(data);
            }
            Console.WriteLine();
        } catch (Exception) {
            Console.WriteLine($"錯誤: {str(e)}");
        }
    }
    
    // 
    //     測試場景5: 測試帶PDF附件的對話功能
    // 
    //     流程:
    //     1. 請求預簽名上傳 URL
    //     2. 上傳PDF文件
    //     3. 註冊附件
    //     4. 進行帶PDF附件的對話
    // 
    //     API 調用:
    //     1. 請求預簽名上傳 URL:
    //     POST /upload-presigned-url/
    //     Request Payload:
    //     {
    //         "filename": "優勢規格.pdf",
    //         "modelName": "attachment",
    //         "fieldName": "file",
    //         "fileSize": 123456
    //     }
    // 
    //     2. 上傳PDF:
    //     POST https://s3.ap-northeast-1.amazonaws.com/whizchat-media-prod-django.playma.app
    // 
    //     Request Payload:
    //     {
    //         "key": "<file_key>",
    //         "x-amz-algorithm": "AWS4-HMAC-SHA256",
    //         "x-amz-credential": "<aws_credential>",
    //         "x-amz-date": "<timestamp>",
    //         "policy": "<base64_encoded_policy>",
    //         "x-amz-signature": "<signature>",
    //         "file": "<file_content>"
    //     }
    // 
    //     3. 註冊附件:
    //     POST /attachments/
    // 
    //     Request Payload:
    //     {
    //         "file": "<file_key>",
    //         "filename": "優勢規格.pdf",
    //         "type": "file"
    //     }
    // 
    //     4. PDF分析:
    //     POST /chatbots/{chatbot_id}/completions/
    // 
    //     Request Payload:
    //     {
    //         "conversation": null,
    //         "message": {
    //             "content": "請分析這個PDF文件的內容並總結主要信息",
    //             "attachments": [{
    //                 "id": "<attachment_id>",
    //                 "type": "file",
    //                 "filename": "<filename>",
    //                 "file": "<file_url>"
    //             }]
    //         },
    //         "isStreaming": true
    //     }
    //     
    public static object test_conversation_with_pdf_attachment() {
        print_separator("帶PDF附件的對話測試");
        var maiagent_helper = get_maiagent_helper();
        try {
            // 準備附件
            Console.WriteLine($"正在上傳PDF文件: {TEST_PDF_PATH}");
            var upload_response = maiagent_helper.upload_attachment_without_conversation(file_path: TEST_PDF_PATH, type: "other");
            Console.WriteLine($"上傳響應: {upload_response}");
            if (!upload_response) {
                Console.WriteLine("PDF附件準備失敗");
                return;
            }
            // 創建PDF附件數據
            var attachments = new List<Dictionary<string, string>> {
                new Dictionary<object, object> {
                    {
                        "id",
                        upload_response["id"]},
                    {
                        "type",
                        "other"},
                    {
                        "filename",
                        upload_response["filename"]},
                    {
                        "file",
                        upload_response["file"]}}
            };
            Console.WriteLine($"PDF附件數據準備完成: {attachments}");
            Console.WriteLine("\n開始分析PDF文件...");
            var response = maiagent_helper.create_chatbot_completion(CHATBOT_ID, TEST_PROMPTS["pdf_analysis"], attachments: attachments, is_streaming: false);
            Console.WriteLine($"回應: {response}");
        } catch (Exception) {
            Console.WriteLine($"錯誤: {str(e)}");
        }
    }
    
    // 主函數：運行所有測試場景
    public static void main() {
        test_with_streaming();
        test_without_streaming();
        test_conversation_flow();
        test_conversation_with_image_attachment();
        test_conversation_with_pdf_attachment();
    }
    
    static chatbot_completion() {
        main();
    }
    
    static chatbot_completion() {
        if (@__name__ == "__main__") {
        }
    }
}
