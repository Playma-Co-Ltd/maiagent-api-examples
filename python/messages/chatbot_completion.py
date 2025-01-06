from utils import MaiAgentHelper
from utils.config import API_KEY, BASE_URL, CHATBOT_ID
import sys
# API 配置
STORAGE_URL = 'https://s3.ap-northeast-1.amazonaws.com/autox-media-dev.playma.app'

# 測試配置
TEST_IMAGE_PATH = '/Users/haofu/Documents/playma/測試資料/Cat03.jpg'
TEST_PROMPTS = {
    'streaming': "使用串流模式測試：請給我一個笑話",
    'non_streaming': "不使用串流模式測試：請給我一個笑話",
    'conversation_first': "你好，請記住我說我叫小明",
    'conversation_second': "我剛才說我叫什麼名字？",
    'image_analysis': "請描述這張圖片的內容"
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
        return None
    
    print(f"正在上傳圖片: {image_path}")
    upload_response = maiagent_helper.upload_attachment_without_conversation(image_path)
    print(f"上傳響應: {upload_response}")
    
    if not upload_response:
        return None
    
    attachments = [{
        'id': upload_response['id'],
        'type': 'image',
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
    1. 初始化 MaiAgentHelper
    2. 調用 create_chatbot_completion API，設置 is_streaming=True
    3. 逐步接收並顯示串流響應
    
    API 調用:
    - POST /api/v1/chatbots/{chatbot_id}/completions/
      參數:
        - is_streaming: true
        - message.content: 測試提示
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
    1. 初始化 MaiAgentHelper
    2. 調用 create_chatbot_completion API，設置 is_streaming=False
    3. 一次性接收完整響應
    
    API 調用:
    - POST /api/v1/chatbots/{chatbot_id}/completions/?is_streaming=false
      參數:
        - is_streaming: false
        - message.content: 測試提示
    """
    print_separator("不使用串流模式")
    maiagent_helper = get_maiagent_helper()
    
    try:
        response = next(maiagent_helper.create_chatbot_completion(
            CHATBOT_ID,
            TEST_PROMPTS['non_streaming'],
            is_streaming=False
        ))
        print(f"完整響應: {response}")
    except Exception as e:
        print(f"錯誤: {str(e)}")

def test_conversation_flow():
    """
    測試場景3: 測試對話上下文功能
    
    流程:
    1. 初始化 MaiAgentHelper
    2. 第一次調用 API 不帶 conversation_id
    3. 從響應中獲取 conversation_id
    4. 第二次調用帶上 conversation_id 進行對話
    
    API 調用:
    1. 第一次對話:
       - POST /api/v1/chatbots/{chatbot_id}/completions/
         參數:
           - message.content: 第一個測試提示
           - conversation: null
    
    2. 第二次對話:
       - POST /api/v1/chatbots/{chatbot_id}/completions/
         參數:
           - message.content: 第二個測試提示
           - conversation: 第一次對話獲取的 conversation_id
           - is_streaming: true
    """
    print_separator("對話流程測試")
    maiagent_helper = get_maiagent_helper()
    
    try:
        # 第一次對話，不帶conversation_id
        print("第一次對話（無conversation_id）:")
        first_response = next(maiagent_helper.create_chatbot_completion(
            CHATBOT_ID,
            TEST_PROMPTS['conversation_first'],
            is_streaming=False
        ))
        print(f"第一次響應: {first_response}")
        
        # 從響應中獲取conversation_id
        conversation_id = first_response.get('conversation_id')
        print(f"\n獲取到的conversation_id: {conversation_id}\n")
        
        # 第二次對話，使用獲取到的conversation_id
        print("第二次對話（帶conversation_id）:")
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

def test_ocr_like_usage():
    """
    測試場景4: 測試圖片分析功能
    
    流程:
    1. 初始化 MaiAgentHelper
    2. 上傳圖片文件獲取附件信息
    3. 調用 API 進行圖片分析
    
    API 調用:
    1. 上傳圖片:
       - POST /api/v1/upload-presigned-url/
         獲取預簽名上傳 URL
       
       - POST {storage_url}
         上傳文件到 S3
         
       - POST /api/v1/attachments/
         註冊附件信息
    
    2. 圖片分析:
       - POST /api/v1/chatbots/{chatbot_id}/completions/
         參數:
           - message.content: 圖片分析提示
           - message.attachments: 包含圖片信息的附件數組
           - is_streaming: true
    """
    print_separator("OCR式使用測試")
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
    test_with_streaming()
    test_without_streaming()
    test_conversation_flow()
    test_ocr_like_usage()

if __name__ == '__main__':
    main()
