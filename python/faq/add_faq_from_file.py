import os
import pandas as pd
import requests

from pathlib import Path
from dotenv import load_dotenv

import time

ROOT_DIR = Path(__file__).resolve(strict=True).parent.parent.parent
load_dotenv(ROOT_DIR / ".env")

BASE_URL = os.environ.get("BASE_URL", default="https://api.maiagent.ai/api/v1/")
API_KEY = os.environ.get("API_KEY")

print(BASE_URL)
print(API_KEY)

assert API_KEY is not None, "Please set your API key"


def add_faq(chatbot_id: str, question: str, answer: str) -> int:
    url = f"{BASE_URL}faqs/"

    try:
        response = requests.post(
            url,
            headers={"Authorization": f"Api-Key {API_KEY}"},
            json={
                "chatbot": chatbot_id,
                "question": question,
                "answer": answer,
            },
        )
    except requests.exceptions.RequestException as e:
        print(response.text)  # type: ignore
        print(e)
        exit(1)
    except Exception as e:
        print(e)
        exit(1)

    return response


def add_faq_from_file(file_path: str, chatbot_id: str) -> int:
    """
    Add FAQs from a file to the chatbot.
    """
    df = pd.read_csv(file_path)

    for _, row in df.iterrows():
        question, answer = row.iloc[1], row.iloc[2]

        if isinstance(question, str) and isinstance(answer, str):
            # print(question, answer)
            res = add_faq(chatbot_id, question, answer)
            if res.status_code == 201:
                print(res.status_code)
            else:
                print(res.text)
            time.sleep(5)
        else:
            print(f"Skipping row {_} due to non-string values: {question}, {answer}")

    return 0


if __name__ == "__main__":
    chatbot_ids = [
        "7ab8d348-0f14-4476-a563-ca1498e194ff",  # 廟宇前燃燒興盛的香火
        "b68d0cd8-2fc8-44e4-9c65-32f283ccf9cc",  # 潮間帶上波濤浪花及礁石碰撞聲
        "9196ae89-9708-4c8c-bc89-b90eb04d5a9a",  # 村莊巷弄裡的居民與玩耍的孩童
        # "6f2fc12a-ca5e-4539-834d-e5d21181d199", # dev
    ]
    for chatbot_id in chatbot_ids:
        add_faq_from_file("faq/常見問題FAQ.csv", chatbot_id)
