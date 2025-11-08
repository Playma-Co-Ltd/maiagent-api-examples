# C# 範例

這個範例展示如何使用 MaiAgent API 管理助理、發送訊息、管理知識庫、管理常見問題。

## 範例資料夾說明

- [assistants](assistants/): 管理助理的範例
- [messages](messages/): 發送訊息的範例
  - chatbot_completion.md: 聊天機器人 API 使用說明
  - [send_message.cs](messages/send_message.cs): 發送訊息範例
  - [send_image_message.cs](messages/send_image_message.cs): 發送圖片訊息範例
  - [webhook_server.cs](messages/webhook_server.cs): Webhook 伺服器範例
- [knowledges](knowledges/): 管理知識庫的範例
- [faqs](faqs/): 管理常見問題的範例
- [batch_qa](batch_qa/): 發送批次問答的範例
- [others](others/): 其他有用的範例

# 使用 MaiAgentHelper

MaiAgentHelper 是一個用於與 MaiAgent API 互動的輔助類別，提供了一系列方便的方法來處理對話、訊息、檔案上傳和知識庫管理等功能。

- 請參考 [utils/maiagent.md](utils/maiagent.md) 了解 MaiAgentHelper 的完整功能和使用方法。

## 設置步驟

1. 安裝 .NET SDK：

建議使用 .NET 8.0 或更新版本

```bash
# Windows (使用 winget)
winget install Microsoft.DotNet.SDK.8

# macOS (使用 Homebrew)
brew install dotnet

# Linux (請參考官方文檔)
# https://learn.microsoft.com/dotnet/core/install/linux
```

2. 安裝所需 NuGet 套件（如果需要）：

```bash
# 如需要讀寫 Excel 檔案
dotnet add package EPPlus

# 如需要 .env 檔案支援
dotnet add package DotNetEnv

# 如需要額外的 JSON 處理
dotnet add package Newtonsoft.Json
```

3. 設置環境變數：

```bash
cp .env.example .env
# 編輯 .env 文件，填入您的 API 金鑰和其他配置
```

4. 編譯和運行範例：

```bash
# 編譯單一檔案
csc messages/send_message.cs utils/maiagent.cs

# 或使用 dotnet 腳本運行（需要 .csproj 檔案）
dotnet run messages/send_message.cs

# 直接使用 C# 腳本模式（如果支援）
dotnet script messages/send_message.cs
```

## 注意事項

1. 請確保您已經取得 MaiAgent API 金鑰
2. 運行範例前請先完成環境變數設置
3. 這些範例檔案是從 Python 轉換而來，可能需要調整類型和引用才能成功編譯
4. 某些範例（如 batch_upload_advanced.cs）包含複雜的異步邏輯，已標記為需要手動實作

## Python 與 C# 對照

本專案包含 Python 和 C# 兩種語言的範例：

- Python 範例位於 `python/` 資料夾
- C# 範例位於 `csharp/` 資料夾（本資料夾）

兩者功能相同，可根據您的開發需求選擇使用。
