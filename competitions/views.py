from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Stage, Group
from .serializers import GroupSerializer
from .utils import split_contestants_into_groups

class SplitContestantsIntoGroupsAPIView(APIView):
    """
    Belirtilen etap için yarışmacıları istenilen grup boyutuna göre bölüp grupları otomatik numaralandırır.
    
    Beklenen POST verisi:
    {
        "stage_id": <etap_id>,
        "randomize": true  // opsiyonel, varsayılan True
    }
    """
    
    def post(self, request, format=None):
        stage_id = request.data.get("stage_id")
        randomize = request.data.get("randomize", True)
        
        if not stage_id:
            return Response({"error": "stage_id gereklidir."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            stage = Stage.objects.get(id=stage_id)
            
            # ⚠️ Eğer gruplar zaten oluşturulmuşsa mevcut grupları döndür
            if stage.is_grouped:
                existing_groups = Group.objects.filter(stage=stage)
                serializer = GroupSerializer(existing_groups, many=True)
                return Response({
                    "message": "Bu etap için gruplar zaten oluşturulmuş. Mevcut gruplar döndürülüyor.",
                    "groups": serializer.data
                }, status=status.HTTP_200_OK)
            
        except Stage.DoesNotExist:
            return Response({"error": "Belirtilen etap bulunamadı."}, status=status.HTTP_404_NOT_FOUND)
        
        # Grupları oluşturacak fonksiyonu çağırıyoruz
        groups = split_contestants_into_groups(stage, randomize=randomize)
        
        # Etap için grupların oluşturulduğunu işaretle
        stage.is_grouped = True
        stage.save()
        
        # Oluşturulan grupları serileştirip döndürüyoruz
        serializer = GroupSerializer(groups, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError
from .models import Group, Judge, Ranking, Contestant
from .serializers import RankingSerializer

class RankGroupAPIView(APIView):
    """
    Jüri, belirli bir grup için yarışmacıları sıralar.
    
    Beklenen POST verisi:
    {
        "group_id": <grup_id>,
        "judge_id": <juri_id>,
        "rank": [<yarışmacı_id>, <yarışmacı_id>, ...]
    }
    """

    def post(self, request, format=None):
        group_id = request.data.get("group_id")
        judge_id = request.data.get("judge_id")
        rank = request.data.get("rank")

        # Eksik veri kontrolü
        if not (group_id and judge_id and rank):
            return Response({"error": "Tüm alanlar gereklidir."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            group = Group.objects.get(id=group_id)
            judge = Judge.objects.get(id=judge_id)

            # Grubun yarışmacılarını al
            group_contestant_ids = set(group.contestants.values_list('id', flat=True))

            # 🔴 Hatalı yarışmacı kontrolü
            if not set(rank).issubset(group_contestant_ids):
                return Response({"error": "Sıralanan yarışmacılar bu gruba ait değil."}, status=status.HTTP_400_BAD_REQUEST)

            # Aynı jüri, aynı grup için sıralama yapmış mı? Eğer yapmışsa güncelle
            ranking, created = Ranking.objects.update_or_create(
                group=group,
                judge=judge,
                defaults={'rank': rank}
            )

            serializer = RankingSerializer(ranking)
            if created:
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response({"message": "Sıralama güncellendi.", "data": serializer.data}, status=status.HTTP_200_OK)

        except Group.DoesNotExist:
            return Response({"error": "Grup bulunamadı."}, status=status.HTTP_404_NOT_FOUND)
        except Judge.DoesNotExist:
            return Response({"error": "Jüri bulunamadı."}, status=status.HTTP_404_NOT_FOUND)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count
from .models import Stage, Group, Ranking, Contestant

class CompleteStageAPIView(APIView):
    """
    Bir etabı tamamlar ve jüri değerlendirmelerine göre yarışmacıları bir sonraki etaba taşır.

    Beklenen POST verisi:
    {
        "stage_id": <etap_id>
    }

    Dönen JSON:
    {
        "message": "Etap tamamlandı ve bir sonraki etap için yarışmacılar belirlendi.",
        "next_stage_id": <yeni_etap_id>,
        "selected_contestants": [<contestant_id>, <contestant_id>, ...]
    }
    """

    def post(self, request, format=None):
        stage_id = request.data.get("stage_id")

        if not stage_id:
            return Response({"error": "stage_id gereklidir."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            stage = Stage.objects.get(id=stage_id)
            competition = stage.competition

            # Eğer etap zaten tamamlandıysa hata döndür
            if stage.is_finished:
                return Response({"error": "Bu etap zaten tamamlandı!","next_stage_id" : stage_id+1 }, status=status.HTTP_400_BAD_REQUEST)

            # Tüm grupları al
            groups = Group.objects.filter(stage=stage)

            # Eğer bu etapta hiç grup yoksa hata döndür
            if not groups.exists():
                return Response({"error": "Bu etapta herhangi bir grup bulunmuyor!"}, status=status.HTTP_400_BAD_REQUEST)

            # **1️⃣ Tüm gruplar için jüri değerlendirmesi yapıldı mı?**
            for group in groups:
                if not Ranking.objects.filter(group=group).exists():
                    return Response({"error": f"{group} için jüri değerlendirmeleri eksik!"}, status=status.HTTP_400_BAD_REQUEST)

            # **2️⃣ Yarışmacıların toplam puanlarını hesapla**
            contestant_scores = {}
            for group in groups:
                rankings = Ranking.objects.filter(group=group)

                for ranking in rankings:
                    for index, contestant_id in enumerate(ranking.rank):
                        if contestant_id not in contestant_scores:
                            contestant_scores[contestant_id] = 0
                        contestant_scores[contestant_id] += index + 1  # Sıralama puanı: 1. sıradaki 1 puan alır, 2. sıradaki 2 puan alır...

            # **3️⃣ Yarışmacıları en düşük puandan en yüksek puana sırala**
            sorted_contestants = sorted(contestant_scores.items(), key=lambda x: x[1])

            # **4️⃣ Adminin belirlediği sayıda yarışmacıyı seç**
            selected_contestants_ids = [int(c[0]) for c in sorted_contestants[:stage.contestants_to_next_stage]]
            selected_contestants = Contestant.objects.filter(id__in=selected_contestants_ids)

            # **5️⃣ Bir sonraki etabı oluştur**
            next_stage_number = stage.stage_number + 1
            next_stage, created = Stage.objects.get_or_create(
                competition=competition,
                stage_number=next_stage_number,
                defaults={"group_size": stage.group_size, "contestants_to_next_stage": stage.contestants_to_next_stage}
            )

            # **6️⃣ Yeni etap için grupları oluştur**
            new_group_size = next_stage.group_size
            groups_created = []
            for i in range(0, len(selected_contestants), new_group_size):
                group_number = (i // new_group_size) + 1
                new_group = Group.objects.create(
                    competition=competition,
                    stage=next_stage,
                    group_number=group_number
                )
                new_group.contestants.set(selected_contestants[i:i + new_group_size])
                groups_created.append(new_group)

            # Etabı tamamlanmış olarak işaretle
            stage.is_finished = True
            stage.save()

            return Response({
                "message": "Etap tamamlandı ve bir sonraki etap için yarışmacılar belirlendi.",
                "next_stage_id": next_stage.id,
                "selected_contestants": list(selected_contestants.values("id", "name")),
                "new_groups": [group.id for group in groups_created]
            }, status=status.HTTP_200_OK)

        except Stage.DoesNotExist:
            return Response({"error": "Belirtilen etap bulunamadı!"}, status=status.HTTP_404_NOT_FOUND)
