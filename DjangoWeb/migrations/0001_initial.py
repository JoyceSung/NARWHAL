# Generated by Django 3.2.18 on 2023-05-15 08:27

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='bac_species',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('collection', models.CharField(default='NA', max_length=15)),
                ('file_name', models.CharField(default='NA', max_length=100)),
                ('tax_id', models.IntegerField(default=-1)),
                ('s_name', models.CharField(default='NA', max_length=120)),
            ],
        ),
        migrations.CreateModel(
            name='ip_log',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip', models.CharField(max_length=25)),
                ('country', models.CharField(default='NA', max_length=50)),
                ('functions', models.CharField(default='NA', max_length=25)),
                ('submission_time', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='User_Job',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.CharField(max_length=50)),
                ('upload_id', models.CharField(max_length=64)),
                ('ip', models.CharField(max_length=25)),
                ('mail', models.EmailField(max_length=254)),
                ('submission_time', models.DateTimeField(auto_now_add=True)),
                ('start_time', models.DateTimeField(auto_now_add=True)),
                ('end_time', models.DateTimeField(auto_now_add=True)),
                ('total_status', models.CharField(default='WAITING', max_length=10)),
                ('quality_check_status', models.CharField(default='WAITING', max_length=10)),
                ('hla_status', models.CharField(default='WAITING', max_length=10)),
                ('hla_result_status', models.CharField(default='WAITING', max_length=10)),
                ('gatk_status', models.CharField(default='WAITING', max_length=10)),
                ('somatic_status', models.CharField(default='WAITING', max_length=10)),
                ('germline_status', models.CharField(default='WAITING', max_length=10)),
                ('phasing_status', models.CharField(default='WAITING', max_length=10)),
                ('pvactools_status', models.CharField(default='WAITING', max_length=10)),
                ('dna_total_status', models.CharField(default='WAITING', max_length=10)),
                ('rna_total_status', models.CharField(default='WAITING', max_length=10)),
                ('error_log', models.CharField(default='NA', max_length=50)),
            ],
        ),
    ]
