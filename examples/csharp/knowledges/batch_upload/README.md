# 批量上傳與檔案管理工具 (Batch Upload & File Management Tools)

這是一套完整的知識庫檔案管理解決方案，包含高效能批量上傳工具和智慧檔案修復工具。

## 功能特色

### 🚀 高效能上傳
- **異步並發上傳**：同時處理多個檔案，顯著提升上傳速度
- **可調整並發數**：可根據網路環境調整同時上傳的檔案數量
- **智慧速度控制**：自動調整上傳速度以獲得最佳效能

### 🔄 斷點續傳
- **自動恢復機制**：程式中斷後可從上次停止的位置繼續
- **固定 Checkpoint**：使用單一檔案累積記錄，避免重複上傳
- **Knowledge File ID 追蹤**：記錄每個檔案的知識庫 ID，確保完整性
- **進度持久化**：定期儲存進度，確保資料不遺失

### 📊 視覺化進度追蹤
- **進度條顯示**：美觀的進度條顯示上傳進度
- **即時統計資訊**：顯示成功/失敗數量、上傳速率
- **完整日誌記錄**：記錄所有上傳過程和錯誤訊息
- **詳細報告生成**：產生包含統計資訊的 JSON 報告

### 🔍 完整性檢查
- **自動完整性驗證**：上傳完成後自動比對知識庫內容
- **漏傳檔案檢測**：識別可能失敗或被刪除的檔案
- **重複檔案提醒**：發現可能重複上傳的檔案
- **詳細分析報告**：產生完整的完整性檢查報告

### 🛡️ 錯誤處理
- **自動重試機制**：失敗檔案會自動重試，可設定重試次數
- **錯誤分類記錄**：詳細記錄每個失敗檔案的錯誤原因
- **優雅中斷處理**：支援 Ctrl+C 中斷，會先儲存進度再退出

### 📁 智慧檔案管理
- **獨立輸出目錄**：根據來源資料夾和知識庫 ID 創建唯一目錄
- **分類檔案存放**：Checkpoint、日誌、報告分別存放在不同資料夾
- **自動過濾檔案**：自動跳過隱藏檔案和系統檔案

## 工具概覽

### 🚀 批量上傳工具
- **`batch_upload_advanced.cs`** - 高效能批量檔案上傳主程式

### 🔍 檔案狀態管理工具
- **`scan_file_status.cs`** - 掃描知識庫檔案狀態，識別問題檔案
- **`delete_duplicate_files.cs`** - 刪除重複檔案，清理知識庫
- **`fix_failed_files.cs`** - 修復失敗檔案，自動重新上傳
- **`upload_missing_files.cs`** - 補充缺失檔案，確保完整性

## 檔案結構

```
batch_upload/
├── batch_upload_advanced.cs    # 主上傳程式
├── scan_file_status.cs         # 檔案狀態掃描工具
├── delete_duplicate_files.cs   # 重複檔案刪除工具
├── fix_failed_files.cs         # 失敗檔案修復工具
├── upload_missing_files.cs     # 缺失檔案上傳工具
├── README.md                   # 說明文件
└── upload_outputs/             # 輸出目錄
    └── {資料夾名}_{知識庫ID}/
        ├── checkpoints/
        │   └── upload_checkpoint.json
        ├── logs/
        │   └── upload_log_YYYYMMDD_HHMMSS.log
        └── reports/
            ├── upload_report_YYYYMMDD_HHMMSS.json
            ├── integrity_check_YYYYMMDD_HHMMSS.json
            ├── status_scan_YYYYMMDD_HHMMSS.json
            ├── duplicate_deletion_log_YYYYMMDD_HHMMSS.json
            ├── fix_failed_files_log_YYYYMMDD_HHMMSS.json
            └── missing_files_upload_YYYYMMDD_HHMMSS.json
```

## 設定說明

### 必要設定
在 `batch_upload_advanced.cs` 中修改以下參數：

```csharp
public static string API_KEY = "<your-api-key>";                    // MaiAgent API 金鑰
public static string KNOWLEDGE_BASE_ID = "<your-knowledge-base-id>"; // 目標知識庫 ID
public static string FILES_DIRECTORY = "C:\\path\\to\\your\\files";  // 要上傳的檔案目錄
```

### 進階設定
可調整 `UploadConfig` 參數：

```csharp
var config = new UploadConfig
{
    MaxConcurrentUploads = 10,   // 最大並發上傳數
    MaxRetries = 3,              // 失敗重試次數
    RetryDelay = 2.0,            // 重試間隔（秒）
    TimeoutSeconds = 300,        // 請求超時時間
};
```

## 使用方法

### 1. 確認相依套件已安裝

本專案需要的 NuGet 套件已在 [MaiAgentExamples.csproj](../../MaiAgentExamples.csproj) 中包含：

```xml
<PackageReference Include="RestSharp" Version="112.1.0" />
<PackageReference Include="Microsoft.Extensions.Http" Version="8.0.1" />
<PackageReference Include="System.Net.ServerSentEvents" Version="9.0.0" />
```

確認套件已還原：

```bash
cd examples/csharp
dotnet restore
```

### 2. 設定參數

編輯 `batch_upload_advanced.cs`，填入您的 API 金鑰、知識庫 ID 和檔案目錄路徑。

### 3. 執行上傳

**方法 1：修改 Program.cs**

編輯 [../../Program.cs](../../Program.cs)：

```csharp
static async Task Main(string[] args)
{
    await MaiAgentExamples.Knowledges.BatchUpload.BatchUploadAdvanced.Main(args);
}
```

然後執行：

```bash
cd examples/csharp
dotnet run
```

**方法 2：使用 dotnet script（需安裝 dotnet-script）**

```bash
# 安裝 dotnet-script
dotnet tool install -g dotnet-script

# 執行批量上傳
cd examples/csharp/knowledges/batch_upload
dotnet script batch_upload_advanced.cs
```

### 4. 監控進度

程式會顯示進度資訊：

```
Uploading files: 1500/10000 15% [02:30<14:10, 8.5files/s]
```

### 5. 處理中斷

如果程式被中斷（Ctrl+C 或其他原因），再次執行即可從斷點繼續：

```bash
dotnet run
```

程式會自動載入 checkpoint 並跳過已完成的檔案。

### 6. 檔案狀態管理（可選）

#### 掃描檔案狀態

修改 Program.cs：

```csharp
await MaiAgentExamples.Knowledges.BatchUpload.ScanFileStatus.Main(args);
```

執行：

```bash
dotnet run
```

掃描知識庫中所有檔案的狀態，識別 initial、processing、failed 狀態的檔案。

#### 修復失敗檔案

修改 Program.cs：

```csharp
await MaiAgentExamples.Knowledges.BatchUpload.FixFailedFiles.Main(args);
```

執行：

```bash
dotnet run
```

自動刪除失敗狀態的檔案並重新上傳。需要先執行狀態掃描生成報告。

#### 清理重複檔案

修改 Program.cs：

```csharp
await MaiAgentExamples.Knowledges.BatchUpload.DeleteDuplicateFiles.Main(args);
```

執行：

```bash
dotnet run
```

基於完整性檢查報告刪除重複檔案。需要先完成批量上傳生成完整性報告。

#### 補充缺失檔案

修改 Program.cs：

```csharp
await MaiAgentExamples.Knowledges.BatchUpload.UploadMissingFiles.Main(args);
```

執行：

```bash
dotnet run
```

上傳在完整性檢查中發現的缺失檔案。

## 輸出檔案說明

### Checkpoint 檔案 (`upload_checkpoint.json`)

記錄上傳進度和檔案 ID 映射，格式如下：

```json
{
  "timestamp": "2025-07-25T12:00:00.000000",
  "completed_files": [
    "C:\\path\\to\\file1.json",
    "C:\\path\\to\\file2.json"
  ],
  "file_id_mapping": {
    "C:\\path\\to\\file1.json": "knowledge-file-id-1",
    "C:\\path\\to\\file2.json": "knowledge-file-id-2"
  },
  "failed_files": [
    ["C:\\path\\to\\failed_file.json", "Connection timeout"]
  ],
  "pending_files": [
    "C:\\path\\to\\pending_file.json"
  ]
}
```

### 日誌檔案 (`upload_log_*.log`)

詳細記錄所有操作過程，包括：
- 程式啟動和設定資訊
- 檔案掃描結果
- 上傳進度更新
- 錯誤訊息和重試記錄
- 完整性檢查結果
- 最終統計結果

### 上傳報告檔案 (`upload_report_*.json`)

完整的上傳統計報告：

```json
{
  "summary": {
    "total_files": 10000,
    "successful_uploads": 9850,
    "failed_uploads": 150,
    "average_upload_time": 1.25
  },
  "successful_files": [
    {
      "file_path": "C:\\path\\to\\file.json",
      "file_size": 2048,
      "upload_time": 1.2
    }
  ],
  "failed_files": [
    {
      "file_path": "C:\\path\\to\\failed.json",
      "error": "Connection timeout",
      "retry_count": 3
    }
  ]
}
```

### 完整性檢查報告 (`integrity_check_*.json`)

上傳完成後的完整性驗證報告：

```json
{
  "timestamp": "2025-07-25T12:00:00.000000",
  "summary": {
    "total_kb_files": 10000,
    "total_uploaded_files": 9850,
    "total_uploaded_ids": 9850,
    "missing": 5,
    "extra": 150
  },
  "missing_files": [
    {
      "filename": "missing_file.json",
      "filepath": "C:\\path\\to\\missing_file.json",
      "knowledge_file_id": "missing-id-123"
    }
  ],
  "extra_files": [
    {
      "filename": "extra_file.json",
      "knowledge_file_id": "extra-id-456",
      "created_at": "2025-07-25T10:30:00"
    }
  ]
}
```

## 效能調優建議

### 網路環境良好

```csharp
var config = new UploadConfig
{
    MaxConcurrentUploads = 20,
    MaxRetries = 3,
    RetryDelay = 1.0,
    TimeoutSeconds = 180,
};
```

### 網路環境一般

```csharp
var config = new UploadConfig
{
    MaxConcurrentUploads = 10,
    MaxRetries = 5,
    RetryDelay = 2.0,
    TimeoutSeconds = 300,
};
```

### 網路環境較差

```csharp
var config = new UploadConfig
{
    MaxConcurrentUploads = 5,
    MaxRetries = 5,
    RetryDelay = 5.0,
    TimeoutSeconds = 600,
};
```

## 常見問題

### Q: 程式運行中可以中斷嗎？
A: 可以。使用 Ctrl+C 中斷程式會觸發優雅關閉，自動儲存當前進度和檔案 ID 映射。

### Q: 如何處理大量失敗的檔案？
A: 檢查日誌檔案了解失敗原因，調整網路設定或重試參數後重新運行。

### Q: 完整性檢查發現 missing files 怎麼辦？
A: Missing files 可能是上傳後被刪除或上傳失敗。檢查完整性報告中的具體檔案，可以重新上傳這些檔案。

### Q: 如何處理 extra files？
A: Extra files 可能是重複上傳或透過其他方式上傳的檔案。可以根據檔案名稱和創建時間判斷是否需要刪除。

### Q: 可以同時上傳到不同的知識庫嗎？
A: 需要分別執行程式，每次指定不同的知識庫 ID。程式會自動為不同的知識庫創建獨立的輸出目錄。

### Q: 支援哪些檔案格式？
A: 程式本身不限制檔案格式，但 MaiAgent 知識庫可能對特定格式有要求。建議參考 MaiAgent 官方文件。

### Q: 如何查看詳細的錯誤資訊？
A: 檢查 `logs/` 目錄下的日誌檔案，包含所有詳細的錯誤訊息和堆疊追蹤。

### Q: 批量上傳後發現有失敗檔案，如何處理？
A: 使用以下流程：
1. 先執行 `scan_file_status.cs` 掃描檔案狀態
2. 再執行 `fix_failed_files.cs` 自動修復失敗檔案

### Q: 完整性檢查發現重複檔案，如何清理？
A: 執行 `delete_duplicate_files.cs`，程式會基於完整性檢查報告安全地刪除重複檔案。

### Q: 需要補充上傳一些遺漏的檔案，如何操作？
A: 執行 `upload_missing_files.cs`，程式會根據完整性檢查報告上傳缺失的檔案。

### Q: 檔案狀態管理工具的執行順序？
A: 建議順序：
1. `scan_file_status.cs` - 掃描並生成狀態報告
2. `fix_failed_files.cs` - 修復失敗檔案（如果有）
3. `delete_duplicate_files.cs` - 清理重複檔案（如果需要）
4. `upload_missing_files.cs` - 補充缺失檔案（如果需要）

## 技術規格

- **.NET 版本**：.NET 8.0+
- **主要套件**：RestSharp, System.Net.Http, System.Text.Json
- **並發模型**：異步 I/O (async/await)
- **記憶體使用**：低記憶體佔用，適合處理大量檔案
- **平台支援**：跨平台 (Windows, macOS, Linux)

## 相關文檔

- [MaiAgentHelper 使用文檔](../../utils/maiagent.md)
- [知識庫 API 說明](../README.md)
- [MaiAgent API 官方文檔](https://docs.maiagent.ai/)

---

如有任何問題或建議，請聯繫開發團隊。
