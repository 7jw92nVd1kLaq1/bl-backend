# Generated by Django 5.1.1 on 2024-10-10 03:56

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0002_alter_gamechat_id_game_gamechat_game_linescore'),
    ]

    operations = [
        migrations.AlterField(
            model_name='linescore',
            name='line_score_id',
            field=models.CharField(default='asdfasdfasdf', editable=False, max_length=100, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='linescore',
            name='line_score_id',
            field=models.UUIDField(default=uuid.uuid4, help_text='Unique identifier for the line score entry.', primary_key=True, serialize=False),
        ),
    ]
