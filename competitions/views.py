# views.py
from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from .models import Score
from .serializers import ScoreSerializer

class CreateScoreView(generics.CreateAPIView):
    queryset = Score.objects.all()
    serializer_class = ScoreSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Eğer kullanıcı jüri grubunda değilse, oy veremez.
        if not self.request.user.groups.filter(name='jury').exists():
            raise PermissionDenied("Bu işlem için jüri yetkiniz yok.")
        serializer.save(jury=self.request.user)


from rest_framework import generics
from .models import RoundParticipation
from .serializers import RoundParticipationSerializer

class GroupParticipantsListView(generics.ListAPIView):
    serializer_class = RoundParticipationSerializer

    def get_queryset(self):
        group_id = self.kwargs['group_id']
        return RoundParticipation.objects.filter(group_id=group_id)


from rest_framework.views import APIView
from rest_framework.response import Response
from .models import RoundParticipation

class GroupRankParticipantsView(APIView):
    def get(self, request, group_id):
        participations = RoundParticipation.objects.filter(group_id=group_id)
        ranking_list = []

        # Her katılımcı için ortalama puanı hesapla
        for rp in participations:
            scores = rp.scores.all()
            if scores.exists():
                avg_ranking = sum(score.ranking for score in scores) / scores.count()
            else:
                # Eğer oy yoksa çok yüksek bir değer atayarak listenin sonuna yerleştirelim
                avg_ranking = 9999
            ranking_list.append({'rp': rp, 'avg_ranking': avg_ranking})

        # Ortalamaya göre artan sırada (en düşük en iyi) sırala
        ranking_list.sort(key=lambda x: x['avg_ranking'])

        response_data = []
        for pos, item in enumerate(ranking_list, start=1):
            rp = item['rp']
            response_data.append({
                'position': pos,
                'participant_id': rp.participant.id,
                'participant_full_name': rp.participant.full_name,
                'average_ranking': item['avg_ranking']
            })

        return Response(response_data)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from .models import RoundParticipation, Score
from .serializers import ScoreSerializer

class GroupBulkVotingView(APIView):
    """
    Bir jüri üyesinin, belirli bir grup içindeki tüm katılımcılara ait round_participation kayıtlarına
    tek seferde oy vermesini sağlar. İstek payload'ı, her biri "round_participation" (ID) ve "ranking"
    içeren bir liste olmalıdır.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, group_id):
        # Kullanıcının "jury" grubunda olduğundan emin olun
        if not request.user.groups.filter(name='jury').exists():
            raise PermissionDenied("Bu işlem için jüri yetkiniz yok.")

        # İstek verisinin bir liste olduğundan emin olun
        votes = request.data
        if not isinstance(votes, list):
            return Response({"detail": "Payload bir liste olmalıdır."}, status=400)

        errors = {}
        created_scores = []
        
        for vote in votes:
            rp_id = vote.get("round_participation")
            ranking = vote.get("ranking")
            
            if rp_id is None or ranking is None:
                errors[vote] = "round_participation ve ranking alanları gereklidir."
                continue

            # Belirtilen round_participation kaydının, istenen grup içinde olduğundan emin olun
            try:
                rp = RoundParticipation.objects.get(id=rp_id, group_id=group_id)
            except RoundParticipation.DoesNotExist:
                errors[rp_id] = "Bu grup içinde geçerli bir RoundParticipation kaydı bulunamadı."
                continue

            # Aynı jüri için zaten bir oy varsa güncelle, yoksa oluştur
            score, created = Score.objects.update_or_create(
                jury=request.user,
                round_participation=rp,
                defaults={"ranking": ranking}
            )
            created_scores.append(score)

        if errors:
            return Response({"detail": "Bazı oylar kaydedilemedi.", "errors": errors}, status=400)

        serializer = ScoreSerializer(created_scores, many=True, context={'request': request})
        return Response(serializer.data, status=201)

from rest_framework import generics
from .models import RoundParticipation
from .serializers import RoundParticipationSerializer

class GroupParticipantsListView(generics.ListAPIView):
    serializer_class = RoundParticipationSerializer

    def get_queryset(self):
        group_id = self.kwargs['group_id']
        return RoundParticipation.objects.filter(group_id=group_id)


from rest_framework import generics
from .models import Round
from .serializers import RoundSerializer

class CompetitionRoundsListView(generics.ListAPIView):
    """
    Verilen yarışma ID'sine ait tüm turları listeler.
    """
    serializer_class = RoundSerializer

    def get_queryset(self):
        competition_id = self.kwargs.get('competition_id')
        return Round.objects.filter(competition_id=competition_id)
