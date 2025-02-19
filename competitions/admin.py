from django.contrib import admin
from .models import Competition, Contestant, Stage, Judge, Group, Ranking

class ContestantInline(admin.TabularInline):
    model = Contestant
    extra = 1  # Yeni katılımcı eklemek için boş satır sayısı

class StageInline(admin.TabularInline):
    model = Stage
    extra = 1

class JudgeInline(admin.TabularInline):
    model = Judge
    extra = 1


class RankingInline(admin.TabularInline):
    model = Ranking
    extra = 1

class GroupInline(admin.TabularInline):
    model = Group
    extra = 1

@admin.register(Competition)
class CompetitionAdmin(admin.ModelAdmin):
    list_display = ("name", "participant_count", "stage_count")
    inlines = [ContestantInline, StageInline, JudgeInline]  


admin.site.register(Judge)

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ("competition", "stage", "group_number")
