import json
import os

import requests

BASE_URL = 'https://api.maiagent.ai/api/v1/'
STORAGE_URL = 'https://s3.ap-northeast-1.amazonaws.com/autox-media-dev.playma.app'
API_KEY = '<your-api-key>'

CHATBOT_ID = '<your-chatbot-id>'
FILE_PATH = '<your-file-path>'

assert API_KEY != '<your-api-key>', 'Please set your API key'
assert CHATBOT_ID != '<your-chatbot-id>', 'Please set your chatbot id'
assert FILE_PATH != '<your-file-path>', 'Please set your file path'

def get_upload_url(filename, file_size):
    url = f"{BASE_URL}upload-presigned-url/"
    
    headers = {
        "Authorization": f"Api-Key {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "filename": filename,
        "modelName": "chatbot-file",
        "fieldName": "file",
        "fileSize": file_size
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(payload))

    response.raise_for_status()

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

def upload_file_to_s3(file_path, upload_data):
    with open(file_path, 'rb') as file:
        files = {'file': (os.path.basename(file_path), file)}
        data = {
            'key': upload_data['fields']['key'],
            'x-amz-algorithm': upload_data['fields']['x-amz-algorithm'],
            'x-amz-credential': upload_data['fields']['x-amz-credential'],
            'x-amz-date': upload_data['fields']['x-amz-date'],
            'policy': upload_data['fields']['policy'],
            'x-amz-signature': upload_data['fields']['x-amz-signature']
        }
        
        response = requests.post(STORAGE_URL, data=data, files=files)
        
        if response.status_code == 204:
            print("File uploaded successfully")
            return upload_data['fields']['key']
        else:
            print(f"Error uploading file: {response.status_code}")
            print(response.text)
            return None

def update_chatbot_files(file_key, original_filename):
    url = f'{BASE_URL}chatbots/{CHATBOT_ID}/files/'

    headers = {
        'Authorization': f'Api-Key {API_KEY}',
    }
    
    payload = {
        "files": [
            {
                "file": file_key,
                "filename": original_filename
            }
        ]
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(payload))

    response.raise_for_status()

    try:
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(response.text)
        print(e)
        exit(1)
    except Exception as e:
        print(e)
        exit(1)


def main():
    file_path = FILE_PATH
    file_size = os.path.getsize(file_path)
    original_filename = os.path.basename(file_path)
    
    upload_info = get_upload_url(original_filename, file_size)
    
    if upload_info:
        print("Upload URL obtained successfully")
        
        # 上傳文件到 S3
        file_key = upload_file_to_s3(file_path, upload_info)
        if file_key:
            print("File uploaded to S3 successfully")
            
            if update_chatbot_files(file_key, original_filename):
                print("Entire process completed successfully")
            else:
                print("Failed to update chatbot files")
        else:
            print("File upload to S3 failed")
    else:
        print("Failed to obtain upload URL")

if __name__ == '__main__':
    main()
