# 串接 MaiAgent API

API 文件請參考 [MaiAgent API 文件](https://documenter.getpostman.com/view/36982281/2sAXjQ3AgP#2030354f-8af9-4cf0-ad35-79d42836ae88)

## 拿取 API Key

1. 登入[MaiAgent 系統後台](https://admin.maiagent.ai/)
2. 右上角點擊「使用者名稱」
3. 點擊「帳號」
4. 即可查看「API 金鑰」

![image](images/get_api_key.png)

## 設定 Webhook 網址

1. 登入[MaiAgent 系統後台](https://admin.maiagent.ai/)
2. 點擊左側選單中的 `AI 助理`
3. 點擊進入一個 `AI 助理` 的詳細頁面
4. 最下方 `Webhook` 欄位填入 `Webhook 網址`
5. 點擊 `儲存`

## 取得 Web Chat ID

方法一：

1. 登入[MaiAgent 系統後台](https://admin.maiagent.ai/)
2. 點擊左側選單中的 `AI 助理`
3. 點擊進入一個 `AI 助理` 的詳細頁面
4. 查看最下方 `Web Chat ID` 欄位

方法二：

1. 使用 GET Inboxes API 取得 Web Chat ID。


## Python 範例

Python 範例請參考 [Python 範例](python/README.md)
