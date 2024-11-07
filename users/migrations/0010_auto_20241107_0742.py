# Generated by Django 5.1.1 on 2024-11-07 07:42

from django.db import migrations

def create_status(apps, schema_editor):
    UserChatStatus = apps.get_model('users', 'UserChatStatus')
    UserChatStatus.objects.create(name='created')
    UserChatStatus.objects.create(name='deleted')
    UserChatStatus.objects.create(name='blocked')

class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_remove_userchatparticipantmessage_read_by_receiver'),
    ]

    operations = [
        migrations.RunPython(create_status),
    ]
