# Generated by Django 5.1.6 on 2025-02-19 05:25

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
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('participant_count', models.PositiveIntegerField()),
                ('stage_count', models.PositiveIntegerField()),
                ('round_details', models.JSONField()),
            ],
        ),
        migrations.CreateModel(
            name='Contestant',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('competition', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contestants', to='competitions.competition')),
            ],
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('group_number', models.PositiveIntegerField()),
                ('competition', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='groups', to='competitions.competition')),
                ('contestants', models.ManyToManyField(related_name='groups', to='competitions.contestant')),
            ],
        ),
        migrations.CreateModel(
            name='Judge',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('competition', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='judges', to='competitions.competition')),
            ],
        ),
        migrations.CreateModel(
            name='Ranking',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('rank', models.JSONField()),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rankings', to='competitions.group')),
                ('judge', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rankings', to='competitions.judge')),
            ],
        ),
        migrations.CreateModel(
            name='Stage',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('stage_number', models.PositiveIntegerField()),
                ('group_size', models.PositiveIntegerField()),
                ('competition', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stages', to='competitions.competition')),
            ],
        ),
        migrations.AddField(
            model_name='group',
            name='stage',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='groups', to='competitions.stage'),
        ),
    ]
