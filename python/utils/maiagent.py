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

        url = f'{self.base_url}upload-presigned-url/'

        headers = {'Authorization': f'Api-Key {self.api_key}', 'Content-Type': 'application/json'}

        payload = {'filename': filename, 'modelName': model_name, 'fieldName': field_name, 'fileSize': file_size}

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

    def update_chatbot_files(self, chatbot_id, file_key, original_filename):
        url = f'{self.base_url}chatbots/{chatbot_id}/files/'

        headers = {
            'Authorization': f'Api-Key {self.api_key}',
        }

        payload = {'files': [{'file': file_key, 'filename': original_filename}]}

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

    def upload_attachment(self, conversation_id, file_path):
        upload_url = self.get_upload_url(file_path, 'attachment')
        file_key = self.upload_file_to_s3(file_path, upload_url)

        return self.update_attachment(conversation_id, file_key, os.path.basename(file_path))

    def upload_attachment_without_conversation(self, file_path, type):
        upload_url = self.get_upload_url(file_path, 'attachment')
        file_key = self.upload_file_to_s3(file_path, upload_url)
        return self.update_attachment_without_conversation(file_key, os.path.basename(file_path), type)

    def upload_knowledge_file(self, knowledge_base_id, file_path):
        """上傳檔案到知識庫"""
        upload_url = self.get_upload_url(file_path, 'chatbot-file')
        file_key = self.upload_file_to_s3(file_path, upload_url)

        url = f'{self.base_url}knowledge-bases/{knowledge_base_id}/files/'
        
        headers = {
            'Authorization': f'Api-Key {self.api_key}',
        }

        payload = {'files': [{'file': file_key, 'filename': os.path.basename(file_path)}]}

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

    def delete_knowledge_file(self, knowledge_base_id, file_id):
        """刪除知識庫檔案"""
        url = f'{self.base_url}knowledge-bases/{knowledge_base_id}/files/{file_id}/'

        headers = {
            'Authorization': f'Api-Key {self.api_key}',
        }

        try:
            response = requests.delete(url, headers=headers)
            
            if response.status_code == 204:
                print(f'Successfully deleted knowledge file with ID: {file_id}')
                return True
            else:
                print(f'Error: {response.status_code}')
                print(response.text)
                # 拋出異常而不是只打印錯誤
                response.raise_for_status()
                
        except requests.exceptions.RequestException as e:
            print(f'刪除檔案時發生錯誤：{e}')
            raise e
        except Exception as e:
            print(f'未知錯誤：{e}')
            raise e

    # ========== 知識庫 CRUD 操作 ==========
    
    def create_knowledge_base(self, name, description=None, embedding_model=None, 
                            reranker_model=None, number_of_retrieved_chunks=12, 
                            sentence_window_size=2, enable_hyde=False, 
                            similarity_cutoff=0.0, enable_rerank=True, chatbots=None):
        """建立知識庫"""
        url = f'{self.base_url}knowledge-bases/'
        
        headers = {
            'Authorization': f'Api-Key {self.api_key}',
        }
        
        payload = {
            'name': name,
            'description': description,
            'embedding_model': embedding_model,
            'reranker_model': reranker_model,
            'number_of_retrieved_chunks': number_of_retrieved_chunks,
            'sentence_window_size': sentence_window_size,
            'enable_hyde': enable_hyde,
            'similarity_cutoff': similarity_cutoff,
            'enable_rerank': enable_rerank,
            'chatbots': chatbots or []
        }
        
        # 移除 None 值
        payload = {k: v for k, v in payload.items() if v is not None}
        
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

    def list_knowledge_bases(self):
        """列出所有知識庫"""
        url = f'{self.base_url}knowledge-bases/'
        
        headers = {
            'Authorization': f'Api-Key {self.api_key}',
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(response.text)
            print(e)
            exit(1)
        except Exception as e:
            print(e)
            exit(1)

    def get_knowledge_base(self, knowledge_base_id):
        """獲取知識庫詳情"""
        url = f'{self.base_url}knowledge-bases/{knowledge_base_id}/'
        
        headers = {
            'Authorization': f'Api-Key {self.api_key}',
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(response.text)
            print(e)
            exit(1)
        except Exception as e:
            print(e)
            exit(1)

    def update_knowledge_base(self, knowledge_base_id, name=None, description=None, 
                            embedding_model=None, reranker_model=None, 
                            number_of_retrieved_chunks=None, sentence_window_size=None, 
                            enable_hyde=None, similarity_cutoff=None, enable_rerank=None, 
                            chatbots=None):
        """更新知識庫"""
        url = f'{self.base_url}knowledge-bases/{knowledge_base_id}/'
        
        headers = {
            'Authorization': f'Api-Key {self.api_key}',
        }
        
        payload = {}
        if name is not None:
            payload['name'] = name
        if description is not None:
            payload['description'] = description
        if embedding_model is not None:
            payload['embedding_model'] = embedding_model
        if reranker_model is not None:
            payload['reranker_model'] = reranker_model
        if number_of_retrieved_chunks is not None:
            payload['number_of_retrieved_chunks'] = number_of_retrieved_chunks
        if sentence_window_size is not None:
            payload['sentence_window_size'] = sentence_window_size
        if enable_hyde is not None:
            payload['enable_hyde'] = enable_hyde
        if similarity_cutoff is not None:
            payload['similarity_cutoff'] = similarity_cutoff
        if enable_rerank is not None:
            payload['enable_rerank'] = enable_rerank
        if chatbots is not None:
            payload['chatbots'] = chatbots
        
        try:
            response = requests.put(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(response.text)
            print(e)
            exit(1)
        except Exception as e:
            print(e)
            exit(1)

    def delete_knowledge_base(self, knowledge_base_id):
        """刪除知識庫"""
        url = f'{self.base_url}knowledge-bases/{knowledge_base_id}/'
        
        headers = {
            'Authorization': f'Api-Key {self.api_key}',
        }
        
        try:
            response = requests.delete(url, headers=headers)
            response.raise_for_status()
            print(f'Successfully deleted knowledge base with ID: {knowledge_base_id}')
        except requests.exceptions.RequestException as e:
            print(response.text)
            print(e)
            exit(1)
        except Exception as e:
            print(e)
            exit(1)

    def search_knowledge_base(self, knowledge_base_id, query):
        """搜尋知識庫內容"""
        url = f'{self.base_url}knowledge-bases/{knowledge_base_id}/search/'
        
        headers = {
            'Authorization': f'Api-Key {self.api_key}',
        }
        
        payload = {'query': query}
        
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

    # ========== 知識庫標籤 CRUD 操作 ==========
    
    def create_knowledge_base_label(self, knowledge_base_id, name):
        """建立知識庫標籤"""
        url = f'{self.base_url}knowledge-bases/{knowledge_base_id}/labels/'
        
        headers = {
            'Authorization': f'Api-Key {self.api_key}',
        }
        
        payload = {'name': name}
        
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

    def list_knowledge_base_labels(self, knowledge_base_id):
        """列出知識庫標籤"""
        url = f'{self.base_url}knowledge-bases/{knowledge_base_id}/labels/'
        
        headers = {
            'Authorization': f'Api-Key {self.api_key}',
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(response.text)
            print(e)
            exit(1)
        except Exception as e:
            print(e)
            exit(1)

    def get_knowledge_base_label(self, knowledge_base_id, label_id):
        """獲取知識庫標籤詳情"""
        url = f'{self.base_url}knowledge-bases/{knowledge_base_id}/labels/{label_id}/'
        
        headers = {
            'Authorization': f'Api-Key {self.api_key}',
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(response.text)
            print(e)
            exit(1)
        except Exception as e:
            print(e)
            exit(1)

    def update_knowledge_base_label(self, knowledge_base_id, label_id, name):
        """更新知識庫標籤"""
        url = f'{self.base_url}knowledge-bases/{knowledge_base_id}/labels/{label_id}/'
        
        headers = {
            'Authorization': f'Api-Key {self.api_key}',
        }
        
        payload = {'name': name}
        
        try:
            response = requests.put(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(response.text)
            print(e)
            exit(1)
        except Exception as e:
            print(e)
            exit(1)

    def delete_knowledge_base_label(self, knowledge_base_id, label_id):
        """刪除知識庫標籤"""
        url = f'{self.base_url}knowledge-bases/{knowledge_base_id}/labels/{label_id}/'
        
        headers = {
            'Authorization': f'Api-Key {self.api_key}',
        }
        
        try:
            response = requests.delete(url, headers=headers)
            response.raise_for_status()
            print(f'Successfully deleted knowledge base label with ID: {label_id}')
        except requests.exceptions.RequestException as e:
            print(response.text)
            print(e)
            exit(1)
        except Exception as e:
            print(e)
            exit(1)

    # ========== 知識庫檔案進階操作 ==========
    
    def list_knowledge_base_files(self, knowledge_base_id):
        """列出知識庫檔案"""
        url = f'{self.base_url}knowledge-bases/{knowledge_base_id}/files/'
        
        headers = {
            'Authorization': f'Api-Key {self.api_key}',
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(response.text)
            print(e)
            exit(1)
        except Exception as e:
            print(e)
            exit(1)

    def get_knowledge_base_file(self, knowledge_base_id, file_id):
        """獲取知識庫檔案詳情"""
        url = f'{self.base_url}knowledge-bases/{knowledge_base_id}/files/{file_id}/'
        
        headers = {
            'Authorization': f'Api-Key {self.api_key}',
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(response.text)
            print(e)
            exit(1)
        except Exception as e:
            print(e)
            exit(1)

    def update_knowledge_base_file_metadata(self, knowledge_base_id, file_id, labels=None, metadata=None):
        """更新知識庫檔案的標籤和元數據"""
        url = f'{self.base_url}knowledge-bases/{knowledge_base_id}/files/{file_id}/update-metadata/'
        
        headers = {
            'Authorization': f'Api-Key {self.api_key}',
        }
        
        payload = {}
        if labels is not None:
            payload['labels'] = labels
        if metadata is not None:
            payload['metadata'] = metadata
        
        try:
            response = requests.patch(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(response.text)
            print(e)
            exit(1)
        except Exception as e:
            print(e)
            exit(1)

    def batch_delete_knowledge_base_files(self, knowledge_base_id, file_ids):
        """批次刪除知識庫檔案"""
        url = f'{self.base_url}knowledge-bases/{knowledge_base_id}/files/batch-delete/'
        
        headers = {
            'Authorization': f'Api-Key {self.api_key}',
        }
        
        payload = {'ids': file_ids}
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            print(f'Successfully deleted {len(file_ids)} files')
        except requests.exceptions.RequestException as e:
            print(response.text)
            print(e)
            exit(1)
        except Exception as e:
            print(e)
            exit(1)

    def batch_reparse_knowledge_base_files(self, knowledge_base_id, file_parsers):
        """批次重新解析知識庫檔案"""
        url = f'{self.base_url}knowledge-bases/{knowledge_base_id}/files/batch-reparse/'
        
        headers = {
            'Authorization': f'Api-Key {self.api_key}',
        }
        
        try:
            response = requests.patch(url, headers=headers, json=file_parsers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(response.text)
            print(e)
            exit(1)
        except Exception as e:
            print(e)
            exit(1)

    # ========== 知識庫 FAQ CRUD 操作 ==========
    
    def create_knowledge_base_faq(self, knowledge_base_id, question, answer, labels=None):
        """建立知識庫 FAQ"""
        url = f'{self.base_url}knowledge-bases/{knowledge_base_id}/faqs/'
        
        headers = {
            'Authorization': f'Api-Key {self.api_key}',
        }
        
        payload = {
            'question': question,
            'answer': answer,
            'labels': labels or []
        }
        
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

    def list_knowledge_base_faqs(self, knowledge_base_id):
        """列出知識庫 FAQ"""
        url = f'{self.base_url}knowledge-bases/{knowledge_base_id}/faqs/'
        
        headers = {
            'Authorization': f'Api-Key {self.api_key}',
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(response.text)
            print(e)
            exit(1)
        except Exception as e:
            print(e)
            exit(1)

    def get_knowledge_base_faq(self, knowledge_base_id, faq_id):
        """獲取知識庫 FAQ 詳情"""
        url = f'{self.base_url}knowledge-bases/{knowledge_base_id}/faqs/{faq_id}/'
        
        headers = {
            'Authorization': f'Api-Key {self.api_key}',
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(response.text)
            print(e)
            exit(1)
        except Exception as e:
            print(e)
            exit(1)

    def update_knowledge_base_faq(self, knowledge_base_id, faq_id, question=None, answer=None, labels=None):
        """更新知識庫 FAQ"""
        url = f'{self.base_url}knowledge-bases/{knowledge_base_id}/faqs/{faq_id}/'
        
        headers = {
            'Authorization': f'Api-Key {self.api_key}',
        }
        
        payload = {}
        if question is not None:
            payload['question'] = question
        if answer is not None:
            payload['answer'] = answer
        if labels is not None:
            payload['labels'] = labels
        
        try:
            response = requests.put(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(response.text)
            print(e)
            exit(1)
        except Exception as e:
            print(e)
            exit(1)

    def delete_knowledge_base_faq(self, knowledge_base_id, faq_id):
        """刪除知識庫 FAQ"""
        url = f'{self.base_url}knowledge-bases/{knowledge_base_id}/faqs/{faq_id}/'
        
        headers = {
            'Authorization': f'Api-Key {self.api_key}',
        }
        
        try:
            response = requests.delete(url, headers=headers)
            response.raise_for_status()
            print(f'Successfully deleted knowledge base FAQ with ID: {faq_id}')
        except requests.exceptions.RequestException as e:
            print(response.text)
            print(e)
            exit(1)
        except Exception as e:
            print(e)
            exit(1)

    def batch_delete_knowledge_base_faqs(self, knowledge_base_id, faq_ids=None):
        """批次刪除知識庫 FAQ"""
        url = f'{self.base_url}knowledge-bases/{knowledge_base_id}/faqs/batch-delete/'
        
        headers = {
            'Authorization': f'Api-Key {self.api_key}',
        }
        
        payload = {'ids': faq_ids or []}
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            if faq_ids:
                print(f'Successfully deleted {len(faq_ids)} FAQs')
            else:
                print('Successfully deleted all FAQs')
        except requests.exceptions.RequestException as e:
            print(response.text)
            print(e)
            exit(1)
        except Exception as e:
            print(e)
            exit(1)

    def update_knowledge_base_faq_metadata(self, knowledge_base_id, faq_id, labels=None, metadata=None):
        """更新知識庫 FAQ 的標籤和元數據"""
        url = f'{self.base_url}knowledge-bases/{knowledge_base_id}/faqs/{faq_id}/update-metadata/'
        
        headers = {
            'Authorization': f'Api-Key {self.api_key}',
        }
        
        payload = {}
        if labels is not None:
            payload['labels'] = labels
        if metadata is not None:
            payload['metadata'] = metadata
        
        try:
            response = requests.patch(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(response.text)
            print(e)
            exit(1)
        except Exception as e:
            print(e)
            exit(1)

    # ========== 知識庫文件操作 ==========
    
    def list_knowledge_base_documents(self, knowledge_base_id, chatbot_file_id):
        """列出知識庫文件"""
        url = f'{self.base_url}knowledge-bases/{knowledge_base_id}/documents/'
        
        headers = {
            'Authorization': f'Api-Key {self.api_key}',
        }
        
        params = {'chatbot_file_id': chatbot_file_id}
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(response.text)
            print(e)
            exit(1)
        except Exception as e:
            print(e)
            exit(1)

    def update_knowledge_base_document(self, knowledge_base_id, document_id, content=None, metadata=None):
        """更新知識庫文件"""
        url = f'{self.base_url}knowledge-bases/{knowledge_base_id}/documents/{document_id}/'
        
        headers = {
            'Authorization': f'Api-Key {self.api_key}',
        }
        
        payload = {}
        if content is not None:
            payload['content'] = content
        if metadata is not None:
            payload['metadata'] = metadata
        
        try:
            response = requests.put(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(response.text)
            print(e)
            exit(1)
        except Exception as e:
            print(e)
            exit(1)

    def delete_knowledge_base_document(self, knowledge_base_id, document_id):
        """刪除知識庫文件"""
        url = f'{self.base_url}knowledge-bases/{knowledge_base_id}/documents/{document_id}/'
        
        headers = {
            'Authorization': f'Api-Key {self.api_key}',
        }
        
        try:
            response = requests.delete(url, headers=headers)
            response.raise_for_status()
            print(f'Successfully deleted knowledge base document with ID: {document_id}')
        except requests.exceptions.RequestException as e:
            print(response.text)
            print(e)
            exit(1)
        except Exception as e:
            print(e)
            exit(1)

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
