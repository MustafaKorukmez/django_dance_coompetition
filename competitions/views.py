from django.shortcuts import render, get_object_or_404
from .models import Round, Group

def round_list_view(request):
    """
    Tüm turların listesini gösteren örnek view.
    """
    rounds = Round.objects.select_related('competition').all()
    return render(request, 'competitions/round_list.html', {"rounds": rounds})


def group_detail_view(request, group_id):
    """
    Belirli bir grubun detaylarını gösteren örnek view.
    """
    group = get_object_or_404(Group.objects.select_related('round'), pk=group_id)
    return render(request, 'competitions/group_detail.html', {"group": group})
