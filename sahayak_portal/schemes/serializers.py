import json
from rest_framework import serializers
from .models import Scheme ,Feedback

class SchemeSerializer(serializers.ModelSerializer):
    eligibility_criteria = serializers.SerializerMethodField()
    documents_required = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()

    class Meta:
        model = Scheme
        fields = '__all__'

    def get_eligibility_criteria(self, obj):
        return [line.strip() for line in obj.eligibility_criteria.split('\n') if line.strip()]

    def get_documents_required(self, obj):
        return [line.strip() for line in obj.documents_required.split('\n') if line.strip()]

    def get_tags(self, obj):
        return [line.strip() for line in obj.tags.split('\n') if line.strip()]

class SchemeSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Scheme
        fields = ['id', 'title', 'description', 'tags', 'state']  # region = state

# ✅ Full Detail Serializer – for fetching by UID
class SchemeDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scheme
        fields = '__all__'

# ✅ Feedback Serializer
class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ['id', 'scheme', 'feedback_text', 'rating', 'submitted_at']