# Generated by Django 5.1.1 on 2024-11-07 12:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0015_userchatparticipant_chat_deleted_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userchat',
            name='status',
        ),
        migrations.DeleteModel(
            name='UserChatStatus',
        ),
    ]