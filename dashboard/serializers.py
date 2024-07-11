from rest_framework import serializers
from .models import Stage, CandidateStage
from candidate.models import Candidate


class CandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        fields = ['id', 'name', 'email']


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

