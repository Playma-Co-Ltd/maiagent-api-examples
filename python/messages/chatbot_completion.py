from utils import MaiAgentHelper
from utils.config import API_KEY, BASE_URL, CHATBOT_ID, STORAGE_URL
import sys
import os

# 測試配置
TEST_IMAGE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
    'images', 
    '測試pdf用8頁.pdf'
)
TEST_PROMPTS = {
    'streaming': "使用串流模式測試：請給我一個笑話",
    'non_streaming': "不使用串流模式測試：請給我一個笑話",
    'conversation_first': "你好，請記住我說我叫小明",
    'conversation_second': "我剛才說我叫什麼名字？",
    'image_analysis': "這啥"
}

# 輸出格式
SEPARATOR_LINE = "=" * 50

def get_maiagent_helper() -> MaiAgentHelper:
    """獲取 MaiAgent 幫助器實例"""
    return MaiAgentHelper(
        api_key=API_KEY,
        base_url=BASE_URL,
        storage_url=STORAGE_URL
    )

def print_separator(title: str):
    """打印分隔線和標題"""
    print(f"\n{SEPARATOR_LINE}")
    print(f"測試場景: {title}")
    print(f"{SEPARATOR_LINE}\n")

def create_attachment(maiagent_helper: MaiAgentHelper, image_path: str) -> list[dict]:
    """創建附件數據"""
    if not image_path:
        return []
    
    print(f"正在上傳圖片: {image_path}")
    upload_response = maiagent_helper.upload_attachment_without_conversation(image_path)
    print(f"上傳響應: {upload_response}")
    
    if not upload_response:
        return None
    
    attachments = [{
        'id': upload_response['id'],
        'type': 'other',
        'filename': upload_response['filename'],
        'file': upload_response['file'],
    }]
    print(f"附件數據準備完成: {attachments}")
    return attachments

def handle_streaming_response(data: dict[str, any]):
    """處理串流響應"""
    if 'content' in data and data.get('done') is False:
        sys.stdout.write(data['content'])
        sys.stdout.flush()

def test_with_streaming():
    """
    測試場景1: 使用串流模式與聊天機器人對話
    
    流程:
    1. 調用 create_chatbot_completion API，設置 isStreaming=True
    2. 逐步接收並顯示串流響應
    
    API 調用:
    POST /chatbots/{chatbot_id}/completions/
    
    Request Payload:
    {
        "conversation": null,
        "message": {
            "content": "使用串流模式測試：請給我一個笑話",
            "attachments": []
        },
        "isStreaming": true
    }
    """
    print_separator("使用串流模式")
    maiagent_helper = get_maiagent_helper()
    
    try:
        for data in maiagent_helper.create_chatbot_completion(
            CHATBOT_ID,
            TEST_PROMPTS['streaming'],
            is_streaming=True
        ):
            handle_streaming_response(data)
        print()  # 換行
    except Exception as e:
        print(f"錯誤: {str(e)}")

def test_without_streaming():
    """
    測試場景2: 使用非串流模式與聊天機器人對話
    
    流程:
    1. 調用 create_chatbot_completion API，設置 isStreaming=False
    2. 一次性接收完整響應
    
    API 調用:
    POST /chatbots/{chatbot_id}/completions/
    
    Request Payload:
    {
        "conversation": null,
        "message": {
            "content": "不使用串流模式測試：請給我一個笑話",
            "attachments": []
        },
        "isStreaming": false # 可以省略，因為預設為 false
    }
    """
    print_separator("不使用串流模式")
    maiagent_helper = get_maiagent_helper()
    
    try:
        response = maiagent_helper.create_chatbot_completion(
            CHATBOT_ID,
            TEST_PROMPTS['non_streaming'],
            is_streaming=False
        )
        print(f"回應: {response}")
    except Exception as e:
        print(f"錯誤: {str(e)}")

def test_conversation_flow():
    """
    測試場景3: 測試對話上下文功能
    
    流程:
    1. 第一次調用 API 不帶 conversationId
    2. 從響應中獲取 conversationId
    3. 第二次調用帶上 conversationId 進行對話
    
    API 調用:
    1. 第一次對話:
    POST /chatbots/{chatbot_id}/completions/
    
    Request Payload:
    {
        "conversation": null,
        "message": {
            "content": "你好，請記住我說我叫小明",
            "attachments": []
        },
        "isStreaming": false
    }
    
    2. 第二次對話:
    POST /chatbots/{chatbot_id}/completions/
    
    Request Payload:
    {
        "conversation": "<第一次對話獲取的conversationId>",
        "message": {
            "content": "我剛才說我叫什麼名字？",
            "attachments": []
        },
        "isStreaming": true
    }
    """
    print_separator("對話流程測試")
    maiagent_helper = get_maiagent_helper()
    
    try:
        # 第一次對話，不帶 conversationId
        print("第一次對話（無 conversationId）:")
        first_response = maiagent_helper.create_chatbot_completion(
            CHATBOT_ID,
            TEST_PROMPTS['conversation_first'],
            is_streaming=False
        )
        
        if not isinstance(first_response, dict):
            print(f"錯誤：收到非預期的回應類型: {type(first_response)}")
            return
            
        print(f"第一次響應: {first_response}")
        
        # 從響應中獲取 conversationId
        conversation_id = first_response.get('conversationId')
        if not conversation_id:
            print("錯誤：回應中沒有 conversationId")
            return
            
        print(f"\n獲取到的 conversationId: {conversation_id}\n")
        
        # 第二次對話，使用獲取到的 conversationId
        print("第二次對話（帶 conversationId）:")
        for data in maiagent_helper.create_chatbot_completion(
            CHATBOT_ID,
            TEST_PROMPTS['conversation_second'],
            conversation_id=conversation_id,
            is_streaming=True
        ):
            handle_streaming_response(data)
        print()  # 換行
    except Exception as e:
        print(f"錯誤: {str(e)}")

def test_conversation_with_attachment():
    """
    測試場景4: 測試帶附件的對話功能
    
    流程:
    1. 請求預簽名上傳 URL
    2. 上傳圖片
    3. 註冊附件
    4. 進行帶附件的對話
    
    API 調用:
    1. 請求預簽名上傳 URL:
    POST /upload-presigned-url/
    Request Payload:
    {
        "filename": "Cat03.jpg",
        "modelName": "attachment",
        "fieldName": "file",
        "fileSize": 123456
    }

    2. 上傳圖片:
    POST https://s3.ap-northeast-1.amazonaws.com/whizchat-media-prod-django.playma.app

    Request Payload:
    {
        "key": "<file_key>",
        "x-amz-algorithm": "AWS4-HMAC-SHA256",
        "x-amz-credential": "<aws_credential>",
        "x-amz-date": "<timestamp>",
        "policy": "<base64_encoded_policy>",
        "x-amz-signature": "<signature>",
        "file": "<file_content>"
    }
    
    3. 註冊附件:
    POST /attachments/

    Request Payload:
    {
        "file": "<file_key>",
        "filename": "Cat03.jpg",
        "type": "image"
    }
    
    2. 圖片分析:
    POST /chatbots/{chatbot_id}/completions/
    
    Request Payload:
    {
        "conversation": null,
        "message": {
            "content": "請描述這張圖片的內容",
            "attachments": [{
                "id": "<attachment_id>",
                "type": "image",
                "filename": "<filename>",
                "file": "<file_url>"
            }]
        },
        "isStreaming": true
    }
    """
    print_separator("帶附件的對話測試")
    maiagent_helper = get_maiagent_helper()
    
    try:
        # 準備附件
        attachments = create_attachment(maiagent_helper, TEST_IMAGE_PATH)
        if not attachments:
            print("附件準備失敗")
            return
            
        print("\n開始分析圖片...")
        for data in maiagent_helper.create_chatbot_completion(
            CHATBOT_ID,
            TEST_PROMPTS['image_analysis'],
            attachments=attachments,
            is_streaming=True
        ):
            handle_streaming_response(data)
        print()  # 換行
    except Exception as e:
        print(f"錯誤: {str(e)}")

def main():
    """主函數：運行所有測試場景"""
    # test_with_streaming()
    # test_without_streaming()
    # test_conversation_flow()
    test_conversation_with_attachment()

if __name__ == '__main__':
    main()
