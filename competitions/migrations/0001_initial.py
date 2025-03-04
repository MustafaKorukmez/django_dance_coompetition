# Generated by Django 5.1.6 on 2025-02-22 13:11

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Competition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Oluşturma Tarihi')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Güncelleme Tarihi')),
                ('name', models.CharField(db_index=True, max_length=200, verbose_name='Yarışma Adı')),
                ('style', models.CharField(blank=True, max_length=100, verbose_name='Dans Tarzı')),
                ('status', models.CharField(choices=[('planned', 'Planlandı'), ('active', 'Aktif'), ('completed', 'Tamamlandı'), ('canceled', 'İptal Edildi')], default='planned', max_length=10, verbose_name='Durum')),
                ('total_rounds', models.PositiveIntegerField(help_text='Yarışmanın kaç turdan oluşacağını belirtir.', validators=[django.core.validators.MinValueValidator(1)], verbose_name='Toplam Tur Sayısı')),
                ('description', models.TextField(blank=True, verbose_name='Açıklama')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Jury',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Oluşturma Tarihi')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Güncelleme Tarihi')),
                ('full_name', models.CharField(max_length=150, verbose_name='Jüri Ad Soyad')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='E-Posta')),
                ('active', models.BooleanField(default=True, verbose_name='Aktif Jüri')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Participant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Oluşturma Tarihi')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Güncelleme Tarihi')),
                ('full_name', models.CharField(db_index=True, max_length=150, verbose_name='Ad Soyad')),
                ('email', models.EmailField(blank=True, max_length=254, null=True, verbose_name='E-Posta')),
                ('active', models.BooleanField(default=True, verbose_name='Aktif Katılımcı')),
                ('final_position', models.PositiveIntegerField(blank=True, help_text='Bu katılımcı yarışmayı kaçıncı bitirdi? (Opsiyonel)', null=True, verbose_name='Final Sıralaması')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Round',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Oluşturma Tarihi')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Güncelleme Tarihi')),
                ('round_number', models.PositiveIntegerField(db_index=True, verbose_name='Tur Numarası')),
                ('round_name', models.CharField(blank=True, help_text='Örn: 1. Tur, Yarı Final, Final vb.', max_length=100, verbose_name='Tur Adı')),
                ('group_count', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1)], verbose_name='Grup Sayısı')),
                ('pass_count', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1)], verbose_name='Bir Sonraki Tura Geçecek Kişi Sayısı')),
                ('is_last_round', models.BooleanField(default=False, verbose_name='Bu Tur Final Mi?')),
                ('competition', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rounds', to='competitions.competition', verbose_name='Yarışma')),
            ],
            options={
                'verbose_name': 'Tur',
                'verbose_name_plural': 'Turlar',
                'ordering': ['competition', 'round_number'],
                'unique_together': {('competition', 'round_number')},
            },
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Oluşturma Tarihi')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Güncelleme Tarihi')),
                ('name', models.CharField(max_length=50, verbose_name='Grup Adı')),
                ('max_participants', models.PositiveIntegerField(default=10, verbose_name='Maksimum Katılımcı Sayısı')),
                ('round', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='groups', to='competitions.round', verbose_name='Tur')),
            ],
            options={
                'verbose_name': 'Grup',
                'verbose_name_plural': 'Gruplar',
            },
        ),
        migrations.CreateModel(
            name='RoundParticipation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Oluşturma Tarihi')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Güncelleme Tarihi')),
                ('order_in_group', models.PositiveIntegerField(blank=True, null=True, verbose_name='Grup İçindeki Sırası')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='round_participations', to='competitions.group', verbose_name='Grup')),
                ('participant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='round_participations', to='competitions.participant', verbose_name='Katılımcı')),
                ('round', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='round_participations', to='competitions.round', verbose_name='Tur')),
            ],
            options={
                'verbose_name': 'Tur Katılımı',
                'verbose_name_plural': 'Tur Katılımları',
            },
        ),
        migrations.CreateModel(
            name='Score',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Oluşturma Tarihi')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Güncelleme Tarihi')),
                ('ranking', models.PositiveIntegerField(help_text='Grup içindeki sıralama. 1 = En yüksek', verbose_name='Sıralama')),
                ('jury', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='scores', to='competitions.jury', verbose_name='Jüri')),
                ('round_participation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='scores', to='competitions.roundparticipation', verbose_name='Tur Katılımı')),
            ],
            options={
                'verbose_name': 'Jüri Oyu',
                'verbose_name_plural': 'Jüri Oyları',
            },
        ),
        migrations.CreateModel(
            name='CompetitionParticipation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Oluşturma Tarihi')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Güncelleme Tarihi')),
                ('joined_at', models.DateTimeField(auto_now_add=True, verbose_name='Yarışmaya Katılım Tarihi')),
                ('competition', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='competition_participations', to='competitions.competition', verbose_name='Yarışma')),
                ('participant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='competition_participations', to='competitions.participant', verbose_name='Katılımcı')),
            ],
            options={
                'verbose_name': 'Yarışma Katılımı',
                'verbose_name_plural': 'Yarışma Katılımları',
                'constraints': [models.UniqueConstraint(fields=('participant', 'competition'), name='unique_participant_in_competition')],
            },
        ),
        migrations.AddConstraint(
            model_name='group',
            constraint=models.UniqueConstraint(fields=('round', 'name'), name='unique_group_name_in_round'),
        ),
        migrations.AddConstraint(
            model_name='roundparticipation',
            constraint=models.UniqueConstraint(fields=('participant', 'round'), name='unique_participant_per_round'),
        ),
        migrations.AddConstraint(
            model_name='score',
            constraint=models.UniqueConstraint(fields=('jury', 'round_participation'), name='unique_score_per_jury'),
        ),
    ]
