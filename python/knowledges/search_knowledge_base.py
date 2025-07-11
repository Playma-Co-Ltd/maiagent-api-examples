import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import MaiAgentHelper

API_KEY = '<your-api-key>'
KNOWLEDGE_BASE_ID = '<your-knowledge-base-id>'   # 你的知識庫 ID
SEARCH_QUERY = '高鐵'

# assert API_KEY != '<your-api-key>', 'Please set your API key'
# assert KNOWLEDGE_BASE_ID != '<your-knowledge-base-id>', 'Please set your knowledge base id'
# assert SEARCH_QUERY != '<your-search-query>', 'Please set your search query'


def main():
    """
    搜尋知識庫範例
    
    展示如何使用新的知識庫 API 搜尋知識庫內容
    """
    maiagent_helper = MaiAgentHelper(API_KEY)

    try:
        # 搜尋知識庫內容
        response = maiagent_helper.search_knowledge_base(KNOWLEDGE_BASE_ID, SEARCH_QUERY)
        
        if isinstance(response, list):
            search_results = response
            print(f"搜尋查詢：{SEARCH_QUERY}")
            print(f"找到 {len(search_results)} 個相關結果：")
            print("-" * 50)
            
            for idx, result in enumerate(search_results, 1):
                print(f"結果 {idx}:")
                print(f"內容: {result.get('text', '無內容')}")
                print(f"相似度分數: {result.get('score', 'N/A')}")
                print(f"檔案名稱: {result.get('chatbot_file', {}).get('filename', 'Unknown')}")
                print(f"頁碼: {result.get('page_number', 'N/A')}")
                print("-" * 50)
        else:
            print("搜尋結果格式不正確")
            
    except Exception as e:
        print(f"搜尋知識庫失敗：{e}")


if __name__ == '__main__':
    main() 