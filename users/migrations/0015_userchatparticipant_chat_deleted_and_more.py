# Generated by Django 5.1.1 on 2024-11-07 12:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0014_alter_userchatparticipant_last_read_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='userchatparticipant',
            name='chat_deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='userchatparticipant',
            name='last_blocked_at',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='userchatparticipant',
            name='chat_blocked',
            field=models.BooleanField(default=False, help_text='Whether the user blocked the chat'),
        ),
        migrations.AlterField(
            model_name='userchatparticipant',
            name='last_deleted_at',
            field=models.DateTimeField(help_text='Last time the user deleted the chat', null=True),
        ),
    ]
