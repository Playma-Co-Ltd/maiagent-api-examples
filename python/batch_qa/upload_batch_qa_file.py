import json
import os

import requests
from utils import MaiAgentHelper



API_KEY = '<your-api-key>'
WEB_CHAT_ID = '<your-web-chat-id>'
FILE_PATH = '<your-file-path>'

assert API_KEY != '<your-api-key>', 'Please set your API key'
assert WEB_CHAT_ID != '<your-web-chat-id>', 'Please set your web-chat id'
assert FILE_PATH != '<your-file-path>', 'Please set your file path'


def main():
    maiagent_helper = MaiAgentHelper(API_KEY)
    original_filename = os.path.basename(FILE_PATH)

    upload_info = maiagent_helper.get_upload_url(
        file_path=FILE_PATH,
        model_name='batch-qa',
        field_name='file',
    )
    file_key = maiagent_helper.upload_file_to_s3(FILE_PATH, upload_info)
    maiagent_helper.upload_batch_qa_file(
        web_chat_id=WEB_CHAT_ID,
        file_key=file_key,
        original_filename=original_filename,
    )



if __name__ == '__main__':
    main()
