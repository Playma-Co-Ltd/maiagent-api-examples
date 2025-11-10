import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import MaiAgentHelper

API_KEY = '<your-api-key>'

KNOWLEDGE_BASE_ID = '<your-knowledge-base-id>'   # 你的知識庫 ID
FILE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    'inputs',
    '台灣高鐵FAQ.xlsx'
)  # 使用存在的檔案

assert API_KEY != '<your-api-key>', 'Please set your API key'
assert KNOWLEDGE_BASE_ID != '<your-knowledge-base-id>', 'Please set your knowledge base id'
# assert FILE_PATH != '<your-file-path>', 'Please set your file path'

def main():
    """
    上傳檔案到知識庫範例
    
    使用新的知識庫 API 上傳檔案
    """
    maiagent_helper = MaiAgentHelper(API_KEY)

    try:
        response = maiagent_helper.upload_knowledge_file(KNOWLEDGE_BASE_ID, FILE_PATH)
        print(f"檔案上傳成功：{response}")
    except Exception as e:
        print(f"檔案上傳失敗：{e}")

if __name__ == '__main__':
    main()
