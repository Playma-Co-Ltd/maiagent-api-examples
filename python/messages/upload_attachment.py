# python -m messages.upload_attachment
import mimetypes
from pathlib import Path
import requests
import os
from utils.config import API_KEY, BASE_URL

TEST_IMAGE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
    'test_files', 
    '異型介紹.txt'
)

def main(file_path: str | Path) -> dict:
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f'檔案不存在：{file_path}')
    
    headers = {'Authorization': f'Api-Key {API_KEY}'}
    mime_type, _ = mimetypes.guess_type(file_path)

    with open(file_path, 'rb') as file:
        files = {'file': (file_path.name, file, mime_type)}
        response = requests.post(f'{BASE_URL}attachments/', headers=headers, files=files)

    print(response.json())


if __name__ == '__main__':
    main(TEST_IMAGE_PATH)