# FAQ Excel 批量上傳工具

這個工具可以讓您從 Excel 檔案批量上傳 FAQ 到指定的知識庫。

## 功能特色

- ✅ **Excel 檔案支援**：讀取 .xlsx 格式的 Excel 檔案
- ✅ **智能欄位識別**：自動識別 Question/Answer/Labels 欄位（支援中英文）
- ✅ **批量上傳**：一次上傳多個 FAQ，提高效率
- ✅ **標籤支援**：支援為 FAQ 添加多個標籤（用逗號分隔）
- ✅ **錯誤處理**：完整的錯誤處理和進度顯示
- ✅ **詳細報告**：生成上傳結果報告，包含成功和失敗的詳細信息
- ✅ **資料驗證**：檢查必要欄位，跳過無效數據

## 使用前準備

### 1. 安裝依賴套件

```bash
pip install openpyxl
```

### 2. 設定 API 金鑰和知識庫 ID

編輯 `upload_faqs_from_excel.py` 檔案：

```python
API_KEY = 'your-actual-api-key'
KNOWLEDGE_BASE_ID = 'your-knowledge-base-id'
EXCEL_FILE_PATH = 'path/to/your/excel/file.xlsx'
```

### 3. 準備 Excel 檔案

您的 Excel 檔案需要包含以下欄位：

| 欄位名稱 | 說明 | 必填 | 範例 |
|---------|------|------|------|
| Question 或 問題 | FAQ 的問題內容 | ✅ 是 | 如何重設密碼？ |
| Answer 或 答案 | FAQ 的答案內容 | ✅ 是 | 請到登入頁面點擊「忘記密碼」 |
| Labels 或 標籤 | FAQ 的標籤，用逗號分隔 | ❌ 否 | 登入,密碼 |

## Excel 檔案格式

### 支援的欄位名稱

程式會自動識別以下欄位名稱（不分大小寫）：

- **Question 欄位**：question, q, 問題, 問
- **Answer 欄位**：answer, a, 答案, 答, 回答
- **Labels 欄位**：labels, tags, label, tag, 標籤, 標記

### Excel 檔案範例

```
| Question                | Answer                                    | Labels    |
|------------------------|-------------------------------------------|-----------|
| 如何重設密碼？           | 請到登入頁面點擊「忘記密碼」，然後按照指示操作。 | 登入,密碼  |
| 營業時間是什麼時候？      | 我們的營業時間是週一到週五 9:00-18:00        | 時間,營業  |
| 如何聯繫客服？           | 您可以撥打客服專線 02-1234-5678             | 客服,聯繫  |
```

## 使用方法

### 1. 執行腳本

```bash
cd python/faqs
python upload_faqs_from_excel.py
```

### 2. 查看執行過程

程式會顯示以下信息：

```
============================================================
MaiAgent FAQ Excel 批量上傳工具
============================================================

📖 正在讀取 Excel 檔案：your_file.xlsx
📋 找到的欄位：['question', 'answer', 'labels']
✅ 欄位對應：Question=1, Answer=2, Labels=3
✅ 成功讀取 10 個 FAQ

📝 FAQ 預覽（前 3 個）：
   1. Q: 如何重設密碼？
      A: 請到登入頁面點擊「忘記密碼」，然後按照指示操作。
      標籤: 登入, 密碼
      來源: 第 2 行

❓ 確認要上傳 10 個 FAQ 嗎？
注意：這個操作會調用 API 新增 FAQ，可能會消耗 API 配額
繼續上傳？(y/N):
```

### 3. 查看上傳結果

```
🚀 開始批量上傳 10 個 FAQ...
==================================================
[  1/10] 正在上傳: 如何重設密碼？
         ✅ 成功 (ID: abc12345...)
[  2/10] 正在上傳: 營業時間是什麼時候？
         ✅ 成功 (ID: def67890...)
...

==================================================
📊 上傳結果統計
==================================================
總計 FAQ：10
成功上傳：9 ✅
上傳失敗：1 ❌
成功率：90.0%
耗時：15.2 秒

📄 詳細報告已保存到：/path/to/downloads/faq_upload_report_20240101_120000.txt
```

## 輸出檔案

### 上傳報告

程式會在 `python/downloads/` 目錄下生成詳細的上傳報告：

- 檔名格式：`faq_upload_report_YYYYMMDD_HHMMSS.txt`
- 包含成功上傳的 FAQ 列表
- 包含失敗的 FAQ 及錯誤原因
- 統計資訊和執行時間

## 錯誤處理

### 常見錯誤

**Excel 檔案格式錯誤**
```
❌ 找不到包含 FAQ 數據的工作表
```
解決：確保 Excel 檔案包含名為 "FAQ List"、"FAQs" 或 "Sheet1" 的工作表

**缺少必要欄位**
```
❌ 找不到必要的欄位。需要包含 'Question' 和 'Answer' 欄位
```
解決：確認 Excel 檔案的第一行包含 Question 和 Answer 欄位

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

## 注意事項

1. **Excel 檔案格式**：目前僅支援 .xlsx 格式
2. **編碼支援**：完全支援中文內容和欄位名稱
3. **API 配額**：大量 FAQ 上傳會消耗 API 配額
4. **處理時間**：上傳速度取決於 FAQ 數量和網路狀況
5. **標籤處理**：程式會自動處理標籤格式，不需要預先創建標籤
6. **資料驗證**：空白行和不完整的資料會自動跳過
7. **重複檢查**：程式不會檢查重複的 FAQ，請手動確認

## 進階使用

### 批量標籤管理

如果您需要統一管理標籤，建議：

1. 先使用 `manage_knowledge_base_labels.py` 創建標籤
2. 在 Excel 中使用標準化的標籤名稱
3. 避免使用過多的標籤變體

### 大量數據處理

處理大量 FAQ 時：

1. **分批處理**：建議每次上傳不超過 100 個 FAQ
2. **錯誤重試**：失敗的 FAQ 可以單獨重新上傳
3. **網路穩定**：確保網路連線穩定，避免中途中斷

### 資料品質檢查

上傳前建議檢查：

1. **問題唯一性**：避免重複的問題
2. **答案完整性**：確保答案內容完整且有意義
3. **標籤一致性**：使用統一的標籤命名規則

## 疑難排解

### 取得知識庫 ID

如果不確定您的知識庫 ID，可以使用：

```bash
cd ../knowledges
python list_knowledge_bases.py
```

### 檢查上傳結果

上傳完成後，您可以使用以下方式驗證：

```bash
cd ../knowledges
python manage_knowledge_base_faq.py
```

或使用下載工具：

```bash
python download_knowledge_base_faqs.py
```

## 效能參考

- **小型批次**（< 20 FAQ）：通常 1-2 分鐘完成
- **中型批次**（20-50 FAQ）：通常 3-5 分鐘完成
- **大型批次**（50-100 FAQ）：通常 5-10 分鐘完成
- **超大批次**（> 100 FAQ）：建議分批處理

## 最佳實踐

1. **測試先行**：首次使用時先用少量資料測試
2. **備份原檔**：保留原始 Excel 檔案作為備份
3. **檢查報告**：每次上傳後檢查詳細報告
4. **標籤統一**：建立標籤使用規範
5. **定期維護**：定期檢查和更新 FAQ 內容

## 支援

如果遇到問題，請檢查：

1. API 金鑰是否正確且有效
2. 知識庫 ID 是否存在
3. Excel 檔案格式是否符合要求
4. 網路連線是否穩定
5. 是否有足夠的 API 配額

---

## 相關工具

- [`download_knowledge_base_faqs.py`](download_knowledge_base_faqs.py) - 下載知識庫 FAQ
- [`manage_knowledge_base_faq.py`](../knowledges/manage_knowledge_base_faq.py) - 管理單個 FAQ
- [`list_knowledge_bases.py`](../knowledges/list_knowledge_bases.py) - 列出所有知識庫
