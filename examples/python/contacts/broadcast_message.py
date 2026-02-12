import requests

API_KEY = '<your-api-key>'
BASE_URL = 'https://api.maiagent.ai/api/v1/'

assert API_KEY != '<your-api-key>', 'Please set your API key'


def main():
    headers = {'Authorization': f'Api-Key {API_KEY}'}

    # ===== 模式 1：指定聯絡人 ID 群發 =====
    payload = {
        'message': '您好，這是一則群發訊息！',
        'contact_ids': [
            '<contact-id-1>',
            '<contact-id-2>',
            '<contact-id-3>',
        ],
    }

    response = requests.post(
        url=f'{BASE_URL}contacts/broadcast-message',
        headers=headers,
        json=payload,
    )
    response.raise_for_status()
    result = response.json()

    print(f"群發結果：")
    print(f"  總共: {result['total_contacts']} 人")
    print(f"  成功: {result['success_count']} 人")
    print(f"  失敗: {result['error_count']} 人")

    for item in result['results']:
        print(f"  ✓ contact: {item['contact_id']}, message: {item['message_id']}")

    for error in result['errors']:
        print(f"  ✗ contact: {error['contact_id']}, error: {error['error']}")

    # ===== 模式 2：指定 inbox，排除特定聯絡人 =====
    # payload = {
    #     'message': '您好，這是一則群發訊息！',
    #     'inbox_id': '<inbox-id>',
    #     'exclude_contact_ids': ['<contact-id-to-exclude>'],
    # }

    # ===== 模式 3：對整個 inbox 所有聯絡人群發 =====
    # payload = {
    #     'message': '您好，這是一則群發訊息！',
    #     'inbox_id': '<inbox-id>',
    # }

    """
    回應格式：
    {
        "results": [
            {
                "contact_id": "uuid",
                "conversation_id": "uuid",
                "message_id": "uuid",
                "status": "success"
            }
        ],
        "errors": [
            {
                "contact_id": "uuid",
                "error": "No conversation found for this contact."
            }
        ],
        "total_contacts": 3,
        "success_count": 2,
        "error_count": 1
    }
    """


if __name__ == '__main__':
    main()
