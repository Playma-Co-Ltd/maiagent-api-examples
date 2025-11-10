import requests

BASE_URL = 'https://api.maiagent.ai/api/v1/'
API_KEY = '<your-api-key>'

CHATBOT_ID = '<your-chatbot-id>'
QUESTION = '<your-question>'
ANSWER = '<your-answer>'

assert API_KEY != '<your-api-key>', 'Please set your API key'

assert CHATBOT_ID != '<your-chatbot-id>', 'Please set your chatbot id'
assert QUESTION != '<your-question>', 'Please set your question'
assert ANSWER != '<your-answer>', 'Please set your answer'


def add_faq(chatbot_id: str, question: str, answer: str) -> int:
    url = f'{BASE_URL}faqs/'

    try:
        response = requests.post(
            url,
            headers={'Authorization': f'Api-Key {API_KEY}'},
            json={
                'chatbot': chatbot_id,
                'question': question,
                'answer': answer,
            },
        )
    except requests.exceptions.RequestException as e:
        print(response.text)
        print(e)
        exit(1)
    except Exception as e:
        print(e)
        exit(1)

    return response.status_code


if __name__ == '__main__':
    result = add_faq(
        chatbot_id=CHATBOT_ID,
        question=QUESTION,
        answer=ANSWER,
    )
    print(result)
