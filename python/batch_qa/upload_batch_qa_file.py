import json
import os

import requests

BASE_URL = "https://api.maiagent.ai/api/v1/"
STORAGE_URL = "https://s3.ap-northeast-1.amazonaws.com/whizchat-media-prod-django.playma.app"
API_KEY = "<your-api-key>"

WEBCHAT_ID = "<your-webchat-id>"
FILE_PATH = "<your-file-path>"

assert API_KEY != "<your-api-key>", "Please set your API key"
assert WEBCHAT_ID != "<your-webchat-id>", "Please set your webchat id"
assert FILE_PATH != "<your-file-path>", "Please set your file path"


def get_upload_url(filename: str, file_size: int) -> dict[str, str | dict[str, str]] | None:
    url = f"{BASE_URL}upload-presigned-url/"

    response = requests.post(
        url,
        headers={
            "Authorization": f"Api-Key {API_KEY}",
            "Content-Type": "application/json",
        },
        data=json.dumps(
            {
                "filename": filename,
                "modelName": "batch-qa",
                "fieldName": "file",
                "fileSize": file_size,
            }
        ),
    )

    response.raise_for_status()

    if response.status_code == 200:
        print("Successfully obtained upload URL")
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        exit(1)


def upload_file_to_s3(file_path: str, upload_data: dict[str, str | dict[str, str]]) -> str | None:
    with open(file_path, "rb") as file:
        response = requests.post(
            STORAGE_URL,
            data={
                "key": upload_data["fields"]["key"],
                "x-amz-algorithm": upload_data["fields"]["x-amz-algorithm"],
                "x-amz-credential": upload_data["fields"]["x-amz-credential"],
                "x-amz-date": upload_data["fields"]["x-amz-date"],
                "policy": upload_data["fields"]["policy"],
                "x-amz-signature": upload_data["fields"]["x-amz-signature"],
            },
            files={"file": (os.path.basename(file_path), file)},
        )

        if response.status_code == 204:
            print("Successfully uploaded file to S3")
            return upload_data["fields"]["key"]
        else:
            print(f"Error uploading file: {response.status_code}")
            print(response.text)
            exit(2)


def upload_batch_qa_file(file_key: str, original_filename: str):
    url = f"{BASE_URL}web-chats/{WEBCHAT_ID}/batch-qas/"

    try:
        response = requests.post(
            url,
            headers={
                "Authorization": f"Api-Key {API_KEY}",
            },
            json={
                "file": file_key,
                "filename": original_filename,
            },
        )
        response.raise_for_status()
        print("Successfully uploaded batch QA file")
        return True
    except requests.exceptions.RequestException as e:
        print(response.text)
        print(e)
        exit(3)
    except Exception as e:
        print(e)
        exit(3)


if __name__ == "__main__":
    file_size = os.path.getsize(FILE_PATH)
    original_filename = os.path.basename(FILE_PATH)

    upload_info = get_upload_url(original_filename, file_size)
    file_key = upload_file_to_s3(FILE_PATH, upload_info)
    uploaded = upload_batch_qa_file(file_key, original_filename)

    print("Entire process completed successfully")
