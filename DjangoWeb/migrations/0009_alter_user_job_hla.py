# Generated by Django 3.2.18 on 2023-08-18 13:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DjangoWeb', '0008_user_job_hla'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user_job',
            name='hla',
            field=models.CharField(default='sample_name', max_length=254),
        ),
    ]