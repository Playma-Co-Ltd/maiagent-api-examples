import requests

API_KEY = '<your-api-key>'
BASE_URL = 'https://api.maiagent.ai/api/v1/'

CONTACT_ID = '<your-contact-id>'

assert API_KEY != '<your-api-key>', 'Please set your API key'
assert CONTACT_ID != '<your-contact-id>', 'Please set your contact id'


def main():
    headers = {'Authorization': f'Api-Key {API_KEY}'}

    # 取得聯絡人的所有對話
    response = requests.get(
        url=f'{BASE_URL}contacts/{CONTACT_ID}/conversations',
        headers=headers,
    )
    response.raise_for_status()
    data = response.json()

    print(f"共 {data['count']} 筆對話")
    for conversation in data['results']:
        print(f"  - 對話 ID: {conversation['id']}")

    # 也可以用關鍵字搜尋對話中的訊息
    response = requests.get(
        url=f'{BASE_URL}contacts/{CONTACT_ID}/conversations',
        headers=headers,
        params={
            'keyword': '你好',
            # 'inboxes': '<inbox-id>',  # 可依 inbox 篩選
        },
    )
    response.raise_for_status()
    data = response.json()

    print(f"\n搜尋結果：共 {data['count']} 筆對話")

    # 取得最新的一筆對話
    response = requests.get(
        url=f'{BASE_URL}contacts/{CONTACT_ID}/conversations/latest',
        headers=headers,
    )
    if response.status_code == 200:
        latest = response.json()
        print(f"\n最新對話 ID: {latest['id']}")
    elif response.status_code == 404:
        print("\n該聯絡人尚無對話紀錄")


if __name__ == '__main__':
    main()
