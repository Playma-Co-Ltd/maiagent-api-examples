import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import MaiAgentHelper

API_KEY = '<your-api-key>'

assert API_KEY != '<your-api-key>', 'Please set your API key'


def main():
    """
    綜合知識庫管理範例
    
    展示知識庫 API 的完整使用流程：
    1. 創建知識庫
    2. 上傳檔案
    3. 創建標籤
    4. 創建 FAQ
    5. 搜尋內容
    6. 管理和清理
    """
    maiagent_helper = MaiAgentHelper(API_KEY)

    try:
        # 1. 創建知識庫
        print("=" * 60)
        print("1. 創建知識庫")
        print("=" * 60)
        
        kb_response = maiagent_helper.create_knowledge_base(
            name="測試知識庫",
            description="這是一個用於測試的知識庫",
            number_of_retrieved_chunks=10,
            sentence_window_size=3,
            enable_hyde=True,
            similarity_cutoff=0.1,
            enable_rerank=True
        )
        
        kb_id = kb_response.get('id')
        print(f"知識庫創建成功！ID: {kb_id}")
        
        # 2. 創建標籤
        print("\n" + "=" * 60)
        print("2. 創建標籤")
        print("=" * 60)
        
        label_response = maiagent_helper.create_knowledge_base_label(
            knowledge_base_id=kb_id,
            name="技術文檔"
        )
        
        label_id = label_response.get('id')
        print(f"標籤創建成功！ID: {label_id}")
        
        # 3. 上傳檔案 (需要實際檔案路徑)
        print("\n" + "=" * 60)
        print("3. 上傳檔案")
        print("=" * 60)
        
        # 注意：這裡需要實際的檔案路徑
        # file_path = "path/to/your/file.pdf"
        # file_response = maiagent_helper.upload_knowledge_file(kb_id, file_path)
        # print(f"檔案上傳成功！")
        print("跳過檔案上傳 - 需要實際檔案路徑")
        
        # 4. 創建 FAQ
        print("\n" + "=" * 60)
        print("4. 創建 FAQ")
        print("=" * 60)
        
        faq_response = maiagent_helper.create_knowledge_base_faq(
            knowledge_base_id=kb_id,
            question="這個知識庫的用途是什麼？",
            answer="這個知識庫用於存儲和管理技術文檔，幫助用戶快速找到所需信息。",
            labels=[{"id": label_id, "name": "技術文檔"}]
        )
        
        faq_id = faq_response.get('id')
        print(f"FAQ 創建成功！ID: {faq_id}")
        
        # 5. 搜尋知識庫
        print("\n" + "=" * 60)
        print("5. 搜尋知識庫")
        print("=" * 60)
        
        search_results = maiagent_helper.search_knowledge_base(
            knowledge_base_id=kb_id,
            query="技術文檔"
        )
        
        print(f"搜尋結果數量: {len(search_results) if isinstance(search_results, list) else 0}")
        
        # 6. 查看知識庫詳情
        print("\n" + "=" * 60)
        print("6. 查看知識庫詳情")
        print("=" * 60)
        
        kb_detail = maiagent_helper.get_knowledge_base(kb_id)
        print(f"知識庫名稱: {kb_detail.get('name')}")
        print(f"知識庫描述: {kb_detail.get('description')}")
        print(f"檔案數量: {kb_detail.get('files_count', 0)}")
        print(f"創建時間: {kb_detail.get('created_at')}")
        
        # 7. 列出所有相關資源
        print("\n" + "=" * 60)
        print("7. 列出所有相關資源")
        print("=" * 60)
        
        # 列出標籤
        labels = maiagent_helper.list_knowledge_base_labels(kb_id)
        print(f"標籤數量: {len(labels.get('results', []))}")
        
        # 列出 FAQ
        faqs = maiagent_helper.list_knowledge_base_faqs(kb_id)
        print(f"FAQ 數量: {len(faqs.get('results', []))}")
        
        # 列出檔案
        files = maiagent_helper.list_knowledge_base_files(kb_id)
        print(f"檔案數量: {len(files.get('results', []))}")
        
        # 8. 清理資源 (可選)
        print("\n" + "=" * 60)
        print("8. 清理資源")
        print("=" * 60)
        
        # 取消註解以執行清理
        # print("刪除 FAQ...")
        # maiagent_helper.delete_knowledge_base_faq(kb_id, faq_id)
        # 
        # print("刪除標籤...")
        # maiagent_helper.delete_knowledge_base_label(kb_id, label_id)
        # 
        # print("刪除知識庫...")
        # maiagent_helper.delete_knowledge_base(kb_id)
        # 
        # print("清理完成！")
        
        print("跳過清理 - 取消註解以執行實際刪除")
        
        print("\n" + "=" * 60)
        print("範例執行完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"操作失敗：{e}")


if __name__ == '__main__':
    main() 
