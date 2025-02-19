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
