import requests

BASE_URL = 'https://api.maiagent.ai/api/v1/'
API_KEY = '<your-api-key>'

CHATBOT_ID = '<your-chatbot-id>'

FILES_ID = '<your-files-id>'

assert API_KEY != '<your-api-key>', 'Please set your API key'
assert CHATBOT_ID != '<your-chatbot-id>', 'Please set your chatbot id'

def delete_knowledge(files_id):
    url = f'{BASE_URL}chatbots/{CHATBOT_ID}/files/{files_id}/'

    headers = {
        'Authorization': f'Api-Key {API_KEY}',
    }

    response = requests.delete(url, headers=headers)

    if response.status_code == 204:
        print(f'Successfully deleted knowledge with ID: {files_id}')
    else:
        print(f'Error: {response.status_code}')
        print(response.text)


if __name__ == "__main__":
    delete_knowledge(FILES_ID)