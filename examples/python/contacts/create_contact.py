import requests

API_KEY = '<your-api-key>'
BASE_URL = 'https://api.maiagent.ai/api/v1/'

# 聯絡人所屬的 inbox ID（必填）
INBOX_ID = '<your-inbox-id>'

assert API_KEY != '<your-api-key>', 'Please set your API key'
assert INBOX_ID != '<your-inbox-id>', 'Please set your inbox id'


def main():
    headers = {'Authorization': f'Api-Key {API_KEY}'}

    # 建立聯絡人
    payload = {
        'name': 'John Doe',
        'email': 'john@example.com',
        'phone_number': '+886912345678',
        'inboxes': [{'id': INBOX_ID}],
        # 選填欄位
        # 'avatar': 'https://example.com/avatar.jpg',
        # 'source_id': 'external_id_123',
        # 'query_metadata': {'source': 'web', 'campaign': 'spring_2024'},
    }

    response = requests.post(
        url=f'{BASE_URL}contacts/',
        headers=headers,
        json=payload,
    )
    response.raise_for_status()
    contact = response.json()

    print(f"聯絡人建立成功！")
    print(f"  ID: {contact['id']}")
    print(f"  名稱: {contact['name']}")
    print(f"  Email: {contact.get('email', 'N/A')}")
    print(f"  Inboxes: {[inbox['name'] for inbox in contact['inboxes']]}")

    """
    回應格式：
    {
        "id": "contact-uuid",
        "name": "John Doe",
        "email": "john@example.com",
        "phone_number": "+886912345678",
        "avatar": null,
        "source_id": null,
        "inboxes": [
            {"id": "inbox-uuid", "name": "My Inbox"}
        ],
        "query_metadata": null,
        "mcp_credentials": [],
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }
    """


if __name__ == '__main__':
    main()
