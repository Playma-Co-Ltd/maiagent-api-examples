import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import MaiAgentHelper

API_KEY = '<your-api-key>'

# 知識庫基本資訊
KNOWLEDGE_BASE_NAME = 'My Knowledge Base'
KNOWLEDGE_BASE_DESCRIPTION = 'This is a sample knowledge base for testing purposes.'

# 可選設定
EMBEDDING_MODEL = None  # 可設定為特定的嵌入模型 ID
RERANKER_MODEL = None  # 可設定為特定的重新排序模型 ID
CHATBOTS = None  # 可設定為聊天機器人 ID 列表，例如 [{'id': 'chatbot-id', 'name': 'chatbot-name'}]

assert API_KEY != '<your-api-key>', 'Please set your API key'


def main():
    """
    創建知識庫範例
    
    展示如何使用新的知識庫 API 創建知識庫
    """
    maiagent_helper = MaiAgentHelper(API_KEY)

    try:
        # 創建知識庫
        response = maiagent_helper.create_knowledge_base(
            name=KNOWLEDGE_BASE_NAME,
            description=KNOWLEDGE_BASE_DESCRIPTION,
            embedding_model=EMBEDDING_MODEL,
            reranker_model=RERANKER_MODEL,
            number_of_retrieved_chunks=12,  # 預設值
            sentence_window_size=2,  # 預設值
            enable_hyde=False,  # 預設值
            similarity_cutoff=0.0,  # 預設值
            enable_rerank=True,  # 預設值
            chatbots=CHATBOTS
        )
        
        print(f"知識庫創建成功！")
        print(f"知識庫 ID: {response.get('id')}")
        print(f"知識庫名稱: {response.get('name')}")
        print(f"知識庫描述: {response.get('description')}")
        print(f"創建時間: {response.get('created_at')}")
        
    except Exception as e:
        print(f"知識庫創建失敗：{e}")


if __name__ == '__main__':
    main() 