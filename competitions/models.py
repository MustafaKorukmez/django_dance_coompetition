from django.db import models
import random

class Competition(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, verbose_name="Yarışma Adı")
    participant_count = models.PositiveIntegerField(verbose_name="Katılımcı Sayısı")
    stage_count = models.PositiveIntegerField(verbose_name="Etap Sayısı")

    class Meta:
        verbose_name = "Yarışma"
        verbose_name_plural = "Yarışmalar"

    def __str__(self):
        return self.name

class Contestant(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, verbose_name="Katılımcı Adı")
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name='contestants', verbose_name="Yarışma")

    class Meta:
        verbose_name = "Katılımcı"
        verbose_name_plural = "Katılımcılar"

    def __str__(self):
        return self.name


class Judge(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, verbose_name="Hakem Adı")
    password = models.CharField(max_length=255, verbose_name="Hakem Şifresi", default="123")  
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name='judges', verbose_name="Yarışma")

    class Meta:
        verbose_name = "Hakem"
        verbose_name_plural = "Hakemler"

    def __str__(self):
        return self.name



class Stage(models.Model):
    id = models.AutoField(primary_key=True)
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name='stages', verbose_name="Yarışma")
    stage_number = models.PositiveIntegerField(verbose_name="Etap Numarası", blank=True, null=True)
    group_size = models.PositiveIntegerField(verbose_name="Grup Boyutu")
    contestants_to_next_stage = models.PositiveIntegerField(verbose_name="Sonraki Etapa Geçecek Katılımcı Sayısı")
    is_grouped = models.BooleanField(default=False, verbose_name="Gruplar Oluşturuldu mu?")
    is_finished = models.BooleanField(default=False, verbose_name="Etap bitti mi")


    class Meta:
        verbose_name = "Etap"
        verbose_name_plural = "Etaplar"

    def __str__(self):
        return f"{self.competition.name} - Etap {self.stage_number}"



class Group(models.Model):
    id = models.AutoField(primary_key=True)
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name='groups', verbose_name="Yarışma")
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE, related_name='groups', verbose_name="Etap")
    group_number = models.PositiveIntegerField(verbose_name="Grup Numarası")
    contestants = models.ManyToManyField(Contestant, related_name='groups', verbose_name="Katılımcılar")

    class Meta:
        verbose_name = "Grup"
        verbose_name_plural = "Gruplar"

    def __str__(self):
        return f"{self.competition.name} - Etap {self.stage.stage_number} - Grup {self.group_number}"

        return f"{self.competition.name} - Etap {self.stage.stage_number} - Grup {self.group_number}"


class Ranking(models.Model):
    id = models.AutoField(primary_key=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='rankings', verbose_name="Grup")
    judge = models.ForeignKey(Judge, on_delete=models.CASCADE, related_name='rankings', verbose_name="Hakem")
    rank = models.JSONField(verbose_name="Sıralama")  # Yarışmacı ID'lerinin listesi tutulur

    class Meta:
        verbose_name = "Sıralama"
        verbose_name_plural = "Sıralamalar"
        unique_together = ('group', 'judge')  # Aynı jüri aynı grubu sadece bir kez değerlendirebilir

    def clean(self):
        """
        Ekstra doğrulamalar:
        - JSON sıralamasında sadece o gruba ait yarışmacılar bulunmalı.
        """
        group_contestant_ids = set(self.group.contestants.values_list('id', flat=True))
        if not set(self.rank).issubset(group_contestant_ids):
            raise ValidationError("Sıralama yalnızca bu gruptaki yarışmacıları içermelidir.")

    def __str__(self):
        return f"{self.group} için {self.judge.name} tarafından yapılan sıralama"
