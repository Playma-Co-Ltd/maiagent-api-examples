import requests

API_KEY = '<your-api-key>'
BASE_URL = 'https://api.maiagent.ai/api/v1/'

assert API_KEY != '<your-api-key>', 'Please set your API key'


def main():
    headers = {'Authorization': f'Api-Key {API_KEY}'}

    # 列出所有聯絡人
    response = requests.get(
        url=f'{BASE_URL}contacts/',
        headers=headers,
    )
    response.raise_for_status()
    data = response.json()

    print(f"共 {data['count']} 筆聯絡人")
    for contact in data['results']:
        print(f"  - {contact['name']} (ID: {contact['id']})")

    # 使用篩選參數查詢
    # query: 依名稱、ID 或 source_id 搜尋（模糊比對）
    # inboxes: 依 inbox ID 篩選
    response = requests.get(
        url=f'{BASE_URL}contacts/',
        headers=headers,
        params={
            'query': 'John',
            'limit': 10,
            'offset': 0,
        },
    )
    response.raise_for_status()
    data = response.json()

    print(f"\n搜尋結果：共 {data['count']} 筆")
    for contact in data['results']:
        print(f"  - {contact['name']} (email: {contact.get('email', 'N/A')})")

    """
    回應格式：
    {
        "count": 100,
        "next": "https://api.maiagent.ai/api/v1/contacts/?limit=20&offset=20",
        "previous": null,
        "results": [
            {
                "id": "contact-uuid",
                "name": "John Doe",
                "email": "john@example.com",
                "phone_number": "+886912345678",
                "avatar": "https://example.com/avatar.jpg",
                "source_id": "external_id_123",
                "inboxes": [
                    {"id": "inbox-uuid", "name": "My Inbox"}
                ],
                "query_metadata": {"source": "web"},
                "mcp_credentials": [],
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        ]
    }
    """


if __name__ == '__main__':
    main()
