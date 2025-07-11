import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import MaiAgentHelper

API_KEY = '<your-api-key>'

assert API_KEY != '<your-api-key>', 'Please set your API key'


def main():
    """
    列出知識庫範例
    
    展示如何使用新的知識庫 API 列出所有知識庫
    """
    maiagent_helper = MaiAgentHelper(API_KEY)

    try:
        # 列出所有知識庫
        response = maiagent_helper.list_knowledge_bases()
        
        if 'results' in response:
            knowledge_bases = response['results']
            print(f"找到 {len(knowledge_bases)} 個知識庫：")
            print("-" * 50)
            
            for kb in knowledge_bases:
                print(f"知識庫 ID: {kb.get('id')}")
                print(f"名稱: {kb.get('name')}")
                print(f"描述: {kb.get('description', '無描述')}")
                print(f"檔案數量: {kb.get('files_count', 0)}")
                print(f"創建時間: {kb.get('created_at')}")
                print(f"更新時間: {kb.get('updated_at')}")
                print("-" * 50)
        else:
            print("沒有找到知識庫")
            
    except Exception as e:
        print(f"列出知識庫失敗：{e}")


if __name__ == '__main__':
    main() 