import os

from utils import MaiAgentHelper

API_KEY = '<your-api-key>'

WEB_CHAT_ID = '<your-webchat-id>'
TEXT_MESSAGE = '<your-text-message>'
IMAGE_PATH = '<your-image-path>'

assert API_KEY != '<your-api-key>', 'Please set your API key'
assert WEB_CHAT_ID != '<your-webchat-id>', 'Please set your webchat id'
assert TEXT_MESSAGE != '<your-text-message>', 'Please set your text message'
assert IMAGE_PATH != '<your-image-path>', 'Please set your image path'


def main():
    maiagent_helper = MaiAgentHelper(API_KEY)

    # 建立對話
    create_conversation_response = maiagent_helper.create_conversation(WEB_CHAT_ID)
    conversation_id = create_conversation_response['id']

    # 上傳附件
    upload_attachment_response = maiagent_helper.upload_attachment(conversation_id, IMAGE_PATH)

    # 發送訊息
    response = maiagent_helper.send_message(
        conversation_id,
        content=TEXT_MESSAGE,
        attachments=[{
            'id': upload_attachment_response['id'],
            'type': 'image',
            'filename': upload_attachment_response['filename'],
            'file': upload_attachment_response['file'],
        }],
    )

    # 此處是直接回傳訊息建立的 response，訊息處理完成後，會以 webhook 通知
    print(response)

    # Webhook 網址請於 MaiAgent 後台「AI 助理」設定
    # 訊息回傳格式如下
    # - 訊息內容位於 content 欄位
    # - 引用資料位於 citations 欄位
    """
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
    """


if __name__ == '__main__':
    main()
