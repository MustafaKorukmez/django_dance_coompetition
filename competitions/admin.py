from django.contrib import admin
from .models import (
    Competition,
    Round,
    Group,
    Participant,
    CompetitionParticipation,
    RoundParticipation,
    Jury,
    Score,
)

# ------------------------------------------------
# 1) INLINES
# ------------------------------------------------

class GroupInline(admin.TabularInline):
    """
    Round admin ekranında 'groups' ilişkisini inline göstermek için.
    """
    model = Group
    extra = 0
    fields = ("name", "max_participants")
    show_change_link = True


class RoundParticipationInline(admin.TabularInline):
    """
    Round admin ekranında veya Group admin ekranında, 
    o turdaki katılımcı ilişkilerini göstermek için kullanılabilir.
    """
    model = RoundParticipation
    extra = 0
    fields = ("participant", "group", "order_in_group")
    autocomplete_fields = ("participant", "group")


class ScoreInline(admin.TabularInline):
    """
    RoundParticipation admin ekranında, bu katılımcıya ait oy kayıtlarını göstermek için.
    """
    model = Score
    extra = 0
    fields = ("jury", "ranking")
    autocomplete_fields = ("jury",)


# ------------------------------------------------
# 2) ADMIN CLASSLARI
# ------------------------------------------------

@admin.register(Competition)
class CompetitionAdmin(admin.ModelAdmin):
    """
    Yarışma admin paneli.
    """
    list_display = ("name", "style", "status", "total_rounds", "created_at", "updated_at")
    list_filter = ("status", "style", "created_at", "updated_at")
    search_fields = ("name", "style")
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Genel Bilgiler", {
            "fields": ("name", "style", "status", "total_rounds", "description")
        }),
        ("Tarih Bilgileri", {
            "fields": ("created_at", "updated_at")
        }),
    )

    actions = ["mark_as_canceled", "calculate_final_positions"]

    def mark_as_canceled(self, request, queryset):
        """
        Seçili yarışmaları iptal et (örnek).
        """
        updated = queryset.update(status="canceled")
        self.message_user(request, f"{updated} yarışma iptal edildi.")
    mark_as_canceled.short_description = "Seçili yarışmaları İptal Et"

    def calculate_final_positions(self, request, queryset):
        """
        Seçili yarışmaların final turundaki (is_last_round=True) katılımcılarının final sıralamasını hesaplar.
        
        İşlem adımları:
          1. Yarışmanın final turu bulunur.
          2. Final turundaki tüm RoundParticipation kayıtları alınır.
          3. Her kaydın Score'larından ortalama sıralama (ranking) hesaplanır.
             (Score kaydı yoksa, ortalama değer olarak yüksek bir değer atanır.)
          4. Ortalama değere göre sıralama yapılır; en düşük ortalamaya sahip olan 1. sırayı alır.
          5. Katılımcının final_position alanı güncellenir.
        """
        for competition in queryset:
            final_round = competition.rounds.filter(is_last_round=True).first()
            if not final_round:
                self.message_user(request, f"{competition} için final turu bulunamadı.", level="error")
                continue

            participations = list(final_round.round_participations.all())
            if not participations:
                self.message_user(request, f"{competition} için final katılımcısı bulunamadı.", level="error")
                continue

            ranking_list = []
            for rp in participations:
                scores = rp.scores.all()
                if scores.exists():
                    avg_ranking = sum(score.ranking for score in scores) / scores.count()
                else:
                    avg_ranking = 9999  # Oy girilmemişse en kötü sıralama varsayılır.
                ranking_list.append((rp, avg_ranking))

            # Ortalama sıralamaya göre artan sırada düzenle (en düşük en iyi)
            ranking_list.sort(key=lambda x: x[1])
            for pos, (rp, avg) in enumerate(ranking_list, start=1):
                rp.participant.final_position = pos
                rp.participant.save()
            self.message_user(request, f"{competition} için final sıralaması başarıyla güncellendi.")
    calculate_final_positions.short_description = "Final sıralamasını hesapla ve güncelle"


@admin.register(Round)
class RoundAdmin(admin.ModelAdmin):
    """
    Tur yönetimi.
    """
    list_display = ("competition", "round_number", "round_name", "group_count", "pass_count", "is_last_round")
    list_filter = ("competition", "is_last_round", "created_at", "updated_at")
    search_fields = ("competition__name", "round_name")
    readonly_fields = ("created_at", "updated_at")
    inlines = [GroupInline, RoundParticipationInline]

    fieldsets = (
        ("Tur Bilgisi", {
            "fields": ("competition", "round_number", "round_name",
                       "group_count", "pass_count", "is_last_round")
        }),
        ("Tarih Bilgileri", {
            "fields": ("created_at", "updated_at")
        }),
    )

    actions = ["advance_this_round"]

    def advance_this_round(self, request, queryset):
        """
        Seçili Round kayıtlarına ait competition'da 'advance_round' fonksiyonunu çağırır.
        Hata durumunda ilgili uyarıyı verir.
        """
        success_count = 0
        for r in queryset:
            try:
                r.competition.advance_round(r.round_number)
                success_count += 1
            except Exception as e:
                self.message_user(request, f"{r} için geçiş işlemi sırasında hata: {e}", level="error")
        if success_count:
            self.message_user(request, f"{success_count} tur için bir sonraki tura geçiş işlemi yapıldı.")
    advance_this_round.short_description = "Seçili turları kapatıp bir sonraki tura geç"


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    """
    Grup yönetimi.
    """
    list_display = ("round", "name", "max_participants", "created_at", "updated_at")
    list_filter = ("round__competition", "round", "created_at", "updated_at")
    search_fields = ("name", "round__round_name")
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Grup Bilgisi", {
            "fields": ("round", "name", "max_participants")
        }),
        ("Tarih Bilgileri", {
            "fields": ("created_at", "updated_at")
        }),
    )


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    """
    Katılımcı yönetimi.
    """
    list_display = ("full_name", "email", "active", "final_position", "created_at", "updated_at")
    list_filter = ("active", "created_at", "updated_at")
    search_fields = ("full_name", "email")
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Katılımcı Bilgisi", {
            "fields": ("full_name", "email", "active", "final_position")
        }),
        ("Tarih Bilgileri", {
            "fields": ("created_at", "updated_at")
        }),
    )


@admin.register(CompetitionParticipation)
class CompetitionParticipationAdmin(admin.ModelAdmin):
    """
    Katılımcının hangi yarışmaya katıldığını yöneten model.
    """
    list_display = ("participant", "competition", "joined_at", "created_at", "updated_at")
    list_filter = ("competition", "created_at", "updated_at")
    search_fields = ("participant__full_name", "competition__name")
    readonly_fields = ("joined_at", "created_at", "updated_at")

    fieldsets = (
        ("Katılım Bilgisi", {
            "fields": ("participant", "competition")
        }),
        ("Tarih Bilgileri", {
            "fields": ("joined_at", "created_at", "updated_at")
        }),
    )


@admin.register(RoundParticipation)
class RoundParticipationAdmin(admin.ModelAdmin):
    """
    Katılımcı <-> Tur <-> Grup eşleşmesi.
    """
    list_display = ("participant", "round", "group", "order_in_group", "created_at", "updated_at")
    list_filter = ("round__competition", "round", "group", "created_at", "updated_at")
    search_fields = ("participant__full_name", "group__name", "round__round_name")
    readonly_fields = ("created_at", "updated_at")
    inlines = [ScoreInline]

    fieldsets = (
        ("Katılım Bilgisi", {
            "fields": ("participant", "round", "group", "order_in_group")
        }),
        ("Tarih Bilgileri", {
            "fields": ("created_at", "updated_at")
        }),
    )


@admin.register(Jury)
class JuryAdmin(admin.ModelAdmin):
    """
    Jüri bilgisi.
    """
    list_display = ("full_name", "email", "active", "created_at", "updated_at")
    list_filter = ("active", "created_at", "updated_at")
    search_fields = ("full_name", "email")
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Jüri Bilgisi", {
            "fields": ("full_name", "email", "active")
        }),
        ("Tarih Bilgileri", {
            "fields": ("created_at", "updated_at")
        }),
    )


@admin.register(Score)
class ScoreAdmin(admin.ModelAdmin):
    """
    Jürinin oy/sıralama kayıtları.
    """
    list_display = ("jury", "round_participation", "ranking", "created_at", "updated_at")
    list_filter = ("jury", "round_participation__round__competition", "created_at", "updated_at")
    search_fields = ("jury__full_name", "round_participation__participant__full_name")
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Oy Bilgisi", {
            "fields": ("jury", "round_participation", "ranking")
        }),
        ("Tarih Bilgileri", {
            "fields": ("created_at", "updated_at")
        }),
    )
