import os
from urllib.parse import urljoin

import requests
from utils import MaiAgentHelper

BASE_URL = 'https://api.maiagent.ai/api/v1/'
API_KEY = '<your-api-key>'
WEB_CHAT_ID = '<your-web-chat-id>'
BATCH_QA_FILE_ID = '<your-batch-qa-file-id>'


assert API_KEY != '<your-api-key>', 'Please set your API key'
assert WEB_CHAT_ID != '<your-web-chat-id>', 'Please set your web-chat id'
assert BATCH_QA_FILE_ID != '<your-batch-qa-file-id>', 'Please set your batch qa file id'


def main():
    maiagent_helper = MaiAgentHelper(API_KEY)
    downloaded_file = maiagent_helper.download_batch_qa_excel(WEB_CHAT_ID, BATCH_QA_FILE_ID)
    if downloaded_file:
        print(f'File saved as: {os.path.abspath(downloaded_file)}')


if __name__ == '__main__':
    main()
