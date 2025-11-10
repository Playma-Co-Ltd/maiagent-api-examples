# Python 範例

這個範例展示如何使用 MaiAgent API 管理助理、發送訊息、管理知識庫、管理常見問題。

## 範例資料夾說明

- [assistants](assistants/): 管理助理的範例
- [messages](messages/): 發送訊息的範例
  - chatbot_completion.md: 聊天機器人 API 使用說明
  - send_message.py: 發送訊息範例
  - send_image_message.py: 發送圖片訊息範例
  - webhook_server.py: Webhook 伺服器範例
- [knowledges](knowledges/): 管理知識庫的範例
- [faqs](faqs/): 管理常見問題的範例
- [batch_qa](batch_qa/): 發送批次問答的範例
- [others](others/): 其他有用的範例

# 使用 MaiAgentHelper

MaiAgentHelper 是一個用於與 MaiAgent API 互動的輔助類別，提供了一系列方便的方法來處理對話、訊息、檔案上傳和知識庫管理等功能。

- 請參考 [utils/maiagent.md](utils/maiagent.md) 了解 MaiAgentHelper 的完整功能和使用方法。
## 設置步驟

1. 安裝所需 Python 套件：

python 版本建議 3.11

```bash
python3.11 -m venv .venv  # 建立虛擬環境
source .venv/bin/activate  # 啟動虛擬環境 (Linux/Mac)
# 或
.venv\Scripts\activate  # 啟動虛擬環境 (Windows)
pip install -r requirements.txt  # 安裝套件
```

2. 設置環境變數：
```bash
cp .env.example .env
# 編輯 .env 文件，填入您的 API 金鑰和其他配置
```

3. 運行測試：
```bash
python -m messages.chatbot_completion  # 運行聊天機器人範例
python -m messages.send_message  # 運行發送訊息範例
# ... 其他範例
```

## 注意事項

1. 請確保您已經取得 MaiAgent API 金鑰
2. 運行範例前請先完成環境變數設置
3. 建議使用虛擬環境來管理套件相依性
