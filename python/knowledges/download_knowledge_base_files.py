import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import MaiAgentHelper

API_KEY = '0yZD0JZY.PhUtANQUat5X5sWEav2GQgVkXJ2uR34D'
KNOWLEDGE_BASE_ID = '6b11f385-fc69-480e-982f-85a395954d5c'   # 你的知識庫 ID

assert API_KEY != '<your-api-key>', 'Please set your API key'
assert KNOWLEDGE_BASE_ID != '<your-knowledge-base-id>', 'Please set your knowledge base id'


def main():
    """
    下載知識庫檔案範例
    
    展示如何使用 MaiAgent API 下載知識庫中的檔案
    """
    maiagent_helper = MaiAgentHelper(API_KEY)

    try:
        print("=" * 60)
        print("MaiAgent 知識庫檔案下載範例")
        print("=" * 60)
        
        # 1. 列出所有檔案（預覽）
        print("\n1. 列出知識庫中的所有檔案...")
        files = maiagent_helper.list_knowledge_base_files(KNOWLEDGE_BASE_ID)
        
        if 'results' in files:
            file_list = files['results']
            print(f"找到 {len(file_list)} 個檔案：")
            for i, file in enumerate(file_list, 1):
                print(f"  {i}. ID: {file.get('id')}")
                print(f"     檔名: {file.get('filename')}")
                print(f"     大小: {file.get('file_size', 'N/A')} bytes")
                print(f"     狀態: {file.get('status')}")
                print("-" * 50)
        else:
            print("無法獲取檔案列表")
            return

        if not file_list:
            print("知識庫中沒有檔案可下載")
            return

        # 2. 詢問用戶是否下載
        total_size = sum(file.get('file_size', 0) for file in file_list)
        print(f"\n總計檔案: {len(file_list)} 個")
        if total_size > 0:
            print(f"總檔案大小: {format_file_size(total_size)}")
        
        print("\n選擇操作：")
        print("1. 下載所有檔案")
        print("2. 取消")
        
        try:
            choice = input("\n請輸入選擇 (1-2): ").strip()
        except KeyboardInterrupt:
            print("\n操作已取消")
            return
            
        if choice == '1':
            # 下載所有檔案
            download_all_files(maiagent_helper, KNOWLEDGE_BASE_ID)
            
        elif choice == '2':
            print("操作已取消")
            return
        else:
            print("無效的選擇")
            
    except Exception as e:
        print(f"程式執行失敗：{e}")


def download_all_files(helper, knowledge_base_id):
    """下載所有檔案"""
    print("\n" + "=" * 50)
    print("開始下載所有檔案...")
    print("=" * 50)
    
    # 自定義下載目錄
    download_dir = f"downloads/knowledge_base_{knowledge_base_id}"
    
    result = helper.download_all_knowledge_base_files(knowledge_base_id, download_dir)
    
    if result:
        print(f"\n📁 所有檔案已下載至: {result['download_dir']}")
        
        # 統計資訊
        total_size = sum(file.get('size', 0) for file in result['downloaded'])
        print(f"📊 統計資訊：")
        print(f"   總檔案數: {result['total']}")
        print(f"   下載成功: {result['downloaded'].__len__()}")
        print(f"   下載失敗: {result['failed'].__len__()}")
        if total_size > 0:
            print(f"   總大小: {format_file_size(total_size)}")
    else:
        print("❌ 下載過程中發生錯誤")





def format_file_size(size_bytes):
    """格式化檔案大小"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    size_bytes = int(size_bytes)
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


if __name__ == '__main__':
    main()
