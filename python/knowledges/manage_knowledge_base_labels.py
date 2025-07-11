import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import MaiAgentHelper

API_KEY = '<your-api-key>'
KNOWLEDGE_BASE_ID = '<your-knowledge-base-id>'  # 你的知識庫 ID

# assert API_KEY != '<your-api-key>', 'Please set your API key'
# assert KNOWLEDGE_BASE_ID != '<your-knowledge-base-id>', 'Please set your knowledge base id'


def main():
    """
    知識庫標籤管理範例
    
    展示如何使用新的知識庫 API 管理標籤
    """
    maiagent_helper = MaiAgentHelper(API_KEY)

    try:
        # 1. 創建標籤
        print("1. 創建標籤...")
        import time
        label_name = f"測試標籤_{int(time.time())}"  # 使用時間戳避免重複
        new_label = maiagent_helper.create_knowledge_base_label(
            knowledge_base_id=KNOWLEDGE_BASE_ID,
            name=label_name
        )
        label_id = new_label.get('id')
        print(f"標籤創建成功，ID: {label_id}")
        
        # 2. 列出所有標籤
        print("\n2. 列出所有標籤...")
        labels = maiagent_helper.list_knowledge_base_labels(KNOWLEDGE_BASE_ID)
        
        if 'results' in labels:
            label_list = labels['results']
            print(f"找到 {len(label_list)} 個標籤：")
            for label in label_list:
                print(f"  ID: {label.get('id')}")
                print(f"  名稱: {label.get('name')}")
                print("-" * 30)
        
        # 3. 更新標籤
        if label_id:
            print(f"\n3. 更新標籤 (ID: {label_id})...")
            updated_name = f"{label_name} - 更新版"
            updated_label = maiagent_helper.update_knowledge_base_label(
                knowledge_base_id=KNOWLEDGE_BASE_ID,
                label_id=label_id,
                name=updated_name
            )
            print("標籤更新成功")
        
        # 4. 獲取特定標籤
        if label_id:
            print(f"\n4. 獲取標籤詳情 (ID: {label_id})...")
            label_detail = maiagent_helper.get_knowledge_base_label(KNOWLEDGE_BASE_ID, label_id)
            print(f"標籤名稱: {label_detail.get('name')}")
        
        # 5. 刪除標籤 (可選，取消註解以執行)
        # if label_id:
        #     print(f"\n5. 刪除標籤 (ID: {label_id})...")
        #     maiagent_helper.delete_knowledge_base_label(KNOWLEDGE_BASE_ID, label_id)
        #     print("標籤刪除成功")
        
    except Exception as e:
        print(f"標籤管理失敗：{e}")


if __name__ == '__main__':
    main() 