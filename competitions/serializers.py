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
'''
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
'''
from rest_framework import serializers
from .models import RoundParticipation, Score

class RoundParticipationSerializer(serializers.ModelSerializer):
    # Burada "round_participation" alanı, kaydın ID'sini temsil edecek şekilde ekleniyor.
    round_participation = serializers.IntegerField(source='id', read_only=True)
    participant_full_name = serializers.CharField(source='participant.full_name', read_only=True)
    average_ranking = serializers.SerializerMethodField()
    jury_score = serializers.SerializerMethodField()

    class Meta:
        model = RoundParticipation
        fields = [
            'round_participation',  # Bu alan sayesinde POST isteklerinde kullanılacak ID'yi görebileceksiniz.
            'participant', 
            'participant_full_name', 
            'group', 
            'order_in_group', 
            'average_ranking',
            'jury_score',  # İstek yapan jüri üyesinin verdiği oy (varsa)
        ]

    def get_average_ranking(self, obj):
        scores = obj.scores.all()
        if scores.exists():
            return sum(score.ranking for score in scores) / scores.count()
        return None

    def get_jury_score(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                score = obj.scores.get(jury=request.user)
                return score.ranking
            except Score.DoesNotExist:
                return None
        return None
