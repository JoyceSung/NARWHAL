# Generated by Django 3.2.18 on 2023-08-15 14:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DjangoWeb', '0006_alter_user_job_data_preparation_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='user_job',
            name='shared_neoantigen_status',
            field=models.CharField(default='WAITING', max_length=50),
        ),
    ]
