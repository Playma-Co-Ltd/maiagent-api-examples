# 發送訊息範例

這個範例展示如何使用 MaiAgent API 發送訊息、設置 webhook 伺服器接收回應。

## 檔案說明

1. [`send_message.cs`](send_message.cs): 用於向 MaiAgent API 建立對話、發送訊息的程式碼。
2. [`send_image_message.cs`](send_image_message.cs): 用於向 MaiAgent API 建立對話、發送圖片訊息的程式碼。
3. [`webhook_server.cs`](webhook_server.cs): 用於接收 webhook 通知的 Flask 伺服器。
4. [`upload_attachment.cs`](upload_attachment.cs): 用於上傳檔案到 MaiAgent API 的程式碼。

## 設置步驟

1. 安裝 localtunnel：

```bash
npm install -g localtunnel
```

2. 在 `send_message.cs` 中設定您的 API 金鑰和 WebChat ID：

```csharp
API_KEY = '您的 API 金鑰'
WEB_CHAT_ID = '您的 WebChat ID'
TEXT_MESSAGE = '您的文字訊息'
```

3. 執行 webhook 伺服器：

```bash
csharp webhook_server.cs
```

這將啟動一個本機伺服器，並提供一個公開 URL 用於接收 webhook 通知。

4. 在 MaiAgent 後台的「AI 助理」設定中配置 webhook URL。


## 使用方式

1. 發送訊息：

```bash
csharp -m messages.send_message # 在 csharp 目錄下執行
```

此腳本會建立一個對話並發送一則測試訊息。

2. webhook 伺服器將接收並顯示來自 MaiAgent 的回應。

## 注意事項

- 在發送訊息之前，請確保 webhook 伺服器正在運作，以便接收回應。
- webhook 伺服器使用 `localtunnel` 將本機伺服器暴露給網際網路。每次重新啟動伺服器時，請務必在 MaiAgent 後台更新 webhook URL。
- 請確保已安裝 Node.js 和 npm，以便能夠安裝和使用 localtunnel。
