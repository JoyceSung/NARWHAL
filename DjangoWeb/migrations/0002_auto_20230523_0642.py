# Generated by Django 3.2.18 on 2023-05-23 06:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DjangoWeb', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user_job',
            name='expression_level_status',
            field=models.CharField(default='WAITING', max_length=10),
        ),
        migrations.AddField(
            model_name='user_job',
            name='filtering_status',
            field=models.CharField(default='WAITING', max_length=10),
        ),
    ]
