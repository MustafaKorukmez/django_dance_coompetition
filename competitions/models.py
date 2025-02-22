from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from string import ascii_uppercase

# -----------------------------------
# 1) BASE / COMMON MODELS
# -----------------------------------

class BaseTimestampedModel(models.Model):
    """
    Projedeki tüm modellerin ortak zaman alanlarını sağlar.
    """
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Oluşturma Tarihi"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Güncelleme Tarihi"))

    class Meta:
        abstract = True


class CompetitionStatus(models.TextChoices):
    PLANNED = "planned", _("Planlandı")
    ACTIVE = "active", _("Aktif")
    COMPLETED = "completed", _("Tamamlandı")
    CANCELED = "canceled", _("İptal Edildi")


# -----------------------------------
# 2) COMPETITION & ROUND
# -----------------------------------

class Competition(BaseTimestampedModel):
    """
    Bir dans yarışması.
    Katılımcılar bu modele doğrudan değil, CompetitionParticipation üzerinden bağlanır.
    """
    name = models.CharField(_("Yarışma Adı"), max_length=200, db_index=True)
    style = models.CharField(_("Dans Tarzı"), max_length=100, blank=True)
    status = models.CharField(
        _("Durum"),
        max_length=10,
        choices=CompetitionStatus.choices,
        default=CompetitionStatus.PLANNED
    )
    total_rounds = models.PositiveIntegerField(
        _("Toplam Tur Sayısı"),
        validators=[MinValueValidator(1)],
        help_text=_("Yarışmanın kaç turdan oluşacağını belirtir.")
    )
    description = models.TextField(_("Açıklama"), blank=True)

    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"

    def advance_round(self, from_round_number):
        """
        Belirli bir turu kapatıp, pass_count kadar katılımcıyı bir sonraki tura taşı.
        Eğer katılımcı zaten sonraki tura eklenmişse get_or_create ile tekrar eklemez.
        """
        from_round = self.rounds.filter(round_number=from_round_number).first()
        if not from_round:
            return  # Tur bulunamadı
        
        to_round_number = from_round_number + 1
        to_round = self.rounds.filter(round_number=to_round_number).first()
        if not to_round:
            return  # Sonraki tur bulunamadı

        for group in from_round.groups.all():
            # RoundParticipation kayıtlarını puanlarına göre sırala
            round_participations = group.round_participations.all()
            sorted_by_score = sorted(
                round_participations, 
                key=lambda rp: rp.scores.first().ranking if rp.scores.exists() else 9999
            )
            passed_participants = sorted_by_score[:from_round.pass_count]
            
            # İlk grup veya en az dolu grubu seçme mantığı (örnek: ilk grup)
            if to_round.groups.exists():
                target_group = to_round.groups.first()
                for rp in passed_participants:
                    # Aynı katılımcı zaten eklenmişse tekrardan eklememek için get_or_create kullanıyoruz.
                    RoundParticipation.objects.get_or_create(
                        participant=rp.participant,
                        round=to_round,
                        defaults={"group": target_group}
                    )
        # İlgili turda pass_count kadar katılımcı sonraki tura taşınmış olur.

class Round(BaseTimestampedModel):
    """
    Yarışmanın tur bilgisi.
    """
    competition = models.ForeignKey(
        Competition,
        on_delete=models.CASCADE,
        related_name="rounds",
        verbose_name=_("Yarışma")
    )
    round_number = models.PositiveIntegerField(_("Tur Numarası"), db_index=True)
    round_name = models.CharField(
        _("Tur Adı"), max_length=100,
        blank=True, help_text=_("Örn: 1. Tur, Yarı Final, Final vb.")
    )
    group_count = models.PositiveIntegerField(
        _("Grup Sayısı"),
        validators=[MinValueValidator(1)]
    )
    pass_count = models.PositiveIntegerField(
        _("Her Gruptan bir sonraki tura kaç kişi geçsin,?"),
        validators=[MinValueValidator(1)]
    )
    is_last_round = models.BooleanField(_("Bu Tur Final Mi?"), default=False)

    class Meta:
        unique_together = (("competition", "round_number"),)
        ordering = ["competition", "round_number"]
        verbose_name = _("Tur")
        verbose_name_plural = _("Turlar")

    def __str__(self):
        display_name = self.round_name if self.round_name else f"{self.round_number}. Tur"
        return f"{self.competition.name} - {display_name}"

    def create_groups_automatically(self):
        """
        Bu tur için group_count kadar Group oluşturur.
        Gruplara isim verirken A, B, C... şeklinde ilerler.
        """
        existing_groups_count = self.groups.count()
        if existing_groups_count >= self.group_count:
            return

        for i in range(existing_groups_count, self.group_count):
            label = ascii_uppercase[i] if i < 26 else f"G{i+1}"
            Group.objects.create(
                round=self,
                name=f"Group {label}"
            )


# -----------------------------------
# 3) GROUP
# -----------------------------------

class Group(BaseTimestampedModel):
    """
    Bir tur içindeki grupları temsil eder.
    """
    round = models.ForeignKey(
        Round,
        on_delete=models.CASCADE,
        related_name="groups",
        verbose_name=_("Tur")
    )
    name = models.CharField(_("Grup Adı"), max_length=50)
    max_participants = models.PositiveIntegerField(
        _("Maksimum Katılımcı Sayısı"),
        default=10
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["round", "name"],
                name="unique_group_name_in_round"
            )
        ]
        verbose_name = _("Grup")
        verbose_name_plural = _("Gruplar")

    def __str__(self):
        return f"{self.round} / {self.name}"


# -----------------------------------
# 4) PARTICIPANT & COMPETITION PARTICIPATION
# -----------------------------------

class Participant(BaseTimestampedModel):
    """
    Genel katılımcı bilgisi; birden fazla yarışmaya katılabilir.
    """
    full_name = models.CharField(_("Ad Soyad"), max_length=150, db_index=True)
    email = models.EmailField(_("E-Posta"), blank=True, null=True)
    active = models.BooleanField(_("Aktif Katılımcı"), default=True)
    final_position = models.PositiveIntegerField(
        _("Final Sıralaması"),
        null=True, blank=True,
        help_text=_("Bu katılımcı yarışmayı kaçıncı bitirdi? (Opsiyonel)")
    )

    def __str__(self):
        return self.full_name


class CompetitionParticipation(BaseTimestampedModel):
    """
    Katılımcının belirli bir yarışmaya kaydını tutar.
    Kayıt anında, otomatik olarak yarışmanın 1. turuna eklemek için sinyal kullanılır.
    """
    participant = models.ForeignKey(
        Participant,
        on_delete=models.CASCADE,
        related_name="competition_participations",
        verbose_name=_("Katılımcı")
    )
    competition = models.ForeignKey(
        Competition,
        on_delete=models.CASCADE,
        related_name="competition_participations",
        verbose_name=_("Yarışma")
    )
    joined_at = models.DateTimeField(
        _("Yarışmaya Katılım Tarihi"), auto_now_add=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["participant", "competition"],
                name="unique_participant_in_competition"
            )
        ]
        verbose_name = _("Yarışma Katılımı")
        verbose_name_plural = _("Yarışma Katılımları")

    def __str__(self):
        return f"{self.participant} -> {self.competition}"


# -----------------------------------
# 5) ROUND PARTICIPATION, JURY, SCORE
# -----------------------------------

class RoundParticipation(BaseTimestampedModel):
    """
    Katılımcının, belli bir tur ve gruptaki varlığını temsil eder.
    """
    participant = models.ForeignKey(
        Participant,
        on_delete=models.CASCADE,
        related_name="round_participations",
        verbose_name=_("Katılımcı")
    )
    round = models.ForeignKey(
        Round,
        on_delete=models.CASCADE,
        related_name="round_participations",
        verbose_name=_("Tur")
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name="round_participations",
        verbose_name=_("Grup")
    )
    order_in_group = models.PositiveIntegerField(
        _("Grup İçindeki Sırası"),
        null=True,
        blank=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["participant", "round"],
                name="unique_participant_per_round"
            )
        ]
        verbose_name = _("Tur Katılımı")
        verbose_name_plural = _("Tur Katılımları")

    def __str__(self):
        return f"{self.participant} - {self.round} - {self.group}"


class Jury(BaseTimestampedModel):
    """
    Jüri bilgisi.
    """
    full_name = models.CharField(_("Jüri Ad Soyad"), max_length=150)
    email = models.EmailField(_("E-Posta"), unique=True)
    active = models.BooleanField(_("Aktif Jüri"), default=True)

    def __str__(self):
        return f"Jüri: {self.full_name}"


class Score(BaseTimestampedModel):
    """
    Jürinin RoundParticipation'a verdiği puan/sıralama.
    """
    jury = models.ForeignKey(
        Jury,
        on_delete=models.CASCADE,
        related_name="scores",
        verbose_name=_("Jüri")
    )
    round_participation = models.ForeignKey(
        RoundParticipation,
        on_delete=models.CASCADE,
        related_name="scores",
        verbose_name=_("Tur Katılımı")
    )
    ranking = models.PositiveIntegerField(
        _("Sıralama"),
        help_text=_("Grup içindeki sıralama. 1 = En yüksek")
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["jury", "round_participation"],
                name="unique_score_per_jury"
            )
        ]
        verbose_name = _("Jüri Oyu")
        verbose_name_plural = _("Jüri Oyları")

    def __str__(self):
        return f"[{self.jury}] {self.round_participation} => Sıra: {self.ranking}"


# -----------------------------------
# 6) SIGNALS
# -----------------------------------

@receiver(post_save, sender=Round)
def round_post_save_handler(sender, instance, created, **kwargs):
    """
    Round kaydı oluşturulduğunda, group_count kadar Group'u otomatik oluşturur.
    """
    if created:
        instance.create_groups_automatically()


@receiver(post_save, sender=CompetitionParticipation)
def competition_participation_post_save_handler(sender, instance, created, **kwargs):
    """
    CompetitionParticipation kaydı oluşturulduğunda,
    yarışmanın 1. turuna katılım ekler.
    """
    if created:
        competition = instance.competition
        participant = instance.participant

        first_round = competition.rounds.order_by("round_number").first()
        if not first_round:
            return

        groups_in_first_round = first_round.groups.all()
        if not groups_in_first_round.exists():
            return

        selected_group = min(
            groups_in_first_round,
            key=lambda g: g.round_participations.count()
        )

        RoundParticipation.objects.get_or_create(
            participant=participant,
            round=first_round,
            defaults={"group": selected_group}
        )


@receiver(pre_save, sender=RoundParticipation)
def check_group_capacity(sender, instance, **kwargs):
    """
    RoundParticipation kaydedilmeden önce, grup kapasitesini kontrol eder.
    """
    group = instance.group
    if not group:
        return

    current_count = group.round_participations.count()
    new_record = instance.pk is None

    if new_record and current_count >= group.max_participants:
        raise ValidationError("Bu grup dolu! Lütfen başka bir gruba ekleyin.")
