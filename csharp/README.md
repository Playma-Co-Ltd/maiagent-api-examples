# C# 範例

此資料夾包含 C# 範例，展示如何使用 MaiAgent API 管理助理、發送訊息、管理知識庫和處理常見問題。

## 範例資料夾說明

- [assistants](assistants/): 管理助理的範例
- [messages](messages/): 發送訊息的範例
  - `send_message.cs`: 發送訊息範例
  - `send_image_message.cs`: 發送圖片訊息範例
  - `webhook_server.cs`: Webhook 伺服器範例
  - `chatbot_completion.cs`: 聊天機器人 API 使用範例
- [knowledges](knowledges/): 管理知識庫的範例
- [faqs](faqs/): 管理常見問題的範例
- [batch_qa](batch_qa/): 批次問答處理範例
- [others](others/): 其他實用範例
- [utils](utils/): MaiAgent API 互動的輔助類別

## 使用 MaiAgentHelper

`MaiAgentHelper` 是用於與 MaiAgent API 互動的輔助類別，提供處理對話、訊息、檔案上傳和知識庫管理的便利方法。

## 設置步驟

### 1. 前置需求

- .NET 8.0 SDK 或更新版本
- Visual Studio 2022、Visual Studio Code 或 JetBrains Rider（推薦）

### 2. 安裝 .NET SDK

從 [https://dotnet.microsoft.com/download](https://dotnet.microsoft.com/download) 下載並安裝

### 3. 還原相依套件

```bash
cd csharp
dotnet restore
```

### 4. 設定組態

編輯 `appsettings.Development.json` 並填入您的 API 金鑰和設定：

```json
{
  "MaiAgent": {
    "BaseUrl": "https://api.maiagent.ai/api/v1/",
    "ApiKey": "your-api-key-here",
    "ChatbotId": "your-chatbot-id-here",
    "WebChatId": "your-webchat-id-here"
  }
}
```

**⚠️ 安全提醒：** 永遠不要將含有真實憑證的 `appsettings.Development.json` 提交至版本控制。

### 5. 建置專案

```bash
dotnet build
```

### 6. 執行範例

```bash
# 執行特定範例
dotnet run --project MaiAgentExamples.csproj

# 或執行個別檔案（如果設置為獨立專案）
cd messages
dotnet run send_message.cs
```

## 專案結構

```
csharp/
├── MaiAgentExamples.sln          # 方案檔
├── MaiAgentExamples.csproj       # 專案檔（含相依套件）
├── appsettings.json              # 組態（範本）
├── appsettings.Development.json  # 開發環境組態（本機，不納入 git）
├── assistants/                   # 助理管理範例
├── messages/                     # 訊息範例
├── knowledges/                   # 知識庫範例
├── faqs/                         # 常見問題管理範例
├── batch_qa/                     # 批次問答範例
├── others/                       # 其他工具
└── utils/                        # 輔助類別
```

## 使用的 NuGet 套件

此專案使用以下 NuGet 套件（相當於 Python 的 requirements.txt）：

| Python 套件 | C# 對應套件 | 用途 |
|------------|------------|------|
| `requests` | `RestSharp` 或 `HttpClient` | HTTP 請求 |
| `Flask` | `ASP.NET Core` | Web 框架 |
| `python-dotenv` | `Microsoft.Extensions.Configuration` | 組態管理 |
| `sseclient-py` | `Sse.Client` | Server-Sent Events |
| `black` | 內建 `dotnet format` | 程式碼格式化 |
| `pre-commit` | Git hooks | 程式碼品質檢查 |

## 組態管理

### Python vs C#

**Python (`.env`)：**
```bash
MAIAGENT_API_KEY=your-api-key
MAIAGENT_BASE_URL=https://api.maiagent.ai/api/v1/
```

**C# (`appsettings.json`)：**
```json
{
  "MaiAgent": {
    "ApiKey": "your-api-key",
    "BaseUrl": "https://api.maiagent.ai/api/v1/"
  }
}
```

### 在 C# 中讀取組態

```csharp
using Microsoft.Extensions.Configuration;

var configuration = new ConfigurationBuilder()
    .SetBasePath(Directory.GetCurrentDirectory())
    .AddJsonFile("appsettings.json", optional: false)
    .AddJsonFile("appsettings.Development.json", optional: true)
    .AddEnvironmentVariables()
    .Build();

string apiKey = configuration["MaiAgent:ApiKey"];
string baseUrl = configuration["MaiAgent:BaseUrl"];
```

## 常見任務

### 格式化程式碼
```bash
dotnet format
```

### 執行測試（如有新增）
```bash
dotnet test
```

### 建置發行版本
```bash
dotnet build --configuration Release
```

### 發行獨立執行檔
```bash
dotnet publish -c Release -r win-x64 --self-contained
```

## 注意事項

1. **需要 API 金鑰：** 執行範例前請確保已取得 MaiAgent API 金鑰
2. **先完成組態：** 執行前請先在 `appsettings.Development.json` 中完成組態設定
3. **程式碼調整：** 轉換後的 C# 程式碼可能需要手動調整：
   - 型別推斷（許多變數為 `object` 型別）
   - Async/await 模式
   - 例外處理
   - LINQ 最佳化
4. **非同步程式碼：** 含有 Python `async with` 陳述式的檔案無法自動轉換，需要手動翻譯

## 轉換說明

這些檔案使用 pytocs 轉換。已知限制：
- 不支援 Python 的 `async with` 陳述式
- 型別推斷有限（大多數型別為 `object`）
- 某些 Python 慣用語法可能無法完美轉換為 C#

正式環境使用時，請考慮：
- 加入適當的型別註解
- 正確實作 async/await 模式
- 新增例外處理
- 建立適當的類別結構
- 新增單元測試

## 資源

- [MaiAgent API 文件](https://maiagent.ai/docs)
- [.NET 文件](https://docs.microsoft.com/zh-tw/dotnet/)
- [pytocs GitHub](https://github.com/uxmal/pytocs)

## 取得協助

如果遇到問題：
1. 檢查 `appsettings.Development.json` 中的組態
2. 驗證您的 API 金鑰是否有效
3. 查看 [MaiAgent API 文件](https://maiagent.ai/docs)
4. 檢視轉換後的程式碼，確認是否需要調整
