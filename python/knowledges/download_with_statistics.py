import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import MaiAgentHelper

# 設定 API Key 和知識庫 ID
API_KEY = '0yZD0JZY.PhUtANQUat5X5sWEav2GQgVkXJ2uR34D'
KNOWLEDGE_BASE_ID = '6b11f385-fc69-480e-982f-85a395954d5c'

# 請在運行前設定正確的值
assert API_KEY != '<your-api-key>', 'Please set your API key'
assert KNOWLEDGE_BASE_ID != '<your-knowledge-base-id>', 'Please set your knowledge base id'


def main():
    """
    帶詳細統計的下載範例
    """
    helper = MaiAgentHelper(API_KEY)
    
    print("=" * 60)
    print("知識庫檔案下載 - 詳細統計版本")
    print("=" * 60)
    
    try:
        print("\n開始下載...")
        result = helper.download_all_knowledge_base_files(
            knowledge_base_id=KNOWLEDGE_BASE_ID,
            download_dir="downloads_with_stats"
        )
        
        if result:
            print(f"\n📋 最終統計報告:")
            print(f"   知識庫 ID: {KNOWLEDGE_BASE_ID}")
            print(f"   下載目錄: {result['download_dir']}")
            print(f"   檔案總數: {result['total']}")
            print(f"   下載成功: {len(result['downloaded'])}")
            print(f"   下載失敗: {len(result['failed'])}")
            print(f"   實際檔案: {result.get('actual_file_count', 'N/A')}")
            
            # 檢查一致性
            if 'actual_file_count' in result:
                if len(result['downloaded']) == result['actual_file_count']:
                    print(f"   ✅ 統計一致！")
                else:
                    print(f"   ⚠️  統計不一致 (可能有檔案名衝突)")
                    print(f"      程式記錄: {len(result['downloaded'])}")
                    print(f"      實際檔案: {result['actual_file_count']}")
        else:
            print("❌ 下載失敗")
            
    except Exception as e:
        print(f"執行失敗：{e}")


if __name__ == '__main__':
    main()
