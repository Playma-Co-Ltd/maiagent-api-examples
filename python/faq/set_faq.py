import requests

# example BASE_URL: 'https://api.maiagent.ai/api/v1/'
BASE_URL = "<base-api-url>"
API_KEY = "<your-api-key>"

assert BASE_URL != "<base-api-url>", "Please set your base API URL"
assert API_KEY != "<your-api-key>", "Please set your API key"


def set_faq(question, answer, chatbot_id):
    url = f"{BASE_URL}api/faqs/"

    data = {"question": question, "answer": answer, "chatbot": chatbot_id}

    response = requests.post(
        url,
        headers={"Authorization": f"Api-Key {API_KEY}"},
        json=data,
    )

    return response.json()


# Example usage
if __name__ == "__main__":
    question = "這是什麼問題"
    answer = "我不知道"
    chatbot_id = "6f2fc12a-ca5e-4539-834d-e5d21181d199"

    result = set_faq(question, answer, chatbot_id)
    print(result)
