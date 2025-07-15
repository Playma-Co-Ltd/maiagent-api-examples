from uuid import UUID

from django.shortcuts import get_object_or_404
from django.utils.translation import gettext as _
from rest_framework import serializers

from whizchat.chatbots.models import EmbeddingModel, Faq, RerankerModel
from whizchat.knowledge_bases.models import KnowledgeBase, KnowledgeBaseLabel
from whizchat.organizations.models import Organization
from whizchat.users.models import User
from whizchat.utils.common.serializers import BaseModelSerializer, IdNameSerializer, IdNameSerializerMixin


class KnowledgeBaseLabelCreateSerializer(BaseModelSerializer[KnowledgeBaseLabel]):
    """KnowledgeBaseLabel 建立的序列化器"""

    name = serializers.CharField(max_length=64)

    class Meta:
        model = KnowledgeBaseLabel
        fields = ['name']

    def validate(self, attrs: dict) -> dict:
        knowledge_base_pk = self.context.get('knowledge_base_pk')
        if not knowledge_base_pk:
            raise serializers.ValidationError({'knowledge_base': _('knowledge_base_pk is required')})
        knowledge_base_instance = get_object_or_404(KnowledgeBase, id=knowledge_base_pk)

        if KnowledgeBaseLabel.objects.filter(knowledge_base=knowledge_base_instance, name=attrs['name']).exists():
            raise serializers.ValidationError({'name': _('同一知識庫下標籤名稱不可重複')})
        attrs['knowledge_base'] = knowledge_base_instance
        return attrs


class KnowledgeBaseLabelSerializer(BaseModelSerializer[KnowledgeBaseLabel]):
    """KnowledgeBaseLabel 配合其他物件分配與顯示的序列化器"""

    id = serializers.UUIDField(required=True)
    name = serializers.CharField(required=False, allow_null=True)

    class Meta:
        model = KnowledgeBaseLabel
        fields = ['id', 'name']
        read_only_fields = ['name']


class KnowledgeBaseLabelUpdateSerializer(BaseModelSerializer[KnowledgeBaseLabel]):
    """KnowledgeBaseLabel 目前只有 name 可以更新"""

    name = serializers.CharField()

    class Meta:
        model = KnowledgeBaseLabel
        fields = ['name']


class KnowledgeBaseCreateSerializer(BaseModelSerializer[KnowledgeBase], IdNameSerializerMixin):
    """KnowledgeBase 建立的序列化器"""

    embedding_model = serializers.PrimaryKeyRelatedField(
        queryset=EmbeddingModel.objects.all(),
        required=False,
        allow_null=True,
    )
    reranker_model = serializers.PrimaryKeyRelatedField(
        queryset=RerankerModel.objects.all(),
        required=False,
        allow_null=True,
    )
    name = serializers.CharField()
    description = serializers.CharField(required=False, allow_null=True)
    number_of_retrieved_chunks = serializers.IntegerField(
        required=False,
        default=12,
        min_value=1,
        help_text='提取的參考資料數量，預設為 12，最小值為 1',
    )
    sentence_window_size = serializers.IntegerField(
        required=False,
        default=2,
        min_value=0,
        help_text='RAG 擴增句子視窗大小，預設為 2，最小值為 0',
    )
    enable_hyde = serializers.BooleanField(
        required=False,
        default=False,
        help_text='啟用 HyDE，預設為 False',
    )
    similarity_cutoff = serializers.FloatField(
        required=False,
        default=0.0,
        min_value=0.0,
        max_value=1.0,
        help_text='相似度門檻，預設為 0.0，範圍為 0.0-1.0',
    )
    enable_rerank = serializers.BooleanField(
        required=False,
        default=True,
        help_text='是否啟用重新排序，預設為 True',
    )
    chatbots = IdNameSerializer(many=True, required=False, allow_null=True)

    class Meta:
        model = KnowledgeBase
        fields = [
            'id',
            'user',
            'organization',
            'embedding_model',
            'reranker_model',
            'name',
            'description',
            'number_of_retrieved_chunks',
            'sentence_window_size',
            'enable_hyde',
            'similarity_cutoff',
            'enable_rerank',
            'chatbots',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'user',
            'organization',
            'created_at',
            'updated_at',
            'id',
        ]

    def validate(self, attrs: dict) -> dict:
        request = self.context['request']
        user_id = request.user.id
        organization_id = request.organization_id

        attrs['chatbots'] = self.extract_ids_from_dict_list(
            input=attrs.get('chatbots', None),
            key='chatbots',
        )
        attrs['user_id'] = user_id
        attrs['organization_id'] = organization_id

        return attrs

    def create(self, validated_data: dict) -> KnowledgeBase:
        """建立 KnowledgeBase 並關聯 chatbots"""
        from whizchat.chatbots.models import Chatbot

        chatbot_ids = validated_data.pop('chatbots', [])
        knowledge_base_instance = super().create(validated_data)

        if chatbot_ids:
            chatbot_instances = Chatbot.objects.filter(
                id__in=chatbot_ids,
                organization_id=knowledge_base_instance.organization_id,
            )
            knowledge_base_instance.chatbots.add(*chatbot_instances)

        return knowledge_base_instance


class KnowledgeBaseSerializer(BaseModelSerializer[KnowledgeBase], IdNameSerializerMixin):
    """KnowledgeBase 序列化器"""

    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
        allow_null=True,
    )
    organization = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.all(),
        required=False,
        allow_null=True,
    )
    embedding_model = serializers.PrimaryKeyRelatedField(
        queryset=EmbeddingModel.objects.all(),
        required=False,
        allow_null=True,
    )
    reranker_model = serializers.PrimaryKeyRelatedField(
        queryset=RerankerModel.objects.all(),
        required=False,
        allow_null=True,
    )
    name = serializers.CharField()
    description = serializers.CharField(required=False, allow_null=True)
    number_of_retrieved_chunks = serializers.IntegerField(
        required=False,
        default=12,
        min_value=1,
        help_text='提取的參考資料數量，預設為 12，最小值為 1',
    )
    sentence_window_size = serializers.IntegerField(
        required=False,
        default=2,
        min_value=0,
        help_text='RAG 擴增句子視窗大小，預設為 2，最小值為 0',
    )
    enable_hyde = serializers.BooleanField(
        required=False,
        default=False,
        help_text='啟用 HyDE，預設為 False',
    )
    similarity_cutoff = serializers.FloatField(
        required=False,
        default=0.0,
        min_value=0.0,
        max_value=1.0,
        help_text='相似度門檻，預設為 0.0，範圍為 0.0-1.0',
    )
    enable_rerank = serializers.BooleanField(
        required=False,
        default=True,
        help_text='是否啟用重新排序，預設為 True',
    )
    labels = IdNameSerializer(many=True, required=False, allow_null=True, read_only=True)
    chatbots = IdNameSerializer(many=True, required=False, allow_null=True)
    files_count = serializers.SerializerMethodField()

    class Meta:
        model = KnowledgeBase
        fields = [
            'id',
            'user',
            'organization',
            'embedding_model',
            'reranker_model',
            'name',
            'description',
            'number_of_retrieved_chunks',
            'sentence_window_size',
            'enable_hyde',
            'similarity_cutoff',
            'enable_rerank',
            'labels',
            'chatbots',
            'files_count',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'user',
            'organization',
            'labels',
            'files_count',
            'created_at',
            'updated_at',
            'id',
        ]

    def get_files_count(self, obj: KnowledgeBase) -> int:
        """回傳此知識庫下的 ChatbotFile 數量"""
        return obj.files.count()

    def validate(self, attrs: dict) -> dict:
        request = self.context['request']
        user_id = request.user.id
        organization_id = request.organization_id

        attrs['user_id'] = user_id
        attrs['organization_id'] = organization_id
        attrs['chatbots'] = self.extract_ids_from_dict_list(
            input=attrs.get('chatbots', None),
            key='chatbots',
        )
        return attrs

    def _update_chatbots(
        self,
        instance: KnowledgeBase,
        submit_chatbot_ids: set[UUID],
        old_chatbot_ids: set[UUID],
    ) -> None:
        """更新 KnowledgeBase 並關聯 chatbots"""
        from whizchat.chatbots.models import Chatbot

        to_add_ids: set[UUID] = submit_chatbot_ids - old_chatbot_ids
        to_remove_ids: set[UUID] = old_chatbot_ids - submit_chatbot_ids

        if to_add_ids:
            chatbots_to_add = Chatbot.objects.filter(id__in=to_add_ids, organization_id=instance.organization_id)
            instance.chatbots.add(*chatbots_to_add)

        if to_remove_ids:
            chatbots_to_remove = Chatbot.objects.filter(id__in=to_remove_ids, organization_id=instance.organization_id)
            instance.chatbots.remove(*chatbots_to_remove)

    def update(self, instance: KnowledgeBase, validated_data: dict) -> KnowledgeBase:
        """更新 KnowledgeBase 並關聯 chatbots"""
        submit_chatbot_ids = validated_data.pop('chatbots')

        if submit_chatbot_ids is not None:
            submit_chatbot_ids: set[UUID] = set(submit_chatbot_ids)
            old_chatbot_ids: set[UUID] = set(instance.chatbots.values_list('id', flat=True))

            if submit_chatbot_ids != old_chatbot_ids:
                self._update_chatbots(
                    instance=instance,
                    submit_chatbot_ids=submit_chatbot_ids,
                    old_chatbot_ids=old_chatbot_ids,
                )

        return super().update(instance, validated_data)


class KnowledgeBaseFaqBatchDeleteSerializer(serializers.Serializer):
    ids = serializers.ListField(child=serializers.UUIDField(), required=False, allow_empty=True)

    def validate(self, attrs: dict) -> dict:
        """驗證要刪除的 FAQ ID 列表，如果未提供 ID 列表，則刪除所有 FAQ"""
        knowledge_base_pk = self.context.get('knowledge_base_pk')
        if not knowledge_base_pk:
            raise serializers.ValidationError({'detail': _('Missing knowledge_base_pk in context')})

        try:
            knowledge_base_instance = KnowledgeBase.objects.get(id=knowledge_base_pk)
        except KnowledgeBase.DoesNotExist:
            raise serializers.ValidationError({'detail': _('KnowledgeBase does not exist')})

        faq_ids = attrs.get('ids')
        if faq_ids:
            faq_instances = Faq.objects.filter(id__in=faq_ids, knowledge_base_id=knowledge_base_pk)
            if len(faq_ids) != faq_instances.count():
                raise serializers.ValidationError({'detail': _('Some FAQ IDs do not exist')})
            attrs['faq_instances'] = faq_instances
        else:
            attrs['faq_instances'] = Faq.objects.filter(knowledge_base_id=knowledge_base_pk)

        attrs['knowledge_base_instance'] = knowledge_base_instance
        return attrs
