import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import MaiAgentHelper

API_KEY = '<your-api-key>'

KNOWLEDGE_BASE_ID = '<your-knowledge-base-id>'  # 你的知識庫 ID
FILE_ID = '<your-files-id>' # 剛才上傳的檔案 ID

# assert API_KEY != '<your-api-key>', 'Please set your API key'
# assert KNOWLEDGE_BASE_ID != '<your-knowledge-base-id>', 'Please set your knowledge base id'
# assert FILE_ID != '<your-file-id>', 'Please set your file id'


def main():
    """
    刪除知識庫檔案範例
    
    使用新的知識庫 API 刪除檔案
    """
    maiagent_helper = MaiAgentHelper(API_KEY)

    try:
        result = maiagent_helper.delete_knowledge_file(KNOWLEDGE_BASE_ID, FILE_ID)
        # 只有當沒有拋出異常時才顯示成功訊息
        if result is None:  # delete_knowledge_file 成功時不返回任何東西
            print(f"檔案刪除成功，檔案 ID: {FILE_ID}")
    except Exception as e:
        print(f"檔案刪除失敗：{e}")

if __name__ == "__main__":
    main()
