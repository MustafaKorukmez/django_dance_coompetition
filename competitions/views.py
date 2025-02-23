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
