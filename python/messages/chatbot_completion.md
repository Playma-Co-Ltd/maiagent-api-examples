# Chatbot Completion API 使用說明

這個範例展示如何使用 MaiAgent API 與聊天機器人進行對話，包含串流模式、非串流模式、多輪對話以及帶附件的對話等場景。

## 測試場景

### 1. 串流模式對話

使用串流模式即時獲取聊天機器人的回應。

```python
# Request
POST /chatbots/{chatbot_id}/completions/
{
    "conversation": null,
    "message": {
        "content": "使用串流模式測試：請給我一個笑話",
        "attachments": []
    }
}

# Response Stream
{
    "conversation_id": "conv_xxx",
    "content": "從前有一隻",     # 第一部分內容
    "done": false
}
{
    "conversation_id": "conv_xxx",
    "content": "小狗在玩球",     # 第二部分內容
    "done": false
}
{
    "conversation_id": "conv_xxx",
    "content": "",              
    "done": true               # 結束標記
}
```

### 2. 非串流模式對話

一次性獲取完整的回應內容。

```python
# Request
POST /chatbots/{chatbot_id}/completions/?is_streaming=false
{
    "conversation": null,
    "message": {
        "content": "不使用串流模式測試：請給我一個笑話",
        "attachments": []
    }
}

# Response
{
    "conversation_id": "conv_xxx",
    "content": "從前有一隻小狗在玩球...",
    "done": false              # done 為 false 時代表還有訊息
}
{
    "conversation_id": "conv_xxx",
    "content": "",
    "done": true
}
```

### 3. 多輪對話

使用 conversation_id 維持對話上下文。

```python
# 第一次請求
POST /chatbots/{chatbot_id}/completions/
{
    "conversation": null,
    "message": {
        "content": "你好，請記住我說我叫小明",
        "attachments": []
    }
}

# 第一次響應
{
    "conversation_id": "conv_xxx",
    "content": "好的，我記住了，你叫小明",
    "done": false
}
{
    "conversation_id": "conv_xxx",
    "content": "",
    "done": true
}

# 第二次請求
POST /chatbots/{chatbot_id}/completions/
{
    "conversation": "conv_xxx", # 延續對話需附上 conversation_id
    "message": {
        "content": "我剛才說我叫什麼名字？",
        "attachments": []
    }
}

# 第二次響應
{
    "conversation_id": "conv_xxx",
    "content": "你剛才說你叫小明",
    "done": false
}
{
    "conversation_id": "conv_xxx",
    "content": "",
    "done": true
}
```

### 4. 帶附件的對話

上傳圖片並進行分析。

#### 4.1 請求預簽名上傳 URL
```python
# Request
POST /upload-presigned-url/
{
    "filename": "Cat03.jpg",
    "modelName": "attachment",
    "fieldName": "file",
    "fileSize": 123456
}

# Response
{
    "url": "https://s3.ap-northeast-1.amazonaws.com/...",
    "fields": {
        "key": "xxx",
        "x-amz-algorithm": "AWS4-HMAC-SHA256",
        "x-amz-credential": "xxx",
        "x-amz-date": "20240101T000000Z",
        "policy": "xxx",
        "x-amz-signature": "xxx"
    }
}
```

#### 4.2 上傳圖片到 S3
```python
# Request
POST https://s3.ap-northeast-1.amazonaws.com/whizchat-media-prod-django.playma.app
Form Data:
{
    "key": "<file_key>",
    "x-amz-algorithm": "AWS4-HMAC-SHA256",
    "x-amz-credential": "<aws_credential>",
    "x-amz-date": "<timestamp>",
    "policy": "<base64_encoded_policy>",
    "x-amz-signature": "<signature>",
    "file": "<file_content>"
}
```

#### 4.3 註冊附件
```python
# Request
POST /attachments/
{
    "file": "<file_key>",
    "filename": "<filename>",
    "type": "image"
}

# Response
{
    "id": "<attachment_id>",
    "file": "<file_url>",
    "filename": "<filename>",
    "type": "<type>"
}
```

#### 4.4 發送帶附件的訊息
```python
# Request
POST /chatbots/{chatbot_id}/completions/
{
    "conversation": null,
    "message": {
        "content": "請描述這張圖片的內容",
        "attachments": [{
            "id": "<attachment_id>",
            "type": "image",
            "filename": "<filename>",
            "file": "<file_url>"
        }]
    }
}

# Response Stream
{
    "conversation_id": "conv_xxx",
    "content": "這張圖片顯示了一隻",
    "done": false
}
{
    "conversation_id": "conv_xxx",
    "content": "可愛的貓咪",
    "done": false
}
{
    "conversation_id": "conv_xxx",
    "content": "",
    "done": true
}
```

### 使用須知

1. 對話模式選擇
   - 串流模式: 適合需要即時顯示回應的場景
   - 非串流模式: 適合需要一次性獲取完整回應的場景

2. 多輪對話
   - 使用 conversation_id 維持對話上下文
   - conversation=null 開啟新對話
   - 延續對話需附上 conversation_id

3. 附件上傳流程
   1. 獲取預簽名 URL
   2. 上傳檔案至 S3
   3. 註冊附件

4. 響應狀態說明
   - done=true: 對話結束,content 為空字符串
   - done=false: 對話進行中,content 不為空
