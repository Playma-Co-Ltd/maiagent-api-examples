# Python 範例

這個範例展示如何使用 MaiAgent API 發送訊息、設置 webhook 伺服器接收回應，以及獲取收件匣資訊。

## 檔案說明

1. [`send_message.py`](send_message.py): 用於向 MaiAgent API 建立對話、發送訊息的程式碼。
2. [`webhook_server.py`](webhook_server.py): 用於接收 webhook 通知的 Flask 伺服器。
3. [`get_inboxes.py`](get_inboxes.py): 用於獲取收件匣資訊的程式碼。

## 設置步驟

1. 安裝 localtunnel：
   ```
   npm install -g localtunnel
   ```

2. 安裝所需 Python 套件：
   ```
   pip install -r requirements.txt
   ```

3. 在 `send_message.py` 中設定您的 API 金鑰和 WebChat ID：
   ```python
   API_KEY = '您的 API 金鑰'
   WEBCHAT_ID = '您的 WebChat ID'
   TEXT_MESSAGE = '您的文字訊息'
   ```

4. 執行 webhook 伺服器：
   ```
   python webhook_server.py
   ```
   這將啟動一個本機伺服器，並提供一個公開 URL 用於接收 webhook 通知。

5. 在 MaiAgent 後台的「AI 助理」設定中配置 webhook URL。

## 使用方式

1. 發送訊息：
   ```
   python send_message.py
   ```
   此腳本會建立一個對話並發送一則測試訊息。

2. webhook 伺服器將接收並顯示來自 MaiAgent 的回應。

## 注意事項

- 在發送訊息之前，請確保 webhook 伺服器正在運作，以便接收回應。
- webhook 伺服器使用 `localtunnel` 將本機伺服器暴露給網際網路。每次重新啟動伺服器時，請務必在 MaiAgent 後台更新 webhook URL。
- 請確保已安裝 Node.js 和 npm，以便能夠安裝和使用 localtunnel。
