from rest_framework import serializers
from .models import Stage, CandidateStage
from candidate.models import Candidate, ResumeAnalysis
import json


class ResumeAnalysisSerializer(serializers.ModelSerializer):
    specific_value = serializers.SerializerMethodField()

    class Meta:
        model = ResumeAnalysis
        fields = ['id', 'response_text', 'specific_value']

    def get_specific_value(self, obj):
        response_text = json.loads(obj.response_text)
        # Extract specific value based on key, e.g., 'key_name'
        if isinstance(response_text, dict):
            key_name = response_text.get('skills_matching', {})
            if isinstance(key_name, dict):
                return key_name.get('match', None)  # Extract 'nested_key' value
        return None

class CandidateSerializer(serializers.ModelSerializer):
    analysis = serializers.SerializerMethodField()

    class Meta:
        model = Candidate
        fields = ['id', 'name', 'email', 'contact', 'analysis']

    def get_analysis(self, obj):
        # Get `job_opening_id` from serializer context and filter analysis data
        job_opening_id = self.context.get('job_opening_id')
        analysis = obj.analysis.filter(job_opening_id=job_opening_id).first()
        return ResumeAnalysisSerializer(analysis).data if analysis else None


class CandidateStageSerializer(serializers.ModelSerializer):
    candidate = CandidateSerializer()
    class Meta:
        model = CandidateStage
        fields = ['id', 'candidate', 'stage', 'order']

class StageSerializer(serializers.ModelSerializer):
    candidates = CandidateStageSerializer(source='candidatestage_set', many=True, read_only=True)

    class Meta:
        model = Stage
        fields = ['id', 'name', 'order', 'job_opening', 'candidates']

