from typing import Any
from uuid import UUID

from django.db import transaction
from django.db.models import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from whizchat.chatbots.api.serializers import (
    ChatbotDocumentSerializer,
    ChatbotFileBatchDeleteSerializer,
    ChatbotFileCreateFilesSerializer,
    ChatbotFileMetadataUpdateSerializer,
    ChatbotFileQueryParamSerializer,
    ChatbotFileReparseSerializer,
    ChatbotFileSerializer,
    ChatbotTextNodeSearchSerializer,
    ChatbotTextNodeSerializer,
    CrawlPageImportSerializer,
    CrawlPageRequestCreateSerializer,
    CrawlPageRequestSerializer,
    CrawlPageSerializer,
    FaqBatchDeleteSerializer,
    FaqCreateSerializer,
    FaqMetadataUpdateSerializer,
    FaqSerializer,
)
from whizchat.chatbots.filters import ChatbotFileFilter, FaqFilter
from whizchat.chatbots.models import ChatbotDocument, ChatbotFile, CrawlPage, CrawlPageRequest, Faq
from whizchat.chatbots.services.faq import create_faq_service
from whizchat.chatbots.tasks import (
    batch_delete_knowledge_base_files_task,
    delete_chatbot_document_task,
    import_crawl_page_to_chatbot_file,
    update_chatbot_file_task,
)
from whizchat.knowledge_bases.api.schemas import (
    knowledge_base_document_view_schema,
    knowledge_base_faq_view_schema,
    knowledge_base_file_view_schema,
    knowledge_base_label_view_schema,
    knowledge_base_search_schema,
    knowledge_base_view_schema,
)
from whizchat.knowledge_bases.api.serializers import (
    KnowledgeBaseCreateSerializer,
    KnowledgeBaseFaqBatchDeleteSerializer,
    KnowledgeBaseLabelCreateSerializer,
    KnowledgeBaseLabelSerializer,
    KnowledgeBaseLabelUpdateSerializer,
    KnowledgeBaseSerializer,
)
from whizchat.knowledge_bases.filters import KnowledgeBaseFilter
from whizchat.knowledge_bases.models import KnowledgeBase, KnowledgeBaseLabel
from whizchat.utils.common.services.maiagent_rag_services.retrieve_api import RetrieveApiService
from whizchat.utils.common.utils import update_chatbot_file_status


@knowledge_base_view_schema
class KnowledgeBaseViewSet(
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = KnowledgeBase.objects.all()
    serializer_class = KnowledgeBaseSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = KnowledgeBaseFilter

    def get_serializer_class(
        self,
    ) -> KnowledgeBaseCreateSerializer | KnowledgeBaseSerializer | ChatbotTextNodeSearchSerializer:
        if self.action == 'create':
            return KnowledgeBaseCreateSerializer
        if self.action == 'search':
            return ChatbotTextNodeSearchSerializer
        return self.serializer_class

    def get_queryset(self):
        return self.queryset.filter(organization_id=self.request.organization_id)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        serializer = KnowledgeBaseSerializer(serializer.instance)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @knowledge_base_search_schema
    @action(detail=True, methods=['post'])
    def search(self, request, pk=None):
        """搜尋 knowledgebase 的知識內容"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        knowledge_base_instance = self.get_object()
        retrieve_api_service = RetrieveApiService()
        results = retrieve_api_service.search_with_knowledge_base(
            query=validated_data['query'],
            knowledge_base_instance=knowledge_base_instance,
        )

        return Response(
            data=ChatbotTextNodeSerializer(results, many=True).data,
            status=status.HTTP_200_OK,
        )


@knowledge_base_label_view_schema
class KnowledgeBaseLabelViewSet(viewsets.ModelViewSet):
    queryset = KnowledgeBaseLabel.objects.all()
    serializer_class = KnowledgeBaseLabelSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return KnowledgeBaseLabelCreateSerializer
        if self.action == 'update':
            return KnowledgeBaseLabelUpdateSerializer
        return self.serializer_class

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['knowledge_base_pk'] = self.kwargs.get('knowledge_base_pk')
        return context

    def get_queryset(self):
        return self.queryset.filter(
            knowledge_base_id=self.kwargs['knowledge_base_pk'],
            knowledge_base__organization_id=self.request.organization_id,
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        serializer = self.serializer_class(serializer.instance)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        serializer = self.serializer_class(serializer.instance)

        return Response(serializer.data, status=status.HTTP_200_OK)


@knowledge_base_file_view_schema
class KnowledgeBaseFileViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
):
    queryset = ChatbotFile.objects.all()
    serializer_class = ChatbotFileSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ChatbotFileFilter

    def get_serializer_class(self):
        if self.action == 'create':
            return ChatbotFileCreateFilesSerializer
        elif self.action == 'update':
            return ChatbotFileMetadataUpdateSerializer
        elif self.action == 'partial_update':
            return ChatbotFileMetadataUpdateSerializer
        elif self.action == 'batch_reparse':
            return ChatbotFileReparseSerializer
        elif self.action == 'batch_delete':
            return ChatbotFileBatchDeleteSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        knowledge_base_id = self.kwargs['knowledge_base_pk']
        queryset = ChatbotFile.objects.filter(
            knowledge_base_id=knowledge_base_id,
            conversation_id__isnull=True,
        )
        if self.action == 'list':
            queryset = queryset.filter(source_file__isnull=True)
        return self.get_serializer_class().setup_eager_loading(queryset)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            chatbot_files = serializer.save(knowledge_base_id=self.kwargs['knowledge_base_pk'])
        return Response(
            data=ChatbotFileSerializer(chatbot_files, many=True).data,
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        """更新檔案，使用 ChatbotFileMetadataUpdateSerializer 處理更新，用 ChatbotFileSerializer 回傳完整資料"""
        return self._update_file(request, partial=False)

    def partial_update(self, request, *args, **kwargs):
        """部分更新檔案，使用 ChatbotFileMetadataUpdateSerializer 處理更新，用 ChatbotFileSerializer 回傳完整資料"""
        return self._update_file(request, partial=True)

    def _update_file(self, request: Request, partial: bool = False) -> Response:
        """更新檔案的共用邏輯"""
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        updated_instance = serializer.save()

        return Response(data=ChatbotFileSerializer(updated_instance).data)

    def perform_create(self, serializer: ChatbotFileCreateFilesSerializer):
        knowledge_base_id = self.kwargs['knowledge_base_pk']
        serializer.save(knowledge_base_id=knowledge_base_id)

    @action(
        detail=False,
        methods=['post'],
        url_path='batch-delete',
    )
    def batch_delete(self, request, knowledge_base_pk=None):
        serializer = self.get_serializer(data=request.data, context={'knowledge_base_pk': knowledge_base_pk})
        serializer.is_valid(raise_exception=True)

        chatbot_file_instances = serializer.validated_data.get('chatbot_file_instances')
        if chatbot_file_instances is not None:
            chatbot_file_ids = list(chatbot_file_instances.values_list('id', flat=True))

            update_chatbot_file_status(
                chatbot_file_ids=chatbot_file_ids,
                status=ChatbotFile.Status.DELETING,
            )

            batch_delete_knowledge_base_files_task.delay(knowledge_base_file_ids=chatbot_file_ids)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['patch'],
        url_path='batch-reparse',
    )
    def batch_reparse(
        self,
        request: Request,
        knowledge_base_pk: UUID | None = None,
    ) -> Response:
        """批次重新解析指定知識庫檔案。"""
        serializer = ChatbotFileReparseSerializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)

        knowledge_base_id = knowledge_base_pk or self.kwargs['knowledge_base_pk']
        chatbot_file_instances = self._get_knowledge_base_files(
            validated_data=serializer.validated_data,
            knowledge_base_pk=knowledge_base_id,
        )
        chatbot_file_instances = ChatbotFileReparseSerializer.validate_reparseable(chatbot_file_instances)
        updated_chatbot_file_instances = self._update_knowledge_base_file_parsers(
            chatbot_file_instances=chatbot_file_instances,
            validated_data=serializer.validated_data,
        )

        for updated_chatbot_file_instance in updated_chatbot_file_instances:
            update_chatbot_file_task.delay(updated_chatbot_file_instance.id)

        return Response(data=ChatbotFileSerializer(updated_chatbot_file_instances, many=True).data)

    @action(
        detail=True,
        methods=['patch'],
        url_path='update-metadata',
    )
    def update_metadata(self, request, knowledge_base_pk=None, pk=None):
        chatbot_file_instance = self.get_object()
        serializer = ChatbotFileMetadataUpdateSerializer(chatbot_file_instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(ChatbotFileSerializer(chatbot_file_instance).data)

    def _get_knowledge_base_files(
        self,
        validated_data: list[dict],
        knowledge_base_pk: UUID,
    ) -> QuerySet[ChatbotFile]:
        file_ids = [file_data['id'] for file_data in validated_data]
        return ChatbotFile.objects.filter(
            id__in=file_ids,
            knowledge_base_id=knowledge_base_pk,
        ).select_related('parser', 'knowledge_base')

    def _update_knowledge_base_file_parsers(
        self,
        chatbot_file_instances: QuerySet[ChatbotFile],
        validated_data: list[dict],
    ) -> list[ChatbotFile]:
        """當解析器有更新時，批次更新 ChatbotFile 的 parser"""
        parser_map = {str(file_data['id']): file_data.get('parser') for file_data in validated_data}

        updated_chatbot_file_instances = []
        for chatbot_file_instance in chatbot_file_instances:
            if new_parser := parser_map.get(str(chatbot_file_instance.id)):
                chatbot_file_instance.parser = new_parser
                updated_chatbot_file_instances.append(chatbot_file_instance)

        ChatbotFile.objects.bulk_update(updated_chatbot_file_instances, ['parser'])

        return updated_chatbot_file_instances


@knowledge_base_faq_view_schema
class KnowledgeBaseFaqViewSet(
    viewsets.ModelViewSet,
):
    queryset = Faq.objects.all()
    serializer_class = FaqSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = FaqFilter

    def get_queryset(self) -> QuerySet[Faq]:
        queryset = self.queryset.filter(
            knowledge_base_id=self.kwargs['knowledge_base_pk'],
            knowledge_base__organization_id=self.request.organization_id,
        )
        return self.get_serializer_class().setup_eager_loading(queryset)

    def get_serializer_class(
        self,
    ) -> FaqSerializer | FaqCreateSerializer | FaqBatchDeleteSerializer | KnowledgeBaseFaqBatchDeleteSerializer:
        """根據不同的操作返回不同的序列化器"""
        if self.action == 'create':
            return FaqCreateSerializer
        elif self.action == 'batch_delete_faqs':
            return KnowledgeBaseFaqBatchDeleteSerializer
        elif self.action == 'batch_delete_faqs':
            return FaqBatchDeleteSerializer

        return super().get_serializer_class()

    def perform_create(
        self,
        serializer: FaqCreateSerializer,
    ) -> None:
        """儲存 FAQ 並關聯到指定的 chatbot ID 和預設的 knowledge_base"""
        knowledge_base_id = self.kwargs['knowledge_base_pk']
        save_kwargs = {'knowledge_base_id': knowledge_base_id}
        serializer.save(**save_kwargs)

    @action(
        detail=False,
        methods=['post'],
        url_path='batch-delete',
    )
    def batch_delete_faqs(
        self,
        request: Request,
        knowledge_base_pk: UUID,
    ) -> Response:
        """批量刪除 FAQ，如果未提供 ID 列表，則刪除所有 FAQ"""
        serializer = self.get_serializer(data=request.data, context={'knowledge_base_pk': knowledge_base_pk})
        serializer.is_valid(raise_exception=True)

        faq_instances: QuerySet[Faq] = serializer.validated_data['faq_instances']

        if faq_instances.exists():
            faq_service = create_faq_service(faq_instance=faq_instances.first())

            with transaction.atomic():
                faq_service.delete_faqs(faq_instances=faq_instances)
                faq_instances.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['patch'],
        url_path='update-metadata',
    )
    def update_metadata(
        self,
        request: Request,
        knowledge_base_pk: UUID | None = None,
        pk: UUID | None = None,
    ) -> Response:
        """更新 Faq 的標籤和元數據"""
        faq_instance = self.get_object()
        serializer = FaqMetadataUpdateSerializer(
            instance=faq_instance,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(FaqSerializer(faq_instance).data)


@knowledge_base_document_view_schema
class KnowledgeBaseDocumentViewSet(
    viewsets.GenericViewSet,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
):
    queryset = ChatbotDocument.objects.all()
    serializer_class = ChatbotDocumentSerializer
    pagination_class = None

    def get_queryset(self) -> QuerySet[ChatbotDocument]:
        queryset = super().get_queryset()
        queryset = queryset.order_by('page_number')

        param_serializer = ChatbotFileQueryParamSerializer(data=self.request.query_params)
        param_serializer.is_valid(raise_exception=True)
        chatbot_file: ChatbotFile = param_serializer.validated_data['chatbot_file']

        queryset = queryset.filter(chatbot_file=chatbot_file)
        return self.get_serializer_class().setup_eager_loading(queryset)

    def perform_destroy(
        self,
        instance: ChatbotDocument,
    ) -> None:
        delete_chatbot_document_task(instance.id)
        super().perform_destroy(instance)


class KnowledgeBaseCrawlPageRequestViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
):
    queryset = CrawlPageRequest.objects.all()
    serializer_class = CrawlPageRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self) -> QuerySet[CrawlPageRequest]:
        knowledge_base_id = self.kwargs['knowledge_base_pk']
        return self.queryset.filter(knowledge_base_id=knowledge_base_id)

    def get_serializer_class(self):
        if self.action == 'create':
            return CrawlPageRequestCreateSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer: CrawlPageRequestCreateSerializer) -> None:
        knowledge_base_id = self.kwargs['knowledge_base_pk']
        serializer.save(knowledge_base_id=knowledge_base_id)


class KnowledgeBaseCrawlPageViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
):
    queryset = CrawlPage.objects.all()
    serializer_class = CrawlPageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self) -> QuerySet[CrawlPage]:
        knowledge_base_id = self.kwargs['knowledge_base_pk']
        crawl_page_request_id = self.kwargs['crawl_page_request_pk']
        return self.queryset.filter(
            crawl_page_request_id=crawl_page_request_id,
            crawl_page_request__knowledge_base_id=knowledge_base_id,
        )

    def get_serializer_class(self):
        if self.action == 'import_file':
            return CrawlPageImportSerializer
        return super().get_serializer_class()

    @action(
        detail=True,
        methods=['post'],
        url_path='import-file',
    )
    def import_file(
        self,
        request: Request,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        crawl_page_instance: CrawlPage = self.get_object()
        serializer = self.get_serializer(
            data=request.data,
            context={'crawl_page_instance': crawl_page_instance},
        )
        serializer.is_valid(raise_exception=True)
        crawl_page_instance = serializer.validated_data['crawl_page_instance']
        transaction.on_commit(
            lambda: import_crawl_page_to_chatbot_file.delay(
                crawl_page_id=crawl_page_instance.id,
            )
        )
        crawl_page_instance.status = CrawlPage.Status.PROCESSING
        crawl_page_instance.save(update_fields=['status'])

        return Response(data=CrawlPageSerializer(crawl_page_instance).data)
