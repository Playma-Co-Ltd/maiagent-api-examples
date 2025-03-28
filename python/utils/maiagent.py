import json
import os
import sseclient
from urllib.parse import urljoin
from typing import Union, Generator

import requests


class MaiAgentHelper:
    def __init__(
        self,
        api_key,
        base_url='https://api.maiagent.ai/api/v1/',
        storage_url='https://s3.ap-northeast-1.amazonaws.com/whizchat-media-prod-django.playma.app'
    ):
        self.api_key = api_key
        self.base_url = base_url
        self.storage_url = storage_url

    def create_conversation(self, web_chat_id):
        try:
            # 建立 conversation
            response = requests.post(
                url=f'{self.base_url}conversations/',
                headers={'Authorization': f'Api-Key {self.api_key}'},
                json={
                    'webChat': web_chat_id,
                },
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(e)
            print(response.text)
            print(e)
            exit(1)
        except Exception as e:
            print(e)

        return response.json()

    def send_message(self, conversation_id, content, attachments=None):
        try:
            # 傳送訊息
            response = requests.post(
                url=f'{self.base_url}messages/',
                headers={'Authorization': f'Api-Key {self.api_key}'},
                json={
                    'conversation': conversation_id,
                    'content': content,
                    'attachments': attachments or [],
                },
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(response.text)
            print(e)
            exit(1)

        return response.json()

    def get_upload_url(self, file_path, model_name, field_name='file'):
        assert os.path.exists(file_path), 'File does not exist'

        file_size = os.path.getsize(file_path)
        filename = os.path.basename(file_path)

        url = urljoin(self.base_url, 'upload-presigned-url/')

        headers = {
            'Authorization': f'Api-Key {self.api_key}',
            'Content-Type': 'application/json'
        }

        payload = {
            'filename': filename,
            'modelName': model_name,
            'fieldName': field_name,
            'fileSize': file_size
        }

        response = requests.post(url, headers=headers, data=json.dumps(payload))

        response.raise_for_status()

        if response.status_code == 200:
            return response.json()
        else:
            print(f'Error: {response.status_code}')
            print(response.text)
            return None


    def upload_file_to_s3(self, file_path, upload_data):
        with open(file_path, 'rb') as file:
            files = {'file': (os.path.basename(file_path), file)}
            data = {
                'key': upload_data['fields']['key'],
                'x-amz-algorithm': upload_data['fields']['x-amz-algorithm'],
                'x-amz-credential': upload_data['fields']['x-amz-credential'],
                'x-amz-date': upload_data['fields']['x-amz-date'],
                'policy': upload_data['fields']['policy'],
                'x-amz-signature': upload_data['fields']['x-amz-signature'],
            }

            response = requests.post(self.storage_url, data=data, files=files)

            if response.status_code == 204:
                print('File uploaded successfully')
                return upload_data['fields']['key']
            else:
                print(f'Error uploading file: {response.status_code}')
                print(response.text)
                return None

    def update_attachment(self, conversation_id, file_id, original_filename):
        url = f'{self.base_url}conversations/{conversation_id}/attachments/'

        headers = {
            'Authorization': f'Api-Key {self.api_key}',
        }

        payload = {
            'file': file_id,
            'filename': original_filename,
            'type': 'image',
        }

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(response.text)
            print(e)
            exit(1)
        except Exception as e:
            print(e)
            exit(1)

        return response.json()
    
    def update_attachment_without_conversation(self, file_id, original_filename, type):
        url = f'{self.base_url}attachments/'

        headers = {
            'Authorization': f'Api-Key {self.api_key}',
        }

        payload = {
            'file': file_id,
            'filename': original_filename,
            'type': type,
        }

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(response.text)
            print(e)
            exit(1)
        except Exception as e:
            print(e)
            exit(1)

        return response.json()

    def update_chatbot_files(self, chatbot_id: str, file_key: str, original_filename: str, parser_id: str = None):
        url = f'{self.base_url}chatbots/{chatbot_id}/files/'

        headers = {
            'Authorization': f'Api-Key {self.api_key}',
        }

        payload = {
            'files': [{
                'file': file_key,
                'filename': original_filename,
            }]
        }

        if parser_id:
            payload['files'][0]['parser'] = parser_id

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(response.text)
            print(e)
            exit(1)
        except Exception as e:
            print(e)
            exit(1)

    def upload_batch_qa_file(self, web_chat_id: str, file_key: str, original_filename: str):
        url = f'{self.base_url}web-chats/{web_chat_id}/batch-qas/'

        try:
            response = requests.post(
                url,
                headers={
                    'Authorization': f'Api-Key {self.api_key}',
                },
                json={
                    'file': file_key,
                    'filename': original_filename,
                },
            )
            response.raise_for_status()
            print('Successfully uploaded batch QA file')
        except requests.exceptions.RequestException as e:
            print(response.text)
            print(e)
            exit(3)
        except Exception as e:
            print(e)
            exit(3)

        return response.json()
    

    def download_batch_qa_excel(self, webchat_id: str, batch_qa_file_id: str):
        url = urljoin(self.base_url, f'web-chats/{webchat_id}/batch-qas/{batch_qa_file_id}/export-excel/')

        headers = {
            'Authorization': f'Api-Key {self.api_key}',
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            content_disposition = response.headers.get('Content-Disposition')
            filename = 'chatbot_records.xlsx'
            if content_disposition:
                filename = content_disposition.split('filename=')[1].strip('"')

            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f'Successfully downloaded: {filename}')
            return filename
        else:
            print(f'Error: {response.status_code}')
            print(response.text)
            return None
        
    def get_supported_file_types(self) -> dict:
        url = urljoin(self.base_url, f'parsers/supported-file-types/')
        
        headers = {
            'Authorization': f'Api-Key {self.api_key}',
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            error_msg = f"獲取支援的檔案類型失敗: {str(e)}"
            if hasattr(e, 'response') and e.response is not None:
                error_msg += f"\n回應內容: {e.response.text}"
            raise RuntimeError(error_msg)

    def upload_attachment(self, conversation_id, file_path):
        upload_url = self.get_upload_url(file_path, 'attachment')
        file_key = self.upload_file_to_s3(file_path, upload_url)
        return self.update_attachment(conversation_id, file_key, os.path.basename(file_path))

    def upload_attachment_without_conversation(self, file_path, type):
        upload_url = self.get_upload_url(file_path, 'attachment')
        file_key = self.upload_file_to_s3(file_path, upload_url)
        return self.update_attachment_without_conversation(file_key, os.path.basename(file_path), type)

    def upload_knowledge_file(self, chatbot_id: str, file_path: str, parser_id: str = None) -> dict:
        """上傳知識庫檔案"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f'檔案不存在: {file_path}')

        # 上傳檔案到 S3
        upload_url = self.get_upload_url(file_path, 'chatbot-file')
        file_key = self.upload_file_to_s3(file_path, upload_url)

        # 更新聊天機器人檔案
        return self.update_chatbot_files(
            chatbot_id=chatbot_id,
            file_key=file_key,
            original_filename=os.path.basename(file_path),
            parser_id=parser_id
        )

    def delete_knowledge_file(self, chatbot_id, file_id):
        url = f'{self.base_url}chatbots/{chatbot_id}/files/{file_id}/'

        headers = {
            'Authorization': f'Api-Key {self.api_key}',
        }

        response = requests.delete(url, headers=headers)

        if response.status_code == 204:
            print(f'Successfully deleted knowledge with ID: {file_id}')
        else:
            print(f'Error: {response.status_code}')
            print(response.text)

    def get_inbox_items(self):
        inbox_items = []

        url = f'{self.base_url}inboxes/'
        while True:
            try:
                response = requests.get(
                    url=url,
                    headers={'Authorization': f'Api-Key {self.api_key}'},
                )
                response.raise_for_status()
                inbox_items.extend(response.json()['results'])
            except requests.exceptions.RequestException as e:
                print(response.text)
                print(e)
                exit(1)
            except Exception as e:
                print(e)
                exit(1)

            url = response.json()['next']
            if url is None:
                break

        return inbox_items

    def display_inbox_items(self, inbox_items):
        for inbox_item in inbox_items:
            inbox_id = inbox_item['id']
            webchat_id = inbox_item['channel']['id']
            webchat_name = inbox_item['channel']['name']
            print(f'Inbox ID: {inbox_id}, Webchat ID: {webchat_id}, Webchat Name: {webchat_name}')

    def create_chatbot_completion(self, chatbot_id: str, content: str, attachments: list = None, conversation_id: str = None, is_streaming: bool = False) -> Union[dict, Generator]:
        """
        建立聊天機器人回應

        Args:
            chatbot_id: 聊天機器人 ID
            content: 訊息內容
            attachments: 附件列表
            conversation_id: 對話 ID
            is_streaming: 是否使用串流模式

        Returns:
            串流模式時回傳 Generator，非串流模式回傳 dict
            回應格式: {
                "conversationId": str,
                "content": str,
                "done": bool
            }
        """
        url = f'{self.base_url}chatbots/{chatbot_id}/completions/'

        headers = {
            'Authorization': f'Api-Key {self.api_key}',
        }
        
        payload = {
            'conversation': conversation_id,
            'message': {
                'content': content,
                'attachments': attachments or []
            },
            'is_streaming': is_streaming
        }

        try:
            if not is_streaming:
                return self._handle_non_streaming_completion(url, headers, payload)
            return self._handle_streaming_completion(url, headers, payload)
                
        except requests.exceptions.RequestException as e:
            error_msg = f"請求失敗: {str(e)}"
            if hasattr(e, 'response') and e.response is not None:
                error_msg += f"\n回應內容: {e.response.text}"
            raise RuntimeError(error_msg)

    def _handle_non_streaming_completion(self, url: str, headers: dict, payload: dict) -> dict:
        """處理非串流模式的回應"""
        response = requests.post(
            url,
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        return response.json()

    def _handle_streaming_completion(self, url: str, headers: dict, payload: dict) -> Generator:
        """處理串流模式的回應"""
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            stream=True
        )
        response.raise_for_status()
        
        client = sseclient.SSEClient(response)
        for event in client.events():
            if event.data:
                try:
                    data = json.loads(event.data)
                    yield data
                except json.JSONDecodeError as e:
                    print(f"JSON 解析失敗: {event.data}")
                    continue
