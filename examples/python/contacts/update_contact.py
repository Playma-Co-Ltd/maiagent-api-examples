import requests

API_KEY = '<your-api-key>'
BASE_URL = 'https://api.maiagent.ai/api/v1/'

CONTACT_ID = '<your-contact-id>'

assert API_KEY != '<your-api-key>', 'Please set your API key'
assert CONTACT_ID != '<your-contact-id>', 'Please set your contact id'


def main():
    headers = {'Authorization': f'Api-Key {API_KEY}'}

    # 使用 PATCH 更新部分欄位
    payload = {
        'name': 'John Doe (Updated)',
        'email': 'john.updated@example.com',
    }

    response = requests.patch(
        url=f'{BASE_URL}contacts/{CONTACT_ID}/',
        headers=headers,
        json=payload,
    )
    response.raise_for_status()
    contact = response.json()

    print(f"聯絡人更新成功！")
    print(f"  ID: {contact['id']}")
    print(f"  名稱: {contact['name']}")
    print(f"  Email: {contact.get('email', 'N/A')}")


if __name__ == '__main__':
    main()
