import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import MaiAgentHelper

API_KEY = '<your-api-key>'
KNOWLEDGE_BASE_ID = '<your-knowledge-base-id>'   # 你的知識庫 ID

# assert API_KEY != '<your-api-key>', 'Please set your API key'
# assert KNOWLEDGE_BASE_ID != '<your-knowledge-base-id>', 'Please set your knowledge base id'


def main():
    """
    知識庫 FAQ 管理範例
    
    展示如何使用新的知識庫 API 管理 FAQ
    """
    maiagent_helper = MaiAgentHelper(API_KEY)

    try:
        # 1. 創建 FAQ
        print("1. 創建 FAQ...")
        new_faq = maiagent_helper.create_knowledge_base_faq(
            knowledge_base_id=KNOWLEDGE_BASE_ID,
            question="什麼是 MaiAgent？",
            answer="MaiAgent 是一個強大的 AI 助手平台，幫助您建立智能聊天機器人。",
            labels=[{"id": "label-id", "name": "general"}]  # 可選標籤
        )
        faq_id = new_faq.get('id')
        print(f"FAQ 創建成功，ID: {faq_id}")
        
        # 2. 列出所有 FAQ
        print("\n2. 列出所有 FAQ...")
        faqs = maiagent_helper.list_knowledge_base_faqs(KNOWLEDGE_BASE_ID)
        
        if 'results' in faqs:
            faq_list = faqs['results']
            print(f"找到 {len(faq_list)} 個 FAQ：")
            for faq in faq_list:
                print(f"  ID: {faq.get('id')}")
                print(f"  問題: {faq.get('question')}")
                print(f"  答案: {faq.get('answer')}")
                print(f"  標籤: {faq.get('labels', [])}")
                print("-" * 30)
        
        # 3. 更新 FAQ
        if faq_id:
            print(f"\n3. 更新 FAQ (ID: {faq_id})...")
            updated_faq = maiagent_helper.update_knowledge_base_faq(
                knowledge_base_id=KNOWLEDGE_BASE_ID,
                faq_id=faq_id,
                question="什麼是 MaiAgent AI 助手？",
                answer="MaiAgent 是一個進階的 AI 助手平台，專為企業和個人提供智能聊天機器人解決方案。"
            )
            print("FAQ 更新成功")
        
        # 4. 獲取特定 FAQ
        if faq_id:
            print(f"\n4. 獲取 FAQ 詳情 (ID: {faq_id})...")
            faq_detail = maiagent_helper.get_knowledge_base_faq(KNOWLEDGE_BASE_ID, faq_id)
            print(f"問題: {faq_detail.get('question')}")
            print(f"答案: {faq_detail.get('answer')}")
        
        # 5. 刪除 FAQ (可選，取消註解以執行)
        # if faq_id:
        #     print(f"\n5. 刪除 FAQ (ID: {faq_id})...")
        #     maiagent_helper.delete_knowledge_base_faq(KNOWLEDGE_BASE_ID, faq_id)
        #     print("FAQ 刪除成功")
        
    except Exception as e:
        print(f"FAQ 管理失敗：{e}")


if __name__ == '__main__':
    main() 