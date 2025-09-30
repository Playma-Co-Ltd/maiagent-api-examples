import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import MaiAgentHelper

API_KEY = '<your-api-key>'
KNOWLEDGE_BASE_ID = '<your-knowledge-base-id>'   # 你的知識庫 ID

assert API_KEY != '<your-api-key>', 'Please set your API key'
assert KNOWLEDGE_BASE_ID != '<your-knowledge-base-id>', 'Please set your knowledge base id'


def main():
    """
    知識庫檔案管理範例
    
    展示如何使用新的知識庫 API 管理檔案
    """
    maiagent_helper = MaiAgentHelper(API_KEY)

    try:
        # 1. 列出所有檔案
        print("1. 列出知識庫中的所有檔案...")
        files = maiagent_helper.list_knowledge_base_files(KNOWLEDGE_BASE_ID)
        
        if 'results' in files:
            file_list = files['results']
            print(f"找到 {len(file_list)} 個檔案：")
            for file in file_list:
                print(f"  ID: {file.get('id')}")
                print(f"  檔名: {file.get('filename')}")
                print(f"  檔案大小: {file.get('file_size', 'N/A')} bytes")
                print(f"  狀態: {file.get('status')}")
                print(f"  上傳時間: {file.get('created_at')}")
                print("-" * 50)
        
        # 2. 獲取特定檔案詳情
        if file_list and len(file_list) > 0:
            file_id = file_list[0].get('id')
            print(f"\n2. 獲取檔案詳情 (ID: {file_id})...")
            file_detail = maiagent_helper.get_knowledge_base_file(KNOWLEDGE_BASE_ID, file_id)
            print(f"檔名: {file_detail.get('filename')}")
            print(f"檔案類型: {file_detail.get('file_type')}")
            print(f"處理狀態: {file_detail.get('status')}")
            print(f"標籤: {file_detail.get('labels', [])}")
        
        # 3. 更新檔案元數據
        if file_list and len(file_list) > 0:
            file_id = file_list[0].get('id')
            print(f"\n3. 更新檔案元數據 (ID: {file_id})...")

            # 先獲取知識庫的標籤列表
            labels_response = maiagent_helper.list_knowledge_base_labels(KNOWLEDGE_BASE_ID)
            labels_list = labels_response.get('results', [])

            # 如果有標籤，使用第一個標籤；否則不設定標籤
            labels_to_set = [{"id": labels_list[0]['id']}] if labels_list else None

            updated_file = maiagent_helper.update_knowledge_base_file_metadata(
                knowledge_base_id=KNOWLEDGE_BASE_ID,
                file_id=file_id,
                labels=labels_to_set,
                raw_user_define_metadata={"category": "documentation", "priority": "high"}
            )
            print("檔案元數據更新成功")
            if labels_to_set:
                print(f"  已設定標籤: {updated_file.get('labels', [])}")
            print(f"  已設定自定義元數據: {updated_file.get('rawUserDefineMetadata', {})}")
        
        # 4. 批次操作範例
        #print("\n4. 批次操作範例...")
        
        # 批次刪除檔案 (可選，取消註解以執行)
        # if file_list and len(file_list) > 0:
        #     file_ids = [f.get('id') for f in file_list[:2]]  # 選取前兩個檔案
        #     print(f"批次刪除檔案 IDs: {file_ids}")
        #     maiagent_helper.batch_delete_knowledge_base_files(KNOWLEDGE_BASE_ID, file_ids)
        #     print("批次刪除完成")
        
        # 批次重新解析檔案 (可選，取消註解以執行)
        # if file_list and len(file_list) > 0:
        #     file_parsers = [
        #         {"id": file_list[0].get('id'), "parser": "pdf_parser"},
        #         {"id": file_list[1].get('id'), "parser": "text_parser"}
        #     ]
        #     print("批次重新解析檔案...")
        #     maiagent_helper.batch_reparse_knowledge_base_files(KNOWLEDGE_BASE_ID, file_parsers)
        #     print("批次重新解析完成")
        
    except Exception as e:
        print(f"檔案管理失敗：{e}")


if __name__ == '__main__':
    main() 
