import requests

# example BASE_URL: 'https://api.maiagent.ai/api/v1/'
BASE_URL = '<base-api-url>'
API_KEY = '<your-api-key>'

assert BASE_URL != '<base-api-url>', 'Please set your base API URL'
assert API_KEY != '<your-api-key>', 'Please set your API key'


def set_faq(question: str, answer: str, chatbot_id: str) -> int:
    url = f'{BASE_URL}api/faqs/'

    try:
        response = requests.post(
            url,
            headers={'Authorization': f'Api-Key {API_KEY}'},
            json={'question': question, 'answer': answer, 'chatbot': chatbot_id},
        )
    except requests.exceptions.RequestException as e:
        print(response.text)  # type: ignore
        print(e)
        exit(1)
    except Exception as e:
        print(e)
        exit(1)

    return response.status_code


# Example usage
if __name__ == '__main__':
    question = 'question'
    answer = 'answer'
    chatbot_id = 'chatbot_id'

    result = set_faq(question, answer, chatbot_id)
    print(result)
