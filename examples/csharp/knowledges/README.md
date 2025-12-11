# 知識庫 API 使用範例

本資料夾包含了使用 MaiAgent 知識庫 API 的各種範例程式碼。

## 概述

知識庫 API 提供了完整的知識管理功能，包括：
- 知識庫的 CRUD 操作
- 檔案上傳和管理
- 標籤系統
- FAQ 管理
- 內容搜尋
- 批次操作

## 檔案說明

本目錄包含 **17個** 知識庫相關程式碼範例，涵蓋完整的知識庫管理功能：

### 🎯 基本操作（4個）
1. **`create_knowledge_base.cs`** - 建立新的知識庫
2. **`list_knowledge_bases.cs`** - 列出所有知識庫
3. **`upload_knowledge_file.cs`** - 上傳檔案到知識庫
4. **`delete_knowledge_file.cs`** - 刪除知識庫中的檔案

### 🔍 搜尋功能（1個）
5. **`search_knowledge_base.cs`** - 搜尋知識庫內容

### 🛠️ 進階管理（3個）
6. **`manage_knowledge_base_labels.cs`** - 管理知識庫標籤
7. **`manage_knowledge_base_faq.cs`** - 管理知識庫 FAQ
8. **`manage_knowledge_base_files.cs`** - 管理知識庫檔案（包括批次操作）

### 🚀 批量上傳工具（1個）
9. **`batch_upload/`** - 高效能批量檔案上傳工具
   - 支援異步並發上傳，大幅提升上傳速度
   - 自動斷點續傳，程式中斷後可繼續
   - 完整性檢查，自動驗證上傳結果
   - 視覺化進度追蹤，使用 tqdm 進度條

### 📊 檔案狀態管理工具（4個）
10. **`scan_file_status.cs`** - 掃描知識庫檔案狀態
    - 識別 initial、processing、failed 狀態的檔案
    - 生成詳細的狀態分析報告
11. **`delete_duplicate_files.cs`** - 刪除重複檔案
    - 基於完整性檢查報告刪除多餘檔案
    - 安全確認機制和詳細日誌
12. **`fix_failed_files.cs`** - 修復失敗檔案
    - 自動刪除失敗狀態的檔案並重新上傳
    - 異步高效能重新上傳機制
13. **`upload_missing_files.cs`** - 上傳缺失檔案
    - 補充上傳遺漏的檔案
    - 智慧檔案路徑查找

### 🌟 綜合範例（1個）
14. **`comprehensive_knowledge_base_example.cs`** - 完整的知識庫操作流程示範

## 📊 快速參考表

| 編號 | 檔案名稱 | 主要功能 | 必要參數 | 執行命令 |
|------|---------|---------|----------|----------|
| 1️⃣ | `create_knowledge_base.cs` | 創建知識庫 | API_KEY | 修改 Program.cs 後執行 `dotnet run` |
| 2️⃣ | `list_knowledge_bases.cs` | 列出知識庫 | API_KEY | 修改 Program.cs 後執行 `dotnet run` |
| 3️⃣ | `upload_knowledge_file.cs` | 上傳檔案 | API_KEY, KB_ID, FILE_PATH | 修改 Program.cs 後執行 `dotnet run` |
| 4️⃣ | `delete_knowledge_file.cs` | 刪除檔案 | API_KEY, KB_ID, FILE_ID | 修改 Program.cs 後執行 `dotnet run` |
| 5️⃣ | `search_knowledge_base.cs` | 搜尋內容 | API_KEY, KB_ID, QUERY | 修改 Program.cs 後執行 `dotnet run` |
| 6️⃣ | `manage_knowledge_base_labels.cs` | 管理標籤 | API_KEY, KB_ID | 修改 Program.cs 後執行 `dotnet run` |
| 7️⃣ | `manage_knowledge_base_faq.cs` | 管理 FAQ | API_KEY, KB_ID | 修改 Program.cs 後執行 `dotnet run` |
| 8️⃣ | `manage_knowledge_base_files.cs` | 檔案管理 | API_KEY, KB_ID | 修改 Program.cs 後執行 `dotnet run` |
| 9️⃣ | `batch_upload/` | **批量上傳工具** | API_KEY, KB_ID, FILES_DIR | 修改 Program.cs 後執行 `dotnet run` |
| 🔟 | `scan_file_status.cs` | **檔案狀態掃描** | API_KEY, KB_ID | 修改 Program.cs 後執行 `dotnet run` |
| 1️⃣1️⃣ | `delete_duplicate_files.cs` | **刪除重複檔案** | API_KEY, KB_ID, REPORT_PATH | 修改 Program.cs 後執行 `dotnet run` |
| 1️⃣2️⃣ | `fix_failed_files.cs` | **修復失敗檔案** | API_KEY, KB_ID, FILES_DIR, REPORT_PATH | 修改 Program.cs 後執行 `dotnet run` |
| 1️⃣3️⃣ | `upload_missing_files.cs` | **上傳缺失檔案** | API_KEY, KB_ID, FILES_DIR, REPORT_PATH | 修改 Program.cs 後執行 `dotnet run` |
| 1️⃣4️⃣ | `comprehensive_knowledge_base_example.cs` | 綜合示範 | API_KEY | 修改 Program.cs 後執行 `dotnet run` |

> **說明**：KB_ID = KNOWLEDGE_BASE_ID

## 使用方法

1. **設定 API Key**
   ```csharp
   public static string API_KEY = "<your-api-key>";
   ```

2. **建立知識庫**
   ```csharp
   using Utils;

   var maiagentHelper = new MaiAgentHelper(API_KEY);
   var response = await maiagentHelper.create_knowledge_base(
       name: "我的知識庫",
       description: "知識庫描述",
       embeddingModel: "your-embedding-model-id",
       rerankerModel: "your-reranker-model-id",
       numberOfRetrievedChunks: 12,
       sentenceWindowSize: 2,
       enableHyde: false,
       similarityCutoff: 0.0,
       enableRerank: true
   );
   ```

3. **上傳檔案**
   ```csharp
   // 注意：第一個參數名稱為 chatbotId，但實際上傳遞知識庫 ID
   var uploadResponse = await maiagentHelper.upload_knowledge_file(
       chatbotId: KB_ID,
       filePath: "path/to/your/file.pdf"
   );
   ```

4. **創建標籤**
   ```csharp
   var labelResponse = await maiagentHelper.create_knowledge_base_label(
       knowledgeBaseId: KB_ID,
       name: "技術文檔"
   );
   ```

5. **創建 FAQ**
   ```csharp
   var labels = new List<Dictionary<string, string>>
   {
       new Dictionary<string, string> { {"id", "label-id-1"}, {"name", "標籤名稱1"} },
       new Dictionary<string, string> { {"id", "label-id-2"}, {"name", "標籤名稱2"} }
   };

   var faqResponse = await maiagentHelper.create_knowledge_base_faq(
       knowledgeBaseId: KB_ID,
       question: "常見問題",
       answer: "問題的答案",
       labels: labels  // 可選參數，格式為 [{"id": "...", "name": "..."}]
   );
   ```

6. **搜尋內容**
   ```csharp
   var results = await maiagentHelper.search_knowledge_base(
       knowledgeBaseId: KB_ID,
       query: "搜尋關鍵字"
   );
   ```

## API 參數說明

### 知識庫建立參數
- `name` (必填): 知識庫名稱
- `description` (可選): 知識庫描述
- `embeddingModel` (可選): 嵌入模型 ID - **建議設定，否則上傳之檔案將無法正確解析**
- `rerankerModel` (可選): 重新排序模型 ID - **建議設定，才能夠啟用 rerank 模型**
- `numberOfRetrievedChunks` (可選): 檢索的文件塊數量 (預設: 12)
- `sentenceWindowSize` (可選): 句子視窗大小 (預設: 2)
- `enableHyde` (可選): 啟用 HyDE (預設: false)
- `similarityCutoff` (可選): 相似度門檻 (預設: 0.0)
- `enableRerank` (可選): 啟用重新排序 (預設: true)
- `chatbots` (可選): 關聯的聊天機器人列表

### 搜尋參數
- `query` (必填): 搜尋查詢字串
- `knowledgeBaseId` (必填): 知識庫 ID

### 標籤管理
- `knowledgeBaseId` (必填): 知識庫 ID
- `name` (必填): 標籤名稱

### FAQ 管理
- `knowledgeBaseId` (必填): 知識庫 ID
- `question` (必填): 問題
- `answer` (必填): 答案
- `labels` (可選): 標籤 ID 列表

## 錯誤處理

所有範例都包含了適當的錯誤處理：

```csharp
try
{
    var response = await maiagentHelper.create_knowledge_base(...);
    Console.WriteLine($"操作成功：{response}");
}
catch (Exception ex)
{
    Console.WriteLine($"操作失敗：{ex.Message}");
}
```

## 注意事項

1. 確保在使用前設定正確的 API Key
2. 知識庫 ID 和其他 ID 必須是有效的 UUID
3. 檔案上傳需要指定實際存在的檔案路徑
4. 知識庫需要設定好 EMBEDDING_MODEL 與 RERANKER_MODEL 才能讓模型正確處理上傳之檔案
5. 批次操作可能需要較長的處理時間
6. 刪除操作是不可逆的，請謹慎使用
7. 檔案上傳後需要等待模型處理完成才能進行搜尋

## 支援的檔案格式

- PDF 文件
- Word 文件 (.docx)
- 純文字檔案 (.txt)
- Markdown 檔案 (.md)
- Excel 檔案 (.xlsx)
- 其他常見文件格式

## 進階功能

### 批次操作
- 批量檔案上傳（參見 `batch_upload/` 範例）
- 批次刪除檔案
- 批次重新解析檔案

### 元數據管理
- 檔案元數據更新
- FAQ 元數據更新
- 標籤系統

### 搜尋功能
- 語意搜尋
- 相似度評分
- 結果排序

## 📋 詳細使用指南

### 🚀 快速開始

**第一次使用建議順序：**

```bash
# 進入 csharp 目錄
cd maiagent-api-examples/examples/csharp

# 1. 查看現有知識庫
# 編輯 Program.cs，在 Main 方法中呼叫：
# await MaiAgentExamples.Knowledges.ListKnowledgeBases.Main(args);
dotnet run

# 2. 創建新知識庫
# 編輯 Program.cs，在 Main 方法中呼叫：
# await MaiAgentExamples.Knowledges.CreateKnowledgeBase.Main(args);
dotnet run

# 3. 上傳檔案（單個檔案）
# 編輯 Program.cs，在 Main 方法中呼叫：
# await MaiAgentExamples.Knowledges.UploadKnowledgeFile.Main(args);
dotnet run

# 4. 批量上傳檔案（推薦用於大量檔案）
# 編輯 Program.cs，在 Main 方法中呼叫：
# await MaiAgentExamples.Knowledges.BatchUpload.BatchUploadAdvanced.Main(args);
dotnet run

# 5. 創建標籤
# 編輯 Program.cs，在 Main 方法中呼叫：
# await MaiAgentExamples.Knowledges.ManageKnowledgeBaseLabels.Main(args);
dotnet run

# 6. 搜尋內容
# 編輯 Program.cs，在 Main 方法中呼叫：
# await MaiAgentExamples.Knowledges.SearchKnowledgeBase.Main(args);
dotnet run
```

### 📝 各檔案詳細說明

#### 1️⃣ `create_knowledge_base.cs` - 建立知識庫

**功能**：創建新的知識庫並設定各種參數

**使用前需要設定**：
- `API_KEY`：您的 MaiAgent API Key
- `KNOWLEDGE_BASE_NAME`：知識庫名稱
- `KNOWLEDGE_BASE_DESCRIPTION`：知識庫描述

**執行**：
```csharp
// 編輯 Program.cs，在 Main 方法中呼叫：
await MaiAgentExamples.Knowledges.CreateKnowledgeBase.Main(args);
```
```bash
cd examples/csharp
dotnet run
```

**輸出**：知識庫 ID、名稱、描述等資訊

---

#### 2️⃣ `list_knowledge_bases.cs` - 列出知識庫

**功能**：列出當前帳戶下的所有知識庫

**使用前需要設定**：
- `API_KEY`：您的 MaiAgent API Key

**執行**：
```csharp
// 編輯 Program.cs，在 Main 方法中呼叫：
await MaiAgentExamples.Knowledges.ListKnowledgeBases.Main(args);
```
```bash
cd examples/csharp
dotnet run
```

**輸出**：所有知識庫的詳細資訊列表

---

#### 3️⃣ `upload_knowledge_file.cs` - 上傳檔案

**功能**：上傳檔案到指定知識庫

**使用前需要設定**：
- `API_KEY`：您的 MaiAgent API Key
- `KNOWLEDGE_BASE_ID`：目標知識庫 ID
- `FILE_PATH`：要上傳的檔案路徑

**執行**：
```csharp
// 編輯 Program.cs，在 Main 方法中呼叫：
await MaiAgentExamples.Knowledges.UploadKnowledgeFile.Main(args);
```
```bash
cd examples/csharp
dotnet run
```

**輸出**：上傳成功的檔案資訊

---

#### 4️⃣ `delete_knowledge_file.cs` - 刪除檔案

**功能**：從知識庫中刪除指定檔案

**使用前需要設定**：
- `API_KEY`：您的 MaiAgent API Key
- `KNOWLEDGE_BASE_ID`：知識庫 ID
- `FILE_ID`：要刪除的檔案 ID

**執行**：
```csharp
// 編輯 Program.cs，在 Main 方法中呼叫：
await MaiAgentExamples.Knowledges.DeleteKnowledgeFile.Main(args);
```
```bash
cd examples/csharp
dotnet run
```

**輸出**：刪除操作的成功或失敗訊息

---

#### 5️⃣ `search_knowledge_base.cs` - 搜尋內容

**功能**：在知識庫中搜尋相關內容

**使用前需要設定**：
- `API_KEY`：您的 MaiAgent API Key
- `KNOWLEDGE_BASE_ID`：知識庫 ID
- `SEARCH_QUERY`：搜尋關鍵字

**執行**：
```csharp
// 編輯 Program.cs，在 Main 方法中呼叫：
await MaiAgentExamples.Knowledges.SearchKnowledgeBase.Main(args);
```
```bash
cd examples/csharp
dotnet run
```

**輸出**：搜尋結果列表，包含相似度分數

---

#### 6️⃣ `manage_knowledge_base_labels.cs` - 管理標籤

**功能**：創建、列出、更新、刪除知識庫標籤

**使用前需要設定**：
- `API_KEY`：您的 MaiAgent API Key
- `KNOWLEDGE_BASE_ID`：知識庫 ID

**執行**：
```csharp
// 編輯 Program.cs，在 Main 方法中呼叫：
await MaiAgentExamples.Knowledges.ManageKnowledgeBaseLabels.Main(args);
```
```bash
cd examples/csharp
dotnet run
```

**功能包含**：
- 創建新標籤（自動生成唯一名稱）
- 列出所有標籤
- 更新標籤名稱
- 獲取標籤詳情
- 刪除標籤

---

#### 7️⃣ `manage_knowledge_base_faq.cs` - 管理 FAQ

**功能**：管理知識庫的常見問題

**使用前需要設定**：
- `API_KEY`：您的 MaiAgent API Key
- `KNOWLEDGE_BASE_ID`：知識庫 ID

**執行**：
```csharp
// 編輯 Program.cs，在 Main 方法中呼叫：
await MaiAgentExamples.Knowledges.ManageKnowledgeBaseFaq.Main(args);
```
```bash
cd examples/csharp
dotnet run
```

**功能包含**：
- 創建 FAQ（支援標籤）
- 列出所有 FAQ
- 更新 FAQ 內容（支援標籤）
- 獲取 FAQ 詳情
- 刪除 FAQ

---

#### 8️⃣ `manage_knowledge_base_files.cs` - 管理檔案

**功能**：進階檔案管理，包括批次操作

**使用前需要設定**：
- `API_KEY`：您的 MaiAgent API Key
- `KNOWLEDGE_BASE_ID`：知識庫 ID

**執行**：
```csharp
// 編輯 Program.cs，在 Main 方法中呼叫：
await MaiAgentExamples.Knowledges.ManageKnowledgeBaseFiles.Main(args);
```
```bash
cd examples/csharp
dotnet run
```

**功能包含**：
- 列出所有檔案
- 獲取檔案詳情
- 更新檔案元數據
- 批次刪除檔案
- 批次重新解析檔案

---

#### 9️⃣ `batch_upload/` - 批量上傳工具

**功能**：高效能批量檔案上傳，適合大量檔案的場景

**主要特色**：
- ⚡ **異步並發上傳**：同時處理多個檔案，大幅提升速度
- 🔄 **自動斷點續傳**：程式中斷後可從上次停止位置繼續
- 📊 **視覺化進度**：使用 tqdm 進度條顯示即時進度
- 🔍 **完整性檢查**：自動驗證上傳結果，識別漏傳檔案
- 📝 **詳細報告**：生成完整的上傳統計和錯誤報告

**使用前需要設定**：
- `API_KEY`：您的 MaiAgent API Key
- `KNOWLEDGE_BASE_ID`：目標知識庫 ID
- `FILES_DIRECTORY`：要上傳的檔案目錄

**安裝依賴**：

本專案已在 [MaiAgentExamples.csproj](../../MaiAgentExamples.csproj) 中包含所有必要的 NuGet 套件。

**執行**：
```csharp
// 編輯 Program.cs，在 Main 方法中呼叫：
await MaiAgentExamples.Knowledges.BatchUpload.BatchUploadAdvanced.Main(args);
```
```bash
cd examples/csharp
dotnet run
```

**適用場景**：
- 需要上傳數百或數千個檔案
- 網路不穩定環境下的大量上傳
- 需要進度追蹤和錯誤報告的批量操作

**效能優勢**：
- 相比單檔案上傳，速度提升 10-50 倍
- 自動重試失敗的檔案
- 智慧並發控制，避免服務器過載

詳細使用說明請參考 [`batch_upload/README.md`](batch_upload/README.md)

---

#### 1️⃣1️⃣ `fix_failed_files.cs` - 修復失敗檔案

**功能**：自動修復知識庫中狀態為 'failed' 的檔案

**主要特色**：
- 🔍 **智慧檢測**：基於狀態掃描報告識別失敗檔案
- 🗑️ **安全刪除**：自動刪除失敗狀態的檔案
- ⚡ **異步重新上傳**：使用高效能異步機制重新上傳
- 📊 **詳細追蹤**：記錄完整的修復過程和結果

**使用前需要設定**：
- `API_KEY`：您的 MaiAgent API Key
- `KNOWLEDGE_BASE_ID`：知識庫 ID
- `FILES_DIRECTORY`：原始檔案所在目錄
- `STATUS_REPORT_PATH`：狀態掃描報告路徑

**執行**：
```csharp
// 編輯 Program.cs，在 Main 方法中呼叫：
await MaiAgentExamples.Knowledges.BatchUpload.FixFailedFiles.Main(args);
```
```bash
cd examples/csharp
dotnet run
```

**工作流程**：
1. 讀取狀態掃描報告中的失敗檔案
2. 從知識庫中刪除這些失敗檔案
3. 從本地目錄重新上傳檔案
4. 生成詳細的修復日誌

**適用場景**：
- 批量上傳後有部分檔案狀態為 'failed'
- 需要自動化修復失敗檔案的流程
- 確保知識庫中所有檔案都處於正常狀態

---

#### 1️⃣2️⃣ `upload_missing_files.cs` - 上傳缺失檔案

**功能**：上傳基於完整性檢查報告識別的缺失檔案

**使用前需要設定**：
- `API_KEY`：您的 MaiAgent API Key
- `KNOWLEDGE_BASE_ID`：知識庫 ID
- `FILES_DIRECTORY`：檔案目錄
- `INTEGRITY_REPORT_PATH`：完整性檢查報告路徑

**執行**：
```csharp
// 編輯 Program.cs，在 Main 方法中呼叫：
await MaiAgentExamples.Knowledges.BatchUpload.UploadMissingFiles.Main(args);
```
```bash
cd examples/csharp
dotnet run
```

**輸出**：補充上傳缺失檔案的結果報告

---

#### 1️⃣3️⃣ `delete_duplicate_files.cs` - 刪除重複檔案

**功能**：刪除基於完整性檢查報告識別的重複檔案

**使用前需要設定**：
- `API_KEY`：您的 MaiAgent API Key
- `KNOWLEDGE_BASE_ID`：知識庫 ID
- `INTEGRITY_REPORT_PATH`：完整性檢查報告路徑

**執行**：
```csharp
// 編輯 Program.cs，在 Main 方法中呼叫：
await MaiAgentExamples.Knowledges.BatchUpload.DeleteDuplicateFiles.Main(args);
```
```bash
cd examples/csharp
dotnet run
```

**安全特性**：
- 顯示將要刪除的檔案列表
- 需要明確確認（輸入 'YES'）才執行
- 生成詳細的刪除日誌

---

#### 1️⃣4️⃣ `comprehensive_knowledge_base_example.cs` - 綜合範例

**功能**：展示完整的知識庫操作流程

**使用前需要設定**：
- `API_KEY`：您的 MaiAgent API Key

**執行**：
```csharp
// 編輯 Program.cs，在 Main 方法中呼叫：
await MaiAgentExamples.Knowledges.ComprehensiveKnowledgeBaseExample.Main(args);
```
```bash
cd examples/csharp
dotnet run
```

**流程包含**：
1. 創建知識庫
2. 創建標籤
3. 創建 FAQ
4. 搜尋內容
5. 查看詳情
6. 列出資源
7. 清理操作（可選，取消註解以執行）

### ⚙️ 設定檔案

**重要**：在執行任何範例前，請確保設定正確的參數：

1. **API Key**：所有檔案都需要設定您的 MaiAgent API Key
2. **知識庫 ID**：使用 `list_knowledge_bases.cs` 獲取現有知識庫 ID
3. **檔案路徑**：確保檔案路徑存在且可讀取

### 🔄 建議執行順序

**完整工作流程**：

```bash
# 進入 csharp 目錄
cd maiagent-api-examples/examples/csharp

# 步驟 1：查看現有資源
# 編輯 Program.cs，在 Main 方法中呼叫：
# await MaiAgentExamples.Knowledges.ListKnowledgeBases.Main(args);
dotnet run

# 步驟 2：創建新知識庫（可選）
# 編輯 Program.cs，在 Main 方法中呼叫：
# await MaiAgentExamples.Knowledges.CreateKnowledgeBase.Main(args);
dotnet run

# 步驟 3：上傳檔案
# 單個檔案上傳
# 編輯 Program.cs，在 Main 方法中呼叫：
# await MaiAgentExamples.Knowledges.UploadKnowledgeFile.Main(args);
dotnet run

# 大量檔案批量上傳（推薦）
# 編輯 Program.cs，在 Main 方法中呼叫：
# await MaiAgentExamples.Knowledges.BatchUpload.BatchUploadAdvanced.Main(args);
dotnet run

# 步驟 4：創建標籤分類
# 編輯 Program.cs，在 Main 方法中呼叫：
# await MaiAgentExamples.Knowledges.ManageKnowledgeBaseLabels.Main(args);
dotnet run

# 步驟 5：添加 FAQ
# 編輯 Program.cs，在 Main 方法中呼叫：
# await MaiAgentExamples.Knowledges.ManageKnowledgeBaseFaq.Main(args);
dotnet run

# 步驟 6：等待檔案處理完成後搜尋
# 編輯 Program.cs，在 Main 方法中呼叫：
# await MaiAgentExamples.Knowledges.SearchKnowledgeBase.Main(args);
dotnet run

# 步驟 7：檔案管理
# 編輯 Program.cs，在 Main 方法中呼叫：
# await MaiAgentExamples.Knowledges.ManageKnowledgeBaseFiles.Main(args);
dotnet run

# 步驟 8：綜合測試
# 編輯 Program.cs，在 Main 方法中呼叫：
# await MaiAgentExamples.Knowledges.ComprehensiveKnowledgeBaseExample.Main(args);
dotnet run
```

### 🚨 常見問題

1. **編譯錯誤**：
   ```bash
   # 確保在 examples/csharp 目錄中執行
   cd maiagent-api-examples/examples/csharp
   dotnet restore
   dotnet build
   ```

2. **知識庫 ID 不一致**：
   - 使用 `list_knowledge_bases.cs` 獲取正確的 ID
   - 確保所有檔案使用相同的知識庫 ID

3. **標籤重複錯誤**：
   - 標籤名稱在同一知識庫中必須唯一
   - 使用時間戳或其他方式生成唯一名稱

4. **搜尋失敗**：
   - 確保知識庫中有已處理完成的檔案
   - 檔案上傳後需要等待處理時間

5. **檔案解析失敗**：
   - 檢查是否已設定 EMBEDDING_MODEL
   - 確認模型 ID 是否正確
   - 檢查模型是否可用

6. **API 錯誤**：
   - 檢查 API Key 是否正確
   - 確認網路連接正常
   - 查看 API 限制和配額

## 疑難排解

如果遇到問題，請檢查：
1. API Key 是否正確
2. 知識庫 ID 是否存在
3. 檔案路徑是否正確
4. 網路連線是否正常
5. 請求參數是否符合 API 規範
6. 是否在正確的目錄中執行命令

如需更多協助，請參考 MaiAgent 官方文檔或聯絡技術支援。 
