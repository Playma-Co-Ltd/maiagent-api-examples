import requests

API_KEY = '<your-api-key>'
BASE_URL = 'https://api.maiagent.ai/api/v1/'

CONTACT_ID = '<your-contact-id>'

assert API_KEY != '<your-api-key>', 'Please set your API key'
assert CONTACT_ID != '<your-contact-id>', 'Please set your contact id'


def main():
    headers = {'Authorization': f'Api-Key {API_KEY}'}

    # 刪除聯絡人（軟刪除）
    response = requests.delete(
        url=f'{BASE_URL}contacts/{CONTACT_ID}/',
        headers=headers,
    )
    response.raise_for_status()

    print(f"聯絡人 {CONTACT_ID} 已刪除")


if __name__ == '__main__':
    main()
