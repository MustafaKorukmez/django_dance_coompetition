from django.shortcuts import render, get_object_or_404
from .models import Competition

def final_results_view(request, competition_id):
    competition = get_object_or_404(Competition, id=competition_id)
    final_results = competition.get_final_results()
    return render(request, 'competition/final_results.html', {
        'competition': competition,
        'final_results': final_results,
    })
