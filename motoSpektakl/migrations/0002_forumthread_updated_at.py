# Generated by Django 4.2.16 on 2024-10-01 01:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('motoSpektakl', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='forumthread',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
