# Contacts API 使用說明

管理聯絡人（Contacts）的 API 範例，包含聯絡人的 CRUD 操作、查詢對話紀錄、群發訊息等功能。

## API 端點總覽

| 操作 | 方法 | 端點 | 說明 |
|------|------|------|------|
| 列出聯絡人 | GET | `/api/v1/contacts/` | 取得聯絡人清單（支援篩選、搜尋） |
| 建立聯絡人 | POST | `/api/v1/contacts/` | 建立新的聯絡人 |
| 取得聯絡人 | GET | `/api/v1/contacts/{id}/` | 取得單一聯絡人詳細資訊 |
| 更新聯絡人 | PATCH | `/api/v1/contacts/{id}/` | 更新聯絡人資訊 |
| 刪除聯絡人 | DELETE | `/api/v1/contacts/{id}/` | 刪除聯絡人（軟刪除） |
| 查詢對話 | GET | `/api/v1/contacts/{id}/conversations` | 取得聯絡人的對話紀錄 |
| 最新對話 | GET | `/api/v1/contacts/{id}/conversations/latest` | 取得聯絡人最新的對話 |
| 群發訊息 | POST | `/api/v1/contacts/broadcast-message` | 對多個聯絡人群發訊息 |

## 聯絡人欄位說明

| 欄位 | 類型 | 必填 | 說明 |
|------|------|------|------|
| `id` | UUID | 自動產生 | 聯絡人唯一識別碼 |
| `name` | string | 是 | 聯絡人名稱 |
| `email` | string | 否 | 電子信箱 |
| `phone_number` | string | 否 | 電話號碼 |
| `avatar` | URL | 否 | 頭像網址 |
| `source_id` | string | 否 | 外部來源識別碼（同一 inbox 內不可重複） |
| `inboxes` | array | 是 | 所屬的 inbox 列表，格式：`[{"id": "inbox-uuid"}]` |
| `query_metadata` | object | 否 | 自訂的查詢用 metadata（JSON 格式） |
| `mcp_credentials` | array | 唯讀 | MCP 憑證列表 |
| `created_at` | datetime | 自動產生 | 建立時間 |
| `updated_at` | datetime | 自動產生 | 更新時間 |

## 篩選參數

列出聯絡人時可使用以下查詢參數：

| 參數 | 說明 |
|------|------|
| `query` | 依聯絡人 ID、名稱或 source_id 搜尋（模糊比對） |
| `inboxes` | 依 inbox ID 篩選 |
| `limit` | 每頁筆數（預設 20） |
| `offset` | 分頁偏移量 |

## 範例檔案

- [list_contacts.py](list_contacts.py): 列出聯絡人清單（含篩選）
- [create_contact.py](create_contact.py): 建立新聯絡人
- [update_contact.py](update_contact.py): 更新聯絡人資訊
- [delete_contact.py](delete_contact.py): 刪除聯絡人
- [get_contact_conversations.py](get_contact_conversations.py): 取得聯絡人對話紀錄
- [broadcast_message.py](broadcast_message.py): 群發訊息給多個聯絡人

## 群發訊息模式

`broadcast-message` 支援三種模式：

1. **指定聯絡人**：提供 `contact_ids` 列表，僅發送給指定的聯絡人
2. **排除聯絡人**：提供 `inbox_id` + `exclude_contact_ids`，發送給該 inbox 中排除指定聯絡人以外的所有人
3. **全部發送**：僅提供 `inbox_id`，發送給該 inbox 的所有聯絡人
