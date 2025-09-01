# Knowledge Base FAQ 下載工具

這個工具可以讓您根據 Knowledge Base ID 下載所有 FAQ，並支援多種匯出格式。

## 功能特色

- ✅ **多格式支援**：JSON、CSV、Excel (.xlsx)
- ✅ **自動分頁處理**：自動處理大量 FAQ 的分頁獲取
- ✅ **詳細統計**：FAQ 數量、標籤統計、預覽功能
- ✅ **批次下載**：一次下載所有 FAQ
- ✅ **結構化數據**：保留完整的 FAQ 結構和標籤資訊
- ✅ **進度顯示**：顯示分頁獲取進度

## 使用方法

### 1. 設定 API 金鑰和知識庫 ID

編輯 `download_knowledge_base_faqs.py` 檔案：

```python
API_KEY = 'your-actual-api-key'
KNOWLEDGE_BASE_ID = 'your-knowledge-base-id'
```

### 2. 執行腳本

```bash
cd python/faqs
python download_knowledge_base_faqs.py
```

### 3. 選擇匯出格式

程式會顯示 FAQ 統計資訊，然後讓您選擇匯出格式：

```
📤 選擇導出格式：
1. JSON 格式 (.json) - 完整的結構化數據
2. CSV 格式 (.csv) - 表格數據，適合 Excel 開啟
3. Excel 格式 (.xlsx) - Excel 工作簿
4. 全部格式
5. 取消
```

## 輸出格式說明

### JSON 格式
- 包含完整的 FAQ 結構和元數據
- 適合程式處理和 API 整合
- 包含知識庫 ID、導出時間等資訊

```json
{
  "knowledge_base_id": "your-kb-id",
  "export_time": "2024-01-01T12:00:00",
  "total_faqs": 100,
  "faqs": [
    {
      "id": "faq-123",
      "question": "問題內容",
      "answer": "答案內容",
      "labels": [{"id": "label-1", "name": "標籤名稱"}],
      "created_at": "2024-01-01T10:00:00",
      "updated_at": "2024-01-01T11:00:00"
    }
  ]
}
```

### CSV 格式
- 表格形式，適合在 Excel 或 Google Sheets 中開啟
- UTF-8 編碼，支援中文顯示
- 包含：ID、問題、答案、標籤、建立時間、更新時間

### Excel 格式
- 專業的 Excel 工作簿 (.xlsx)
- 包含兩個工作表：
  - **FAQ List**：所有 FAQ 的詳細列表
  - **Statistics**：統計資訊摘要
- 格式化的表頭和自動調整欄寬

## 輸出檔案

所有匯出的檔案都會保存在 `python/downloads/` 資料夾中（絕對路徑，不受執行目錄影響），檔名格式為：
```
knowledge_base_faqs_{knowledge_base_id}_{timestamp}.{extension}
```

例如：
- `knowledge_base_faqs_abc123_20240101_120000.json`
- `knowledge_base_faqs_abc123_20240101_120000.csv`
- `knowledge_base_faqs_abc123_20240101_120000.xlsx`

## 系統需求

### 必要套件
- requests
- 標準庫：json, csv, datetime, os, sys

### Excel 功能額外需求
如果要使用 Excel 匯出功能，需要安裝：
```bash
pip install openpyxl
```

## 錯誤處理

程式包含完整的錯誤處理：
- API 金鑰驗證
- 知識庫存在性檢查
- 網路連線錯誤處理
- 檔案寫入權限檢查

## 使用範例

### 快速開始
1. 設定您的 API 金鑰和知識庫 ID
2. 執行腳本：`python download_knowledge_base_faqs.py`
3. 選擇「4. 全部格式」來獲得所有格式的輸出

### 只下載 JSON 格式
1. 執行腳本後選擇「1. JSON 格式」
2. 適合需要程式化處理 FAQ 數據的情況

### 只下載 Excel 格式
1. 執行腳本後選擇「3. Excel 格式」
2. 適合需要在 Excel 中分析和編輯 FAQ 的情況

## 分頁處理

工具已內建**自動分頁處理**功能：

- 🔄 **自動獲取所有頁面**：無論您有多少個 FAQ，工具會自動處理所有分頁
- 📊 **實時進度顯示**：顯示目前正在處理第幾頁，以及已獲取的 FAQ 總數
- ⚡ **智能分頁大小**：預設每頁獲取 100 個 FAQ，平衡效率與穩定性
- 🛡️ **錯誤恢復**：單頁失敗不會影響整體下載，會繼續處理後續頁面

### 分頁處理流程

```
正在獲取第 1 頁，已獲取 100 個 FAQ...
正在獲取第 2 頁，已獲取 200 個 FAQ...
正在獲取第 3 頁，已獲取 250 個 FAQ...
✅ 成功獲取所有 FAQ！
   總計：250 個 FAQ
```

## 注意事項

1. **API 配額**：大量 FAQ 的下載可能會消耗 API 配額，分頁處理會增加 API 調用次數
2. **處理時間**：FAQ 數量很多時，分頁獲取需要更多時間，請耐心等待
3. **檔案大小**：FAQ 數量很多時，檔案可能會比較大
4. **編碼**：所有檔案都使用 UTF-8 編碼，確保中文正確顯示
5. **備份**：建議定期使用此工具備份重要的 FAQ 數據

## 疑難排解

### 常見錯誤

**API 金鑰錯誤**
```
AssertionError: Please set your API key
```
解決：確認已正確設定 API_KEY 變數

**知識庫 ID 錯誤**
```
AssertionError: Please set your knowledge base id  
```
解決：確認已正確設定 KNOWLEDGE_BASE_ID 變數

**Excel 匯出失敗**
```
❌ 需要安裝 openpyxl 套件才能導出 Excel 格式
```
解決：執行 `pip install openpyxl`

### 獲取知識庫 ID

如果不確定您的知識庫 ID，可以使用：
```bash
python ../knowledges/list_knowledge_bases.py
```

這將列出您帳戶下的所有知識庫及其 ID。

## 大量數據處理建議

當您的知識庫包含大量 FAQ 時（超過 1000 個），建議：

1. **選擇合適時間**：在網路穩定的時候執行，避免高峰時段
2. **監控進度**：工具會顯示實時進度，請耐心等待
3. **分批處理**：如果一次性下載失敗，可以考慮分多次處理
4. **檢查結果**：下載完成後檢查統計數字是否符合預期

### 效能參考

- **小型知識庫**（< 100 FAQ）：通常 10-30 秒完成
- **中型知識庫**（100-500 FAQ）：通常 1-3 分鐘完成  
- **大型知識庫**（500-2000 FAQ）：通常 3-10 分鐘完成
- **超大型知識庫**（> 2000 FAQ）：可能需要 10 分鐘以上
