# !python -m parsers.test_parsers
from utils import MaiAgentHelper
from utils.config import API_KEY, BASE_URL, STORAGE_URL, CHATBOT_ID
import os
import argparse

# 測試配置
TEST_FILES_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
    'test_files'
)

TEST_FILES = {
    'PDF': '2212.10496v1.pdf',
    'DOCX': 'voice_204893_dia_regular_docx.docx',
    'XLSX': '詐騙案件案情清單-113年8月全部.xlsx',
    'PPTX': 'AOAI+KB.pptx',
    # 'MP3': 'speech_to_text_1.mp3',
}

assert API_KEY != '<your-api-key>', '請設定你的 API key'
assert CHATBOT_ID != '<your-chatbot-id>', '請設定你的 chatbot id'

def get_supported_parsers(maiagent_helper: MaiAgentHelper, file_path: str) -> list[dict]:
    """取得檔案支援的解析器列表
    
    Args:
        maiagent_helper: MaiAgent 幫助器實例
        file_path: 檔案路徑
        
    Returns:
        list[dict]: 支援的解析器列表，每個解析器包含 id, name, provider, isDefault
    """
    file_extension = os.path.splitext(file_path)[1].lower()
    supported_types = maiagent_helper.get_supported_file_types()
    
    for file_type in supported_types:
        if file_type['fileType'] == file_extension:
            return file_type['parsers']
    
    return []

def print_parsers(parsers: list[dict]):
    """印出解析器列表"""
    print("\n可用的解析器:")
    for parser in parsers:
        default_mark = "[預設]" if parser['isDefault'] else ""
        print(f"- {parser['name']} ({parser['provider']}) {default_mark}")
        print(f"  ID: {parser['id']}")

def get_default_parser_id(parsers: list[dict]) -> str:
    """取得預設解析器 ID"""
    default_parsers = [p for p in parsers if p['isDefault']]
    if default_parsers:
        print(f"預設解析器: {default_parsers[0]['name']}")
        return default_parsers[0]['id']
    return None

def get_parser_by_name(parsers: list[dict], parser_name: str) -> str:
    """根據解析器名稱取得 ID"""
    for parser in parsers:
        if parser['name'].lower() == parser_name.lower():
            print(f"選擇解析器: {parser['name']}")
            return parser['id']
    return None

def print_file_info(file_info: dict):
    """印出檔案資訊"""
    print(f"檔案名稱: {file_info.get('filename')}")
    print(f"檔案 ID: {file_info.get('id')}")
    print(f"狀態: {file_info.get('status', '處理中')}")
    print(f"解析器: {file_info.get('parser')}")
    print("-" * 30)

def select_parser(parsers: list[dict]) -> str:
    """互動式選擇解析器
    
    Args:
        parsers: 解析器列表
        
    Returns:
        str: 選擇的解析器 ID，如果直接按 Enter 則回傳 None
    """
    print("\n可用的解析器:")
    for idx, parser in enumerate(parsers, 1):
        default_mark = "[預設]" if parser['isDefault'] else ""
        print(f"{idx}. {parser['name']} ({parser['provider']}) {default_mark}")
    
    while True:
        try:
            choice = input("\n請選擇解析器 (輸入數字), 直接按 Enter 測試預設行為: ")
            if not choice:  # 使用 None
                print("不指定解析器，測試預設行為")
                return None
                    
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(parsers):
                selected_parser = parsers[choice_idx]
                print(f"選擇解析器: {selected_parser['name']}")
                return selected_parser['id']
            else:
                print(f"錯誤: 請輸入 1-{len(parsers)} 之間的數字")
        except ValueError:
            print("錯誤: 請輸入有效的數字")

def test_file_upload(maiagent_helper: MaiAgentHelper, file_type: str, file_name: str):
    """測試單一檔案上傳"""
    file_path = os.path.join(TEST_FILES_DIR, file_name)
    if not os.path.exists(file_path):
        print(f"找不到檔案: {file_path}")
        return
    
    print(f"\n測試 {file_type} 檔案上傳:")
    print(f"檔案: {file_name}")
    
    try:
        # 取得支援的解析器
        parsers = get_supported_parsers(maiagent_helper, file_path)
        if not parsers:
            print(f"錯誤: 不支援的檔案類型 {os.path.splitext(file_name)[1]}")
            return
            
        # 選擇解析器
        parser_id = select_parser(parsers)
        
        # 上傳檔案
        response = maiagent_helper.upload_knowledge_file(CHATBOT_ID, file_path, parser_id)
        print("\n上傳結果:")
        for file_info in response:
            print_file_info(file_info)
            
    except Exception as e:
        print(f"錯誤: {str(e)}")

def main():
    """測試不同類型知識庫檔案上傳流程"""
    parser = argparse.ArgumentParser(description='測試知識庫檔案上傳')
    parser.add_argument('--file-type', choices=TEST_FILES.keys(), help='指定要測試的檔案類型')
    args = parser.parse_args()
    
    print("開始測試知識庫檔案上傳流程...")
    
    # 初始化 MaiAgent 幫助器
    maiagent_helper = MaiAgentHelper(
        api_key=API_KEY,
        base_url=BASE_URL,
        storage_url=STORAGE_URL
    )
    
    if args.file_type:
        # 測試指定檔案類型
        test_file_upload(
            maiagent_helper, 
            args.file_type, 
            TEST_FILES[args.file_type]
        )
    else:
        # 測試所有檔案類型
        for file_type, file_name in TEST_FILES.items():
            test_file_upload(maiagent_helper, file_type, file_name)

if __name__ == '__main__':
    main()
