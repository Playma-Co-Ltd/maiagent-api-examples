# MaiAgentHelper 類別文檔

`MaiAgentHelper` 是一個用於與 MaiAgent API 互動的輔助類別，提供了一系列方便的方法來處理對話、訊息、檔案上傳和知識庫管理等功能。

## 類別初始化

```python
from utils.maiagent import MaiAgentHelper

helper = MaiAgentHelper(
    api_key='your_api_key_here',
    base_url='https://api.maiagent.ai/api/v1/',  # 選填
    storage_url='https://s3.ap-northeast-1.amazonaws.com/whizchat-media-prod-django.playma.app'  # 選填
)
```

### 參數說明
- `api_key` (str): MaiAgent API 金鑰
- `base_url` (str, 選填): API 基礎 URL，預設為 'https://api.maiagent.ai/api/v1/'
- `storage_url` (str, 選填): 儲存服務 URL，預設為 S3 儲存位置

## 主要方法

### 對話管理

#### create_conversation
建立新的對話。

```python
conversation = helper.create_conversation(web_chat_id='your_web_chat_id')
```

**參數：**
- `web_chat_id` (str): 網頁聊天 ID

**回傳：**
- dict: 包含新建對話資訊的字典

### 訊息處理

#### send_message
發送訊息到指定對話。

```python
message = helper.send_message(
    conversation_id='your_conversation_id',
    content='Hello, world!',
    attachments=None  # 選填
)
```

**參數：**
- `conversation_id` (str): 對話 ID
- `content` (str): 訊息內容
- `attachments` (list, 選填): 附件列表

**回傳：**
- dict: 包含已發送訊息資訊的字典

### 檔案上傳

#### get_upload_url
獲取檔案上傳的預簽署 URL。

```python
upload_url = helper.get_upload_url(
    file_path='path/to/file',
    model_name='model_name',
    field_name='file'  # 選填
)
```

**參數：**
- `file_path` (str): 檔案路徑
- `model_name` (str): 模型名稱
- `field_name` (str, 選填): 欄位名稱，預設為 'file'

#### upload_file_to_s3
將檔案上傳到 S3 儲存空間。

```python
file_key = helper.upload_file_to_s3(
    file_path='path/to/file',
    upload_data=upload_url
)
```

**參數：**
- `file_path` (str): 檔案路徑
- `upload_data` (dict): 上傳資料（從 get_upload_url 獲得）

### 附件管理

#### update_attachment
更新對話中的附件資訊。

```python
attachment = helper.update_attachment(
    conversation_id='your_conversation_id',
    file_id='file_key',
    original_filename='filename.jpg'
)
```

**參數：**
- `conversation_id` (str): 對話 ID
- `file_id` (str): 檔案 ID
- `original_filename` (str): 原始檔案名稱

#### update_attachment_without_conversation
不需要對話 ID 的附件更新。

```python
attachment = helper.update_attachment_without_conversation(
    file_id='file_key',
    original_filename='filename.jpg'
)
```

### 知識庫管理

#### upload_knowledge_file
上傳知識庫檔案。

```python
knowledge_file = helper.upload_knowledge_file(
    chatbot_id='your_chatbot_id',
    file_path='path/to/knowledge.pdf'
)
```

**參數：**
- `chatbot_id` (str): 聊天機器人 ID
- `file_path` (str): 檔案路徑

#### delete_knowledge_file
刪除知識庫檔案。

```python
helper.delete_knowledge_file(
    chatbot_id='your_chatbot_id',
    file_id='your_file_id'
)
```

### 批次問答管理

#### upload_batch_qa_file
上傳批次問答檔案。

```python
batch_qa = helper.upload_batch_qa_file(
    web_chat_id='your_web_chat_id',
    file_key='your_file_key',
    original_filename='qa_file.xlsx'
)
```

**參數：**
- `web_chat_id` (str): 網頁聊天 ID
- `file_key` (str): 檔案金鑰
- `original_filename` (str): 原始檔案名稱

#### download_batch_qa_excel
下載批次問答 Excel 檔案。

```python
filename = helper.download_batch_qa_excel(
    webchat_id='your_web_chat_id',
    batch_qa_file_id='your_batch_qa_file_id'
)
```

### 收件匣管理

#### get_inbox_items
獲取所有收件匣項目。

```python
inbox_items = helper.get_inbox_items()
```

#### display_inbox_items
顯示收件匣項目資訊。

```python
helper.display_inbox_items(inbox_items)
```

### 聊天機器人對話

#### create_chatbot_completion
建立聊天機器人回應，支援一般和串流模式。

```python
# 一般模式
response = helper.create_chatbot_completion(
    chatbot_id='your_chatbot_id',
    content='What is the weather today?',
    attachments=None,  # 選填
    conversation_id=None,  # 選填
    is_streaming=False  # 選填
)

# 串流模式
for chunk in helper.create_chatbot_completion(
    chatbot_id='your_chatbot_id',
    content='Tell me a long story',
    is_streaming=True
):
    print(chunk['content'], end='')
```

**參數：**
- `chatbot_id` (str): 聊天機器人 ID
- `content` (str): 訊息內容
- `attachments` (list, 選填): 附件列表
- `conversation_id` (str, 選填): 對話 ID
- `is_streaming` (bool, 選填): 是否使用串流模式

**回傳：**
- 一般模式：dict，包含回應內容
- 串流模式：Generator，產生串流回應

## 錯誤處理

所有方法都包含基本的錯誤處理機制：
- 檢查 HTTP 回應狀態
- 處理請求異常
- 提供錯誤訊息和詳細資訊

## 注意事項

1. 使用前請確保已設定正確的 API 金鑰
2. 檔案上傳時請確認檔案存在且可讀取
3. 串流模式回應需要適當的處理機制
4. 所有 API 呼叫都需要網路連線
