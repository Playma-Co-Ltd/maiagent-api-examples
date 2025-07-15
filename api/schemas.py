from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import status

from whizchat.chatbots.api.serializers import (
    ChatbotDocumentSerializer,
    ChatbotFileBatchDeleteSerializer,
    ChatbotFileCreateFilesSerializer,
    ChatbotFileCreateSerializer,
    ChatbotFileMetadataUpdateSerializer,
    ChatbotFileReparseSerializer,
    ChatbotFileSerializer,
    ChatbotTextNodeSearchSerializer,
    ChatbotTextNodeSerializer,
    FaqBatchDeleteSerializer,
    FaqCreateSerializer,
    FaqMetadataUpdateSerializer,
    FaqSerializer,
)
from whizchat.knowledge_bases.api.serializers import (
    KnowledgeBaseCreateSerializer,
    KnowledgeBaseLabelCreateSerializer,
    KnowledgeBaseLabelSerializer,
    KnowledgeBaseLabelUpdateSerializer,
    KnowledgeBaseSerializer,
)

knowledge_base_create_schema = extend_schema(
    summary='建立知識庫',
    description='建立知識庫',
    request=KnowledgeBaseCreateSerializer,
    responses={status.HTTP_201_CREATED: KnowledgeBaseSerializer},
    tags=['knowledge-bases'],
)

knowledge_base_list_schema = extend_schema(
    summary='列出知識庫',
    description='列出所有知識庫',
    request=KnowledgeBaseSerializer,
    responses={status.HTTP_200_OK: KnowledgeBaseSerializer(many=True)},
    tags=['knowledge-bases'],
)

knowledge_base_update_schema = extend_schema(
    summary='更新知識庫',
    description='更新知識庫',
    request=KnowledgeBaseSerializer,
    responses={status.HTTP_200_OK: KnowledgeBaseSerializer},
    tags=['knowledge-bases'],
)

knowledge_base_destroy_schema = extend_schema(
    summary='刪除知識庫',
    description='刪除知識庫',
    request=KnowledgeBaseSerializer,
    responses={status.HTTP_204_NO_CONTENT: None},
    tags=['knowledge-bases'],
)

knowledge_base_label_create_schema = extend_schema(
    summary='建立知識庫標籤',
    description='建立知識庫標籤',
    request=KnowledgeBaseLabelCreateSerializer,
    responses={status.HTTP_201_CREATED: KnowledgeBaseLabelSerializer},
    tags=['knowledge-base-labels'],
)

knowledge_base_label_list_schema = extend_schema(
    summary='列出知識庫標籤',
    description='列出所有知識庫標籤',
    request=KnowledgeBaseLabelSerializer,
    responses={status.HTTP_200_OK: KnowledgeBaseLabelSerializer(many=True)},
    tags=['knowledge-base-labels'],
)

knowledge_base_label_retrieve_schema = extend_schema(
    summary='獲取知識庫標籤詳情',
    description='獲取特定知識庫標籤的詳細資訊',
    responses={status.HTTP_200_OK: KnowledgeBaseLabelSerializer()},
    tags=['knowledge-base-labels'],
)

knowledge_base_label_update_schema = extend_schema(
    summary='更新知識庫標籤',
    description='更新特定知識庫標籤的資訊',
    request=KnowledgeBaseLabelUpdateSerializer,
    responses={status.HTTP_200_OK: KnowledgeBaseLabelSerializer()},
    tags=['knowledge-base-labels'],
)

knowledge_base_label_partial_update_schema = extend_schema(
    summary='部分更新知識庫標籤',
    description='部分更新特定知識庫標籤的資訊',
    request=KnowledgeBaseLabelUpdateSerializer,
    responses={status.HTTP_200_OK: KnowledgeBaseLabelSerializer()},
    tags=['knowledge-base-labels'],
)

knowledge_base_label_delete_schema = extend_schema(
    summary='刪除知識庫標籤',
    description='刪除特定知識庫標籤',
    responses={status.HTTP_204_NO_CONTENT: None},
    tags=['knowledge-base-labels'],
)

knowledge_base_search_schema = extend_schema(
    summary='搜尋知識庫內容',
    description='搜尋特定知識庫的內容',
    request=ChatbotTextNodeSearchSerializer,
    responses={status.HTTP_200_OK: ChatbotTextNodeSerializer(many=True)},
    tags=['knowledge-bases'],
)

knowledge_base_faq_list_schema = extend_schema(
    summary='列出知識庫 FAQ',
    description='列出特定知識庫的所有 FAQ',
    responses={status.HTTP_200_OK: FaqSerializer(many=True)},
    tags=['knowledge-base-faqs'],
)

knowledge_base_faq_retrieve_schema = extend_schema(
    summary='獲取 FAQ 詳情',
    description='獲取特定 FAQ 的詳細資訊',
    responses={status.HTTP_200_OK: FaqSerializer()},
    tags=['knowledge-base-faqs'],
)

knowledge_base_faq_create_schema = extend_schema(
    summary='建立 FAQ',
    description='為特定 Chatbot 建立新的 FAQ',
    request=FaqCreateSerializer,
    responses={status.HTTP_201_CREATED: FaqSerializer()},
    tags=['knowledge-base-faqs'],
)

knowledge_base_faq_update_schema = extend_schema(
    summary='更新 FAQ',
    description='更新特定 FAQ 的資訊',
    request=FaqSerializer,
    responses={status.HTTP_200_OK: FaqSerializer()},
    tags=['knowledge-base-faqs'],
)

knowledge_base_faq_delete_schema = extend_schema(
    summary='刪除 FAQ',
    description='刪除特定 FAQ',
    responses={status.HTTP_204_NO_CONTENT: None},
    tags=['knowledge-base-faqs'],
)

knowledge_base_faq_batch_delete_schema = extend_schema(
    summary='批次刪除 FAQ',
    description='一次刪除多個 FAQ',
    request=FaqBatchDeleteSerializer,
    responses={status.HTTP_204_NO_CONTENT: None},
    tags=['knowledge-base-faqs'],
)

knowledge_base_faq_update_metadata_schema = extend_schema(
    summary='更新 FAQ 的標籤和元數據',
    description='更新特定 FAQ 的標籤和使用者自定義元數據',
    request=FaqMetadataUpdateSerializer,
    responses={status.HTTP_200_OK: FaqSerializer()},
    tags=['knowledge-base-faqs'],
)

knowledge_base_document_list_schema = extend_schema(
    summary='列出知識庫文件',
    description='列出特定知識庫檔案的所有文件',
    parameters=[
        OpenApiParameter(
            name='chatbot_file_id',
            location=OpenApiParameter.QUERY,
            description='檔案 ID',
            required=True,
            type=str,
        ),
    ],
    responses={status.HTTP_200_OK: ChatbotDocumentSerializer(many=True)},
    tags=['knowledge-base-documents'],
)

knowledge_base_document_update_schema = extend_schema(
    summary='更新知識庫文件',
    description='更新特定知識庫文件的資訊',
    request=ChatbotDocumentSerializer,
    responses={status.HTTP_200_OK: ChatbotDocumentSerializer()},
    tags=['knowledge-base-documents'],
)

knowledge_base_document_delete_schema = extend_schema(
    summary='刪除知識庫文件',
    description='刪除特定知識庫文件',
    responses={status.HTTP_204_NO_CONTENT: None},
    tags=['knowledge-base-documents'],
)

knowledge_base_view_schema = extend_schema_view(
    list=knowledge_base_list_schema,
    create=knowledge_base_create_schema,
    update=knowledge_base_update_schema,
    destroy=knowledge_base_destroy_schema,
)

knowledge_base_label_view_schema = extend_schema_view(
    list=knowledge_base_label_list_schema,
    create=knowledge_base_label_create_schema,
    retrieve=knowledge_base_label_retrieve_schema,
    update=knowledge_base_label_update_schema,
    partial_update=knowledge_base_label_partial_update_schema,
    destroy=knowledge_base_label_delete_schema,
)

knowledge_base_faq_view_schema = extend_schema_view(
    list=knowledge_base_faq_list_schema,
    retrieve=knowledge_base_faq_retrieve_schema,
    create=knowledge_base_faq_create_schema,
    update=knowledge_base_faq_update_schema,
    partial_update=knowledge_base_faq_update_schema,
    destroy=knowledge_base_faq_delete_schema,
    batch_delete_faqs=knowledge_base_faq_batch_delete_schema,
    update_metadata=knowledge_base_faq_update_metadata_schema,
)

knowledge_base_document_view_schema = extend_schema_view(
    list=knowledge_base_document_list_schema,
    update=knowledge_base_document_update_schema,
    partial_update=knowledge_base_document_update_schema,
    destroy=knowledge_base_document_delete_schema,
)

knowledge_base_file_list_schema = extend_schema(
    summary='列出知識庫檔案',
    description='取得特定知識庫的所有檔案',
    responses={status.HTTP_200_OK: ChatbotFileSerializer(many=True)},
    tags=['knowledge-base-files'],
)

knowledge_base_file_retrieve_schema = extend_schema(
    summary='獲取知識庫檔案詳情',
    description='獲取特定知識庫檔案的詳細資訊',
    responses={status.HTTP_200_OK: ChatbotFileSerializer()},
    tags=['knowledge-base-files'],
)

knowledge_base_file_create_schema = extend_schema(
    summary='建立知識庫檔案',
    description='上傳新的檔案至知識庫',
    request=ChatbotFileCreateFilesSerializer,
    responses={status.HTTP_201_CREATED: ChatbotFileSerializer(many=True)},
    tags=['knowledge-base-files'],
)

knowledge_base_file_update_schema = extend_schema(
    summary='更新知識庫檔案',
    description='更新特定知識庫檔案的資訊',
    request=ChatbotFileCreateSerializer,
    responses={status.HTTP_200_OK: ChatbotFileSerializer()},
    tags=['knowledge-base-files'],
)

knowledge_base_file_partial_update_schema = extend_schema(
    summary='部分更新知識庫檔案',
    description='部分更新特定知識庫檔案的資訊',
    request=ChatbotFileCreateSerializer,
    responses={status.HTTP_200_OK: ChatbotFileSerializer()},
    tags=['knowledge-base-files'],
)

knowledge_base_file_delete_schema = extend_schema(
    summary='刪除知識庫檔案',
    description='刪除特定知識庫檔案',
    responses={status.HTTP_204_NO_CONTENT: None},
    tags=['knowledge-base-files'],
)

knowledge_base_file_batch_delete_schema = extend_schema(
    summary='批次刪除知識庫檔案',
    description='一次刪除多個知識庫檔案',
    request=ChatbotFileBatchDeleteSerializer,
    responses={status.HTTP_204_NO_CONTENT: None},
    tags=['knowledge-base-files'],
)

knowledge_base_file_batch_reparse_schema = extend_schema(
    summary='批次重新解析知識庫檔案',
    description='重新解析多個知識庫檔案的內容',
    request=ChatbotFileReparseSerializer(many=True),
    responses={status.HTTP_200_OK: ChatbotFileSerializer(many=True)},
    tags=['knowledge-base-files'],
)

knowledge_base_file_update_metadata_schema = extend_schema(
    summary='更新知識庫檔案的標籤和元數據',
    description='更新特定知識庫檔案的標籤和使用者自定義元數據',
    request=ChatbotFileMetadataUpdateSerializer,
    responses={status.HTTP_200_OK: ChatbotFileSerializer()},
    tags=['knowledge-base-files'],
)

knowledge_base_file_view_schema = extend_schema_view(
    list=knowledge_base_file_list_schema,
    retrieve=knowledge_base_file_retrieve_schema,
    create=knowledge_base_file_create_schema,
    update=knowledge_base_file_update_schema,
    partial_update=knowledge_base_file_partial_update_schema,
    destroy=knowledge_base_file_delete_schema,
    batch_delete=knowledge_base_file_batch_delete_schema,
    batch_reparse=knowledge_base_file_batch_reparse_schema,
    update_metadata=knowledge_base_file_update_metadata_schema,
)
