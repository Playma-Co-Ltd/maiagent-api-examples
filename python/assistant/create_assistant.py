import requests
import json

BASE_URL = "https://api.maiagent.ai/api/v1/"
API_KEY = "<your-api-key>"

NAME = "<your-assistant-name>"
# model default to ID of "GPT-4o 2024-08-06"
MODEL_ID = "ba7da66a-6f30-414d-98f8-7d681a92d47a"
# rag default to ID of "MaiAgent RAG"
RAG_ID = "66261b7a-bd3f-4214-9c48-364c2e122b0f"
# instructions default to noting(""), if want to set instructions, please set it
INSTRUCTIONS = ""

assert API_KEY != "<your-api-key>", "Please set your API key"
assert NAME != "<your-assistant-name>", "Please set your assistant name"


def create_assistant(name, model_id, rag_id, instructions=""):
    url = f"{BASE_URL}chatbots/"

    try:
        response = requests.post(
            url,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/plain, */*",
                "Authorization": f"Api-Key {API_KEY}",
            },
            data=json.dumps(
                {
                    "name": name,
                    "model": model_id,
                    "rag": rag_id,
                    "instructions": instructions,
                },
            ),
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error creating assistant: {e}")
        print(response.text if response else "No response")
        return None


if __name__ == "__main__":
    result = create_assistant(
        name=NAME,
        model_id=MODEL_ID,
        rag_id=RAG_ID,
        instructions=INSTRUCTIONS,
    )
    if result:
        print("Assistant created successfully:")
        print(json.dumps(result, indent=2))
    else:
        print("Failed to create assistant")
