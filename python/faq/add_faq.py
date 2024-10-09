import os
import requests
from dotenv import load_dotenv

from pathlib import Path


ROOT_DIR = Path(__file__).resolve(strict=True).parent.parent.parent

DOT_ENV_PATH = ROOT_DIR / ".env"
load_dotenv(DOT_ENV_PATH)

BASE_URL = os.environ.get('BASE_URL', default='https://api.maiagent.ai/api/v1/')
API_KEY = os.environ.get('API_KEY')


assert API_KEY is not None, 'Please set your API key'


def add_faq(question: str, answer: str, chatbot_id: str) -> int:
    url = f'{BASE_URL}faqs/'

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

    result = add_faq(question, answer, chatbot_id)
    print(result)
