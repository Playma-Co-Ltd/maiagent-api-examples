import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import MaiAgentHelper

# 設定 API Key 和知識庫 ID
API_KEY = '<your-api-key>'
KNOWLEDGE_BASE_ID = '<your-knowledge-base-id>'

# 請在運行前設定正確的值
assert API_KEY != '<your-api-key>', 'Please set your API key'
assert KNOWLEDGE_BASE_ID != '<your-knowledge-base-id>', 'Please set your knowledge base id'


def simple_download_example():
    """
    簡單的知識庫檔案下載範例
    """
    # 初始化 helper
    helper = MaiAgentHelper(API_KEY)
    
    # 下載所有檔案到 'downloads' 資料夾
    print("開始下載知識庫中的所有檔案...")
    result = helper.download_all_knowledge_base_files(
        knowledge_base_id=KNOWLEDGE_BASE_ID,
        download_dir="downloads"  # 可選：指定下載目錄
    )
    
    # 檢查結果
    if result:
        print(f"\n下載完成！")
        print(f"成功下載: {len(result['downloaded'])} 個檔案")
        print(f"下載失敗: {len(result['failed'])} 個檔案")
        print(f"檔案位置: {result['download_dir']}")
    else:
        print("下載失敗")


def download_with_confirmation():
    """
    帶確認的下載範例
    """
    helper = MaiAgentHelper(API_KEY)
    
    print("=" * 50)
    print("知識庫檔案下載")
    print("=" * 50)
    
    # 先列出檔案數量
    print("正在檢查知識庫...")
    files = helper.list_knowledge_base_files(KNOWLEDGE_BASE_ID)
    file_list = files.get('results', [])
    
    if not file_list:
        print("知識庫中沒有檔案")
        return
    
    total_size = sum(file.get('file_size', 0) for file in file_list)
    print(f"找到 {len(file_list)} 個檔案")
    if total_size > 0:
        # 簡單的檔案大小格式化
        if total_size < 1024:
            size_str = f"{total_size} B"
        elif total_size < 1024 * 1024:
            size_str = f"{total_size / 1024:.1f} KB"
        elif total_size < 1024 * 1024 * 1024:
            size_str = f"{total_size / (1024 * 1024):.1f} MB"
        else:
            size_str = f"{total_size / (1024 * 1024 * 1024):.1f} GB"
        print(f"總大小: {size_str}")
    
    # 詢問是否下載
    try:
        confirm = input("\n是否要下載所有檔案? (y/N): ").strip().lower()
        if confirm == 'y' or confirm == 'yes':
            print("\n開始下載...")
            result = helper.download_all_knowledge_base_files(KNOWLEDGE_BASE_ID)
            if result:
                print(f"\n✅ 下載完成！位置: {result['download_dir']}")
        else:
            print("已取消下載")
    except KeyboardInterrupt:
        print("\n已取消下載")


if __name__ == '__main__':
    # 執行簡單下載範例（直接下載）
    # simple_download_example()
    
    # 或執行帶確認的下載範例
    download_with_confirmation()
