import requests

BASE_URL = 'https://api.maiagent.ai/api/v1/'
API_KEY = '<your-api-key>'

WEBCHAT_ID = '<your-webchat-id>'
TEXT_MESSAGE = '<your-text-message>'

assert API_KEY != '<your-api-key>', 'Please set your API key'
assert WEBCHAT_ID != '<your-webchat-id>', 'Please set your webchat id'
assert TEXT_MESSAGE != '<your-text-message>', 'Please set your text message'


def main():
    try:
        # 建立 conversation
        response = requests.post(
            url=f'{BASE_URL}conversations/',
            headers={'Authorization': f'Api-Key {API_KEY}'},
            json={
                'webChat': WEBCHAT_ID,
            },
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(response.text)
        print(e)
        exit(1)
    except Exception as e:
        print(e)

    conversation_id = response.json()['id']

    try:
        # 傳送訊息
        response = requests.post(
            url=f'{BASE_URL}messages/',
            headers={'Authorization': f'Api-Key {API_KEY}'},
            json={
                'conversation': conversation_id,
                'content': TEXT_MESSAGE,
            },
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(response.text)
        print(e)
        exit(1)

    # 此處是直接回傳訊息建立的 response，訊息處理完成後，會以 webhook 通知
    print(response.text)

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
