'''
from rest_framework import serializers
from .models import Group, Contestant, Ranking

class ContestantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contestant
        fields = ['id', 'name']

class GroupSerializer(serializers.ModelSerializer):
    contestants = ContestantSerializer(many=True)
    
    class Meta:
        model = Group
        fields = ['id', 'group_number', 'contestants']


class RankingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ranking
        fields = ['group', 'judge', 'rank']
'''
# serializers.py
from rest_framework import serializers
from .models import Score

class ScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Score
        fields = ['id', 'round_participation', 'ranking']
        read_only_fields = ['id']

    def create(self, validated_data):
        # İstek yapan kullanıcıyı jüri olarak ata.
        request = self.context.get('request')
        validated_data['jury'] = request.user
        return super().create(validated_data)
    
from rest_framework import serializers
from .models import RoundParticipation

class RoundParticipationSerializer(serializers.ModelSerializer):
    participant_full_name = serializers.CharField(source='participant.full_name', read_only=True)
    average_ranking = serializers.SerializerMethodField()

    class Meta:
        model = RoundParticipation
        fields = ['id', 'participant', 'participant_full_name', 'group', 'order_in_group', 'average_ranking']

    def get_average_ranking(self, obj):
        scores = obj.scores.all()
        if scores.exists():
            return sum(score.ranking for score in scores) / scores.count()
        return None
