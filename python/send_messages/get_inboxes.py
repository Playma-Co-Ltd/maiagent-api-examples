import requests

BASE_URL = 'https://api.maiagent.ai/api/v1/'
API_KEY = '<your-api-key>'

assert API_KEY != '<your-api-key>', 'Please set your API key'


def get_inbox_items():
    inbox_items = []

    url = f'{BASE_URL}inboxes/'
    while True:
        try:
            response = requests.get(
                url=url,
                headers={'Authorization': f'Api-Key {API_KEY}'},
            )
            response.raise_for_status()
            inbox_items.extend(response.json()['results'])
        except requests.exceptions.RequestException as e:
            print(response.text)
            print(e)
            exit(1)
        except Exception as e:
            print(e)
            exit(1)

        url = response.json()['next']
        if url is None:
            break

    return inbox_items


def display_inbox_items(inbox_items):
    for inbox_item in inbox_items:
        inbox_id = inbox_item['id']
        webchat_id = inbox_item['channel']['id']
        webchat_name = inbox_item['channel']['name']
        print(f'Inbox ID: {inbox_id}, Webchat ID: {webchat_id}, Webchat Name: {webchat_name}')


def main():
    inbox_items = get_inbox_items()
    display_inbox_items(inbox_items)


if __name__ == '__main__':
    main()
