import uuid

from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
import re
from tempfile import gettempdir
from pathlib import Path
import os
import gzip
import ast
import shutil
from django.core.files.storage import FileSystemStorage
import json
from django.conf import settings
from .models import User_Job,ip_log,bac_species
import subprocess as sp
import sys
from django.core.mail import send_mail
#from django_q.tasks import async, result,async_chain,Chain
import asyncio
from os import path, environ, makedirs
import subprocess as sp
import datetime
from datetime import timedelta
from django.http import JsonResponse
import pandas as pd
from django.http import FileResponse
from .googledrive_downloader import GoogleDriveDownloader
import wget
from urllib import request
import socket
import requests, requests_ftp
from django.views.decorators.csrf import csrf_exempt
from ipware import get_client_ip
from geolite2 import geolite2
from django_q.tasks import async_task, result,async_chain,Chain





# UPLOAD_BASE_PATH = gettempdir()
# UPLOAD_BASE_PATH = os.getcwd()

UPLOAD_BASE_PATH = os.getcwd() + "/assets/file-uploads-temp"
TMP_BASE_PATH = os.getcwd() + "/assets/file-uploads-temp/tmp/"
DATA = settings.OUTPUT_BASE_DIR
DATABASE_PATH = os.getcwd() + "/TSA_tool/data/" 
HOME_PATH =os.getcwd() + "/anaconda3/bin/" 
web_url = settings.WEB_URL
reader = geolite2.reader()
from_email = settings.DEFAULT_FROM_EMAIL


# Create your views here.
error_map={
"QC":"Quality Control",
"HLA_typing":"HLA Genotyping",
"SYSTEM":"System Error"
}

def _is_path_exist(dir, error_msg=False):
    if dir == None: return False
    elif path.exists(dir): return True
    #if error_msg: logger.error(dir+": No such file or directory\n")
    else: return False

def get_ip():
    response = requests.get('https://api64.ipify.org?format=json').json()
    return response["ip"]


def get_location():
    ip_address = get_ip()
    response = requests.get(f'https://ipapi.co/{ip_address}/json/').json()
    location_data = {
        "ip": ip_address,
        "city": response.get("city"),
        "region": response.get("region"),
        "country": response.get("country_name")
    }
    return location_data


def index(request):
    return render(request, 'homepage.html')


def hlagenotyping(request):
    return render(request, 'HLA_genotyping.html')


def find_overlapped(request):
    hla_df = pd.read_csv(settings.HLA_LIST, sep="\t", engine='python')
    hla_df = hla_df[hla_df.columns[0]]
    hla_list = hla_df.values.tolist()
    return render(request, 'find_overlapped.html',
                  {'hla_list': hla_list})


def homepage(request):
    return render(request, 'homepage.html')


def neoantigen_identification(request):
    #load lists of HLA databases
    hla_df = pd.read_csv(settings.HLA_LIST, sep="\t", engine='python')
    hla_df = hla_df[hla_df.columns[0]]
    hla_list = hla_df.values.tolist()
    return render(request, 'Neoantigen_identification.html',
                  {'hla_list': hla_list})


def tutorial(request):
    return render(request, 'tutorial.html')

def guide(request):
    return render(request, 'guide.html')


@csrf_exempt
def confirmed_sample_names(request):
    if request.method == "POST":
        sample_names = request.POST.getlist("sampleNames[]")
        try:
            upload_id = re.sub(r"[\W]", "", request.POST.get('upload_id'))
            if upload_id == '':
                error_message = "You should upload files first."
                return JsonResponse({"error": error_message}, status=400)
            else:
                upload_path = str(Path(UPLOAD_BASE_PATH).resolve().joinpath(upload_id))
                files = os.listdir(upload_path)
                tsv_file_count = sum(1 for file in files if file.lower().endswith(".tsv"))
                if int(tsv_file_count) != int(len(sample_names)):
                    error_message = "The number of sample names should be equal to the number of files."
                    return JsonResponse({"error": error_message}, status=400)
                if int(tsv_file_count) < 2:
                    error_message = "Please upload at least 2 files."
                    return JsonResponse({"error": error_message}, status=400)
            if User_Job.objects.filter(user_id=upload_id).exists():
                user = User_Job.objects.filter(user_id=upload_id)[0]
                user.sample_names=sample_names     
                user.save(update_fields=['sample_names'])
            else:
                User_Job.objects.create(user_id=upload_id,
                                upload_id=upload_id,
                                sample_names=sample_names)
            response_data = {"message": "Sample names received successfully."}
            return JsonResponse(response_data)
        
        except:
            error_message = "The number of sample names should be equal to the number of files."
            return JsonResponse({"error": error_message}, status=400)
        
        


def about(request):
    #load lists of updates, tools and databases
    updates_list = pd.read_csv(settings.UPDATES_LIST, sep="\t", engine='python').values.tolist()
    
    tools_df = pd.read_csv(settings.TOOLS_LIST, sep="\t", engine='python')
    tools_df = tools_df[tools_df.columns[:4]]
    tools_list = tools_df.values.tolist()

    demo_data_list = pd.read_csv(settings.DEMO_LIST, sep="\t", engine='python').values.tolist()
    
    databases_df = pd.read_csv(settings.DATABASES_LIST, sep="\t", engine='python')
    databases_df = databases_df[databases_df.columns[:3]]
    databases_list = databases_df.values.tolist()
    return render(request, 'about.html',
                  {'updates_list': updates_list,
                   'tools_list': tools_list,
                   'databases_list': databases_list,
                   'demo_data_list':demo_data_list})


def test_data_upload(request):
    return render(request, 'test_data_upload.html')

def base(request):
    return render(request, 'base.html')


def data_upload(request):
    if request.method == 'POST':
        upload_id = re.sub(r"[\W]", "", request.POST.get('upload_id'))
        if upload_id == '':
            return HttpResponse('ERROR! Upload ID is missing.')
        upload_path = str(Path(UPLOAD_BASE_PATH).resolve().joinpath(upload_id))
        new_file_name = 'undefined_format'
        if 'uploadfile_type1' in request.POST:
            new_file_name = 'N.' + request.POST.get('uploadfile_type1') + '.fastq.gz'
        elif 'uploadfile_type2' in request.POST:
            new_file_name = 'N.' + request.POST.get('uploadfile_type2') + '.fastq.gz'
        elif 'uploadfile_type1_dna_tumor' in request.POST:
            new_file_name = 'T.dna.' + request.POST.get('uploadfile_type1_dna_tumor') + '.fastq.gz'
        elif 'uploadfile_type2_dna_tumor' in request.POST:
            new_file_name = 'T.dna.' + request.POST.get('uploadfile_type2_dna_tumor') + '.fastq.gz'
        elif 'uploadfile_type1_dna_normal' in request.POST:
            new_file_name = 'N.dna.' + request.POST.get('uploadfile_type1_dna_normal') + '.fastq.gz'
        elif 'uploadfile_type2_dna_normal' in request.POST:
            new_file_name = 'N.dna.' + request.POST.get('uploadfile_type2_dna_normal') + '.fastq.gz'
        elif 'uploadfile_dna_mass' in request.POST:
            new_file_name = 'dna.mass.fasta'
        try:
            upload_raw_file = upload_path + '/' + new_file_name
            file = request.FILES['myfile']
            if not os.path.exists(upload_path):
                os.makedirs(upload_path)
            if new_file_name == 'dna.mass.fasta':
                if file.name.endswith('.gz'):
                    with open(upload_raw_file, 'wb+') as destination:
                        with gzip.GzipFile(fileobj=file) as source:
                            shutil.copyfileobj(source, destination) 
            else: 
                with open(upload_raw_file, 'wb+') as destination:
                    for chunk in file.chunks():
                        destination.write(chunk)
            file.close()
        except:
            return HttpResponse('ERROR! System error.')
        return HttpResponse(json.dumps(request.POST))


def delete_upload(request):
    if request.method == 'POST':
        upload_id = re.sub(r"[\W]", "", request.POST.get('upload_id'))
        if upload_id == '':
            return HttpResponse('ERROR! Upload ID is missing.')
        upload_path = str(Path(UPLOAD_BASE_PATH).resolve().joinpath(upload_id))
        new_file_name = 'undefined_format'
        if 'uploadfile_type1' in request.POST:
            new_file_name = 'N.' + request.POST.get('uploadfile_type1') + '.fastq.gz'
        elif 'uploadfile_type2' in request.POST:
            new_file_name = 'N.' + request.POST.get('uploadfile_type2') + '.fastq.gz'
        elif 'uploadfile_type1_dna_tumor' in request.POST:
            new_file_name = 'T.dna.' + request.POST.get('uploadfile_type1_dna_tumor') + '.fastq.gz'
        elif 'uploadfile_type2_dna_tumor' in request.POST:
            new_file_name = 'T.dna.' + request.POST.get('uploadfile_type2_dna_tumor') + '.fastq.gz'
        elif 'uploadfile_type1_dna_normal' in request.POST:
            new_file_name = 'N.dna.' + request.POST.get('uploadfile_type1_dna_normal') + '.fastq.gz'
        elif 'uploadfile_type2_dna_normal' in request.POST:
            new_file_name = 'N.dna.' + request.POST.get('uploadfile_type2_dna_normal') + '.fastq.gz'
        elif 'uploadfile_dna_mass' in request.POST:
            new_file_name = 'dna.mass.fasta'
        
        upload_raw_file = upload_path + '/' + new_file_name
        try:
            if os.path.exists(upload_raw_file):
                os.remove(upload_raw_file)
        except:
            return HttpResponse('ERROR! File cannot be deleted!')

        return HttpResponse(json.dumps(request.POST))
    
def data_upload_rna(request):
    if request.method == 'POST':
        upload_id = re.sub(r"[\W]", "", request.POST.get('upload_id_rna'))
        if upload_id == '':
            return HttpResponse('ERROR! Upload ID is missing.')
        upload_path = str(Path(UPLOAD_BASE_PATH).resolve().joinpath(upload_id))
        new_file_name = 'undefined_format'
        if 'uploadfile_type1_rna_tumor' in request.POST:
            new_file_name = 'T.rna.' + request.POST.get('uploadfile_type1_rna_tumor') + '.fastq.gz'
        elif 'uploadfile_type2_rna_tumor' in request.POST:
            new_file_name = 'T.rna.' + request.POST.get('uploadfile_type2_rna_tumor') + '.fastq.gz'
        elif 'uploadfile_type1_rna_normal' in request.POST:
            new_file_name = 'N.rna.' + request.POST.get('uploadfile_type1_rna_normal') + '.fastq.gz'
        elif 'uploadfile_type2_rna_normal' in request.POST:
            new_file_name = 'N.rna.' + request.POST.get('uploadfile_type2_rna_normal') + '.fastq.gz'
        elif 'uploadfile_rna_mass' in request.POST:
            new_file_name = 'rna.mass.fasta'

        try:
            upload_raw_file = upload_path + '/' + new_file_name
            file = request.FILES['myfile']
            if not os.path.exists(upload_path):
                os.makedirs(upload_path)
            if new_file_name == 'rna.mass.fasta':
                if file.name.endswith('.gz'):
                    with open(upload_raw_file, 'wb+') as destination:
                        with gzip.GzipFile(fileobj=file) as source:
                            shutil.copyfileobj(source, destination) 
            else: 
                with open(upload_raw_file, 'wb+') as destination:
                    for chunk in file.chunks():
                        destination.write(chunk)
            file.close()
        except:
            return HttpResponse('ERROR! System error.')
        return HttpResponse(json.dumps(request.POST))


def delete_upload_rna(request):
    if request.method == 'POST':
        upload_id = re.sub(r"[\W]", "", request.POST.get('upload_id_rna'))
        if upload_id == '':
            return HttpResponse('ERROR! Upload ID is missing.')
        upload_path = str(Path(UPLOAD_BASE_PATH).resolve().joinpath(upload_id))
        new_file_name = 'undefined_format'
        if 'uploadfile_type1_rna_tumor' in request.POST:
            new_file_name = 'T.rna.' + request.POST.get('uploadfile_type1_rna_tumor') + '.fastq.gz'
        elif 'uploadfile_type2_rna_tumor' in request.POST:
            new_file_name = 'T.rna.' + request.POST.get('uploadfile_type2_rna_tumor') + '.fastq.gz'
        elif 'uploadfile_type1_rna_normal' in request.POST:
            new_file_name = 'N.rna.' + request.POST.get('uploadfile_type1_rna_normal') + '.fastq.gz'
        elif 'uploadfile_type2_rna_normal' in request.POST:
            new_file_name = 'N.rna.' + request.POST.get('uploadfile_type2_rna_normal') + '.fastq.gz'
        elif 'uploadfile_rna_mass' in request.POST:
            new_file_name = 'rna.mass.fasta'
        
        upload_raw_file = upload_path + '/' + new_file_name
        try:
            if os.path.exists(upload_raw_file):
                os.remove(upload_raw_file)
        except:
            return HttpResponse('ERROR! File cannot be deleted!')

        return HttpResponse(json.dumps(request.POST))
    
def data_upload_drna(request):
    if request.method == 'POST':
        upload_id = re.sub(r"[\W]", "", request.POST.get('upload_id_drna'))
        if upload_id == '':
            return HttpResponse('ERROR! Upload ID is missing.')
        upload_path = str(Path(UPLOAD_BASE_PATH).resolve().joinpath(upload_id))
        new_file_name = 'undefined_format'
        if 'uploadfile_type1_drna_tumor' in request.POST:
            new_file_name = 'T.rna.' + request.POST.get('uploadfile_type1_drna_tumor') + '.fastq.gz'
        elif 'uploadfile_type2_drna_tumor' in request.POST:
            new_file_name = 'T.rna.' + request.POST.get('uploadfile_type2_drna_tumor') + '.fastq.gz'
        elif 'uploadfile_type1_drna_normal' in request.POST:
            new_file_name = 'N.rna.' + request.POST.get('uploadfile_type1_drna_normal') + '.fastq.gz'
        elif 'uploadfile_type2_drna_normal' in request.POST:
            new_file_name = 'N.rna.' + request.POST.get('uploadfile_type2_drna_normal') + '.fastq.gz'
        elif 'uploadfile_type1_rdna_tumor' in request.POST:
            new_file_name = 'T.dna.' + request.POST.get('uploadfile_type1_rdna_tumor') + '.fastq.gz'
        elif 'uploadfile_type2_rdna_tumor' in request.POST:
            new_file_name = 'T.dna.' + request.POST.get('uploadfile_type2_rdna_tumor') + '.fastq.gz'
        elif 'uploadfile_type1_rdna_normal' in request.POST:
            new_file_name = 'N.dna.' + request.POST.get('uploadfile_type1_rdna_normal') + '.fastq.gz'
        elif 'uploadfile_type2_rdna_normal' in request.POST:
            new_file_name = 'N.dna.' + request.POST.get('uploadfile_type2_rdna_normal') + '.fastq.gz'
        elif 'uploadfile_drna_mass' in request.POST:
            new_file_name = 'dna.rna.mass.fasta'
        try:
            upload_raw_file = upload_path + '/' + new_file_name
            file = request.FILES['myfile']
            if not os.path.exists(upload_path):
                os.makedirs(upload_path)
            if new_file_name == 'dna.rna.mass.fasta':
                if file.name.endswith('.gz'):
                    with open(upload_raw_file, 'wb+') as destination:
                        with gzip.GzipFile(fileobj=file) as source:
                            shutil.copyfileobj(source, destination) 
            else: 
                with open(upload_raw_file, 'wb+') as destination:
                    for chunk in file.chunks():
                        destination.write(chunk)
            file.close()
        except:
            return HttpResponse('ERROR! System error.')
        return HttpResponse(json.dumps(request.POST))


def delete_upload_drna(request):
    if request.method == 'POST':
        upload_id = re.sub(r"[\W]", "", request.POST.get('upload_id_drna'))
        if upload_id == '':
            return HttpResponse('ERROR! Upload ID is missing.')
        upload_path = str(Path(UPLOAD_BASE_PATH).resolve().joinpath(upload_id))
        new_file_name = 'undefined_format'
        if 'uploadfile_type1_drna_tumor' in request.POST:
            new_file_name = 'T.rna.' + request.POST.get('uploadfile_type1_drna_tumor') + '.fastq.gz'
        elif 'uploadfile_type2_drna_tumor' in request.POST:
            new_file_name = 'T.rna.' + request.POST.get('uploadfile_type2_drna_tumor') + '.fastq.gz'
        elif 'uploadfile_type1_drna_normal' in request.POST:
            new_file_name = 'N.rna.' + request.POST.get('uploadfile_type1_drna_normal') + '.fastq.gz'
        elif 'uploadfile_type2_drna_normal' in request.POST:
            new_file_name = 'N.rna.' + request.POST.get('uploadfile_type2_drna_normal') + '.fastq.gz'
        elif 'uploadfile_type1_rdna_tumor' in request.POST:
            new_file_name = 'T.dna.' + request.POST.get('uploadfile_type1_rdna_tumor') + '.fastq.gz'
        elif 'uploadfile_type2_rdna_tumor' in request.POST:
            new_file_name = 'T.dna.' + request.POST.get('uploadfile_type2_rdna_tumor') + '.fastq.gz'
        elif 'uploadfile_type1_rdna_normal' in request.POST:
            new_file_name = 'N.dna.' + request.POST.get('uploadfile_type1_rdna_normal') + '.fastq.gz'
        elif 'uploadfile_type2_rdna_normal' in request.POST:
            new_file_name = 'N.dna.' + request.POST.get('uploadfile_type2_rdna_normal') + '.fastq.gz'
        elif 'uploadfile_drna_mass' in request.POST:
            new_file_name = 'dna.rna.mass.fasta'
        
        upload_raw_file = upload_path + '/' + new_file_name
        try:
            if os.path.exists(upload_raw_file):
                os.remove(upload_raw_file)
        except:
            return HttpResponse('ERROR! File cannot be deleted!')

        return HttpResponse(json.dumps(request.POST))

def data_upload_tsv(request):
    if request.method == 'POST':
        upload_id = re.sub(r"[\W]", "", request.POST.get('upload_id'))
        if upload_id == '':
            return HttpResponse('ERROR! Upload ID is missing.')
        upload_path = str(Path(UPLOAD_BASE_PATH).resolve().joinpath(upload_id))
        timeInMs = request.POST.get('timeInMs')
        new_file_name = f'{timeInMs}.neoantigen.result.tsv'
        try:
            upload_raw_file = upload_path + '/' + new_file_name
            file = request.FILES['myfile']
            if not os.path.exists(upload_path):
                os.makedirs(upload_path)
            with open(upload_raw_file, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
            file.close()
        except:
            return HttpResponse('ERROR! System error.')
        return HttpResponse(json.dumps(request.POST))


def delete_upload_tsv(request):
    if request.method == 'POST':
        upload_id = re.sub(r"[\W]", "", request.POST.get('upload_id'))
        if upload_id == '':
            return HttpResponse('ERROR! Upload ID is missing.')
        upload_path = str(Path(UPLOAD_BASE_PATH).resolve().joinpath(upload_id))
        timeInMs = request.POST.get('timeInMs')
        new_file_name = f'{timeInMs}.neoantigen.result.tsv'
        upload_raw_file = upload_path + '/' + new_file_name
        try:
            if os.path.exists(upload_raw_file):
                os.remove(upload_raw_file)
        except:
            return HttpResponse('ERROR! File cannot be deleted!')
        return HttpResponse(json.dumps(request.POST))


def confirm_urls(request):
    if request.method == 'POST':
        if re.sub(r"[\W]", "", request.POST.get('upload_id')) != "None":
            upload_id = re.sub(r"[\W]", "", request.POST.get('upload_id'))
        elif re.sub(r"[\W]", "", request.POST.get('upload_id_rna')) != "None":
            upload_id = re.sub(r"[\W]", "", request.POST.get('upload_id_rna'))
        elif re.sub(r"[\W]", "", request.POST.get('upload_id_drna')) != "None":
            upload_id = re.sub(r"[\W]", "", request.POST.get('upload_id_drna'))
        else:
            return HttpResponse('ERROR! No user ID!')
        upload_path = str(Path(UPLOAD_BASE_PATH).resolve().joinpath(upload_id))
        confirm_result = {'R1': False, 'R2':False, 'Ms':False, 'R1_err':'', 'R2_err':'', 'Ms_err':''}
        if _is_path_exist(upload_path) == False:
            makedirs(upload_path)
        for key, val in request.POST.items():
            is_status_ok = False
            is_format_ok = False
            if key[:3] == 'url': 
                m1 = re.search('google\.com\/file\/d\/(.+)\/', val)
                if m1:
                    # use GoogleDriveDownloader module
                    id = m1.group(1)
                    response = GoogleDriveDownloader.get_response(id)
                else:
                    # direct download
                    if not re.match(r'^(http|https|ftp)://', val):
                        val = 'http://'+val
                    requests_ftp.monkeypatch_session()
                    session = requests.Session()
                    response = session.get(val, stream=True)
                # Check file existing
                is_status_ok = response.ok
                if is_status_ok == False:
                    confirm_result[key[-2:]+'_err'] = 'File Not Found'
                else:
                    # Check file format
                    if m1:
                        m2 = re.search('filename="(.+)"', response.headers['Content-Disposition'])
                        file_name = m2.group(1)
                    else:
                        file_name = response.url.split('/')[-1]
                    if key[-2:] == 'Ms':
                        if re.search('\.(fasta|fa|fna)+(\.gz)*$', file_name):
                            is_format_ok = True
                        else:
                            is_format_ok = False
                            confirm_result[key[-2:]+'_err'] = 'Unkown File Format'
                    else: #R1/R2
                        if re.search('\.f(ast)*q(\.gz)*$', file_name):
                            is_format_ok = True
                        else:
                            is_format_ok = False
                            confirm_result[key[-2:]+'_err'] = 'Unkown File Format'
                confirm_result[key[-2:]] = is_status_ok and is_format_ok
        return HttpResponse(json.dumps(confirm_result))
             
## HLA genotyping

def status(request, task_id="not_passed"):
    status_dict={}
    if(list(User_Job.objects.filter(user_id=task_id))==[]):
        return render(request,'no_id_match.html',{'task_id':task_id})
    return render(request,'status.html',status_dict)

def report(request, task_id="not_passed"):
    if(list(User_Job.objects.filter(user_id=task_id))==[]):
        return render(request,'no_id_match.html',{'task_id':task_id})
    task=User_Job.objects.filter(user_id=task_id)[0]
    
    # overview page
    overview={}
    overview['submit_time']=task.submission_time
    overview['start_time']=task.start_time
    overview['end_time']=task.end_time
    success=1
    total_file=1
    
    # Check success or fail
    if(task.total_status=="FAILED"):
        success=0      
        try:
            failed_step=task.error_log
        except:
            failed_step = "SYSTEM"

        return render(request,'report.html',
                    {
                     'task_id':task_id,
                     'success':success,
                     'failed_step':failed_step,
                     'overview':overview,
                     'total_file':total_file,
                    })
    elif(task.total_status=="WAITING" or task.total_status=="RUNNING"):
        return render(request,'status.html',{})
    
    # get system info tables    
    databases_df = pd.read_csv(DATA+'/'+task_id+'/HLA_typing/N/2-hla-typing/N_result.tsv', sep="\t", engine='python')
    databases_list = databases_df[databases_df.columns[:3]].values.tolist()

    basic_dic={'success':success,
               'task_id':task_id,
               'overview':overview,
               'total_file':total_file,
               'databases_list':databases_list,
              }
    return render(request, 'report.html',basic_dic)


def retrieve(request, task_id="not_passed"):
    if(list(User_Job.objects.filter(user_id=task_id))==[]):
        return render(request,'no_id_match.html',{'task_id':task_id})
    else:
        myjob = User_Job.objects.get(user_id=task_id)
        status_dict = {}
        status_dict['total_status'] = myjob.total_status
        status_dict['data_preparation_status'] = myjob.data_preparation_status  
        status_dict['quality_check_status'] = myjob.quality_check_status
        status_dict['hla_status'] = myjob.hla_status
        status_dict['hla_result_status'] = myjob.hla_result_status
        status_dict['task_id'] = task_id

        # Saving JSON file
        with open(f'/{UPLOAD_BASE_PATH}/{task_id}/status_report.json','w',encoding = 'utf-8') as f :
            json.dump(status_dict,f, indent=2, sort_keys=True, ensure_ascii=False)
    return JsonResponse(status_dict)


def hla_tsv(request, task_id):
    task=User_Job.objects.filter(user_id=task_id)[0]
    hla_tsv = open(f'/{UPLOAD_BASE_PATH}/{task_id}/HLA_typing/N/2-hla-typing/N_result.tsv', 'rb')
    response = FileResponse(hla_tsv)
    return response
    

def hla_result(request):
    # This pipeline is to run HLA genotyping.
    if request.method == 'POST':

        # Step1. getting input files (R1 & R2) & user ID
        try:
            upload_id = re.sub(r"[\W]", "", request.POST.get('upload_id'))
            uid = upload_id
            if upload_id == '':
                msg = "Your upload files cannot not be accepted, please conform to the correct file format and the number of your upload files."
                return render(request, 'not_allow.html', {'uid': uid, 'msg': msg})
            upload_path = str(Path(UPLOAD_BASE_PATH).resolve().joinpath(upload_id))
            if _is_path_exist(upload_path) == False:
                makedirs(upload_path)
            r1_file = 'N.R1.fastq.gz'
            r2_file = 'N.R2.fastq.gz'
        except:
            msg = "Your upload files cannot not be accepted, please conform to the correct file formats"
            return render(request, 'not_allow.html', {'uid': uid, 'msg': msg})
        
        # Step2. parameter setting
        try:
            parameters = {}
            UPLOAD_PATH = UPLOAD_BASE_PATH + '/' + upload_id
            r1_file = 'N.R1.fastq.gz'
            r2_file = 'N.R2.fastq.gz'
            sample_name = "N"
            thread = "24"
            parameters['r1_file'] = r1_file
            parameters['r2_file'] = r2_file
            parameters['dict_urls']={}  # Dictionary for URL download
            if request.POST.get('upload_method') == "from_url":
                parameters['dict_urls'] = {'N.R1.fastq.gz': request.POST.get('confirmed_url_R1'), 'N.R2.fastq.gz': request.POST.get('confirmed_url_R2')}
            if request.POST.get('data_type') == "RNA":
                parameters['sample_type'] = "-RNA"
            else:
                 parameters['sample_type'] = "-DNA"
            parameters['thread'] = thread
            parameters['output_path'] = UPLOAD_BASE_PATH +  '/' + upload_id
            parameters['sample_name'] = sample_name
            parameters['database_path'] = DATABASE_PATH
            parameters['tmp_path'] = TMP_BASE_PATH
            parameters['task_id'] = upload_id  
        except:
            msg = "Your upload files or parameters cannot not be accepted, please conform to the correct file and parameter formats"
            return render(request, 'not_allow.html', {'uid': uid, 'msg': msg})

        # Step3. getting IP

        # ip_address = get_client_ip(request)  #make sure this line work in real environment
        ip_info = get_location()
        ip_address = ip_info['ip']

        if ip_address is not None:
            print("We have a publicly-routable IP address for client")
            submitted_job_number=User_Job.objects.filter(ip=ip_address,total_status__in=["WAITING","RUNNING"]).count()
            if(submitted_job_number>2):  #block more than two jobs from single ip address
                msg="Only 2 tasks are allowed to each IP. We cannot accept it since your 2 tasks are still waiting or running on the system."
                return render(request,'not_allow.html',{'uid':uid,'msg':msg}) 
            try:
                country=reader.get(ip_address)['country']['names']['en']
                # country = ip_info['country']

            except:
                country="NA"        
        else:
            ip_address="NA"
            country="NA"
            print("We don't have an IP address for client or IP is private")
        
        # Step4. saving uid into model 
        try: 
            mail = request.POST['email']
            times = datetime.datetime.now()
            start_time = times.strftime("%Y-%m-%d %H:%M:%S")
            expected_ended_time = "1 hour"
            User_Job.objects.create(user_id=uid,
                                upload_id=upload_id,
                                ip=ip_address,mail=mail,
                                submission_time=times,
                                start_time=times,
                                end_time=times)
            ip_log.objects.create(ip=ip_address,country=country,submission_time=times,functions="HLA")
            print(f'{mail},{times},{ip_address},{country},{expected_ended_time}')
            ip_dict = {}
            ip_dict['user_id'] = uid
            ip_dict['ip_address'] = ip_address
            ip_dict['country'] = country
            ip_dict['submission_time'] = str(times)
            ip_dict['task_type'] = "HLA"
            ip_dict['mail'] = mail

            with open(f'/{UPLOAD_BASE_PATH}/{uid}/user_info.json','w',encoding = 'utf-8') as f :
                json.dump(ip_dict,f, indent=2, sort_keys=True, ensure_ascii=False)
            job_numbers=User_Job.objects.filter(total_status__in=['WAITING','RUNNING']).count()
        except:
            #return email not allowed
            msg="Your email address is not a correct one."
            return render(request,'not_allow.html',{'uid':uid,'msg':msg})    

        # Step5. running hla typing => sending jobs to task.py
        task_id=async_task('DjangoWeb.tasks.run_hla_typing',data_path=UPLOAD_PATH, parameters=parameters)
        
        # Step6. sending mail with link 
        user_status_link = "/" + uid + "/status"
        send_mail('HLA Genotyping Task Submitted', f'Hello,\n\nYor task for HLA genotyping was sucessfully submitted to our online system. Please kindly wait for a few hours to receive a result. You can check the status of your submitted task.\nYour status link: {web_url}{user_status_link}\n\nBest wishes,\nNARWHAL team', from_email, [mail], fail_silently=True)
 
        # Step7. leading to user's specific status.html
        user_status_link = "/" + uid + "/status"
        return render(request, 'submit_response.html',
                      {'uid': uid,
                       'job_numbers': job_numbers,
                       'start_time': start_time,
                       'expected_ended_time': expected_ended_time,
                       'user_status_link': user_status_link})


## Neoantigen identification with DNA-seq

def status_dnaneo(request, task_id="not_passed"):
    status_dict={}
    if(list(User_Job.objects.filter(user_id=task_id))==[]):
        return render(request,'no_id_match.html',{'task_id':task_id})
    return render(request,'status_dnaneo.html',status_dict)

def retrieve_dnaneo(request, task_id="not_passed"):
    if(list(User_Job.objects.filter(user_id=task_id))==[]):
        return render(request,'no_id_match.html',{'task_id':task_id})
    else:
        myjob = User_Job.objects.get(user_id=task_id)
        status_dict = {}
        status_dict['total_status'] = myjob.total_status
        status_dict['data_preparation_status'] = myjob.data_preparation_status  
        status_dict['quality_check_status'] = myjob.quality_check_status
        status_dict['gatk_status'] = myjob.gatk_status
        status_dict['somatic_status'] = myjob.somatic_status
        status_dict['germline_status'] = myjob.germline_status
        status_dict['phasing_status'] = myjob.phasing_status
        status_dict['mass_status'] = myjob.mass_status
        status_dict['hla_status'] = myjob.hla_status
        status_dict['pvactools_status'] = myjob.pvactools_status
        status_dict['dna_total_status'] = myjob.dna_total_status
        status_dict['task_id'] = task_id

        # Saving JSON file
        with open(f'/{UPLOAD_BASE_PATH}/{task_id}/status_report.json','w',encoding = 'utf-8') as f :
            json.dump(status_dict,f, indent=2, sort_keys=True, ensure_ascii=False)
    return JsonResponse(status_dict)

def report_dnaneo(request, task_id="not_passed"):
    if(list(User_Job.objects.filter(user_id=task_id))==[]):
        return render(request,'no_id_match.html',{'task_id':task_id})
    task=User_Job.objects.filter(user_id=task_id)[0]
    
    #overview page
    overview={}
    overview['submit_time']=task.submission_time
    overview['start_time']=task.start_time
    overview['end_time']=task.end_time
    overview['mass_status']=task.mass_status
    success=1
    mass=0
    total_file=1
    
    # Check success or fail
    if(task.total_status=="FAILED"):
        success=0  
        try:
            failed_step=task.error_log
        except:
            failed_step = "SYSTEM"
       
        return render(request,'report_dnaneo.html',
                    {
                     'task_id':task_id,
                     'success':success,
                     'mass':mass,
                     'failed_step':failed_step,
                     'overview':overview,
                     'total_file':total_file,
                    })
    elif(task.total_status=="WAITING" or task.total_status=="RUNNING"):
        return render(request,'status_dnaneo.html',{})
    
    # Check mass result
    if(task.mass_status=="SUCCESSFUL"):
        mass=1
    
    # get system info tables    
    databases_df = pd.read_csv(DATA+'/'+task_id+'/mTSA_DNAseq/6-hla-binding-affinity/T/T_TSA_candidates_with_cosmic.tsv', sep="\t", engine='python')
    databases_list = databases_df[databases_df.columns[:3]].values.tolist()

    basic_dic={'success':success,
               'mass':mass,
               'task_id':task_id,
               'overview':overview,
               'total_file':total_file,
               'databases_list':databases_list,
              }
    return render(request, 'report_dnaneo.html',basic_dic)

# mTSA with DNA-seq table
def dna_mTSA(request, task_id):
    task=User_Job.objects.filter(user_id=task_id)[0]
    dna_mTSA = open(f'/{UPLOAD_BASE_PATH}/{task_id}/mTSA_DNAseq/6-hla-binding-affinity/T/T_TSA_candidates_with_cosmic.tsv', 'rb')
    response = FileResponse(dna_mTSA)
    return response

def dna_neo_result(request):
    # This pipeline is to run neoantigen identification with DNA-seq.
    if request.method == 'POST':
        # Step1. getting input files (R1 & R2) & user ID
        try:
            upload_id = request.POST.get('upload_id')
            uid = upload_id
            if upload_id == '':
                msg = "Your upload files cannot not be accepted, please conform to the correct file format and the number of your upload files."
                return render(request, 'not_allow.html', {'uid': uid, 'msg': msg})
            upload_path = str(Path(UPLOAD_BASE_PATH).resolve().joinpath(upload_id))
            N_r1_file = 'N.dna.R1.fastq.gz'
            N_r2_file = 'N.dna.R2.fastq.gz'
            T_r1_file = 'T.dna.R1.fastq.gz'
            T_r2_file = 'T.dna.R2.fastq.gz'
            mass_file = 'dna.mass.fasta.gz'
            mass_file_path = upload_path + '/' + mass_file
            if _is_path_exist(mass_file_path) == True:
                mass_step = True
            else:
                mass_step = False

        except:
            msg = "Your upload files cannot not be accepted, please conform to the correct file formats"
            return render(request, 'not_allow.html', {'uid': uid, 'msg': msg})
        
        # # Step2. parameter setting
        try:
            parameters = {}
            UPLOAD_PATH = UPLOAD_BASE_PATH + '/' + upload_id
            normal_sample_name = "N"
            tumor_sample_name = "T"
            thread = "24"
            max_ic_strong = request.POST.get('dna_max_ic_strong')
            max_ic_inter = request.POST.get('dna_max_ic_inter')
            max_ic_weak = request.POST.get('dna_max_ic_weak')
            if(len(list(request.POST.getlist('DNA-HLA-multiple')))==0): # set HLA types
                hla_typing_step = True
                hla_type_ls = []
            else:
                hla_typing_step = False
                hla_type_ls =list(request.POST.getlist('DNA-HLA-multiple'))
                print(hla_type_ls)
            parameters['dict_urls']={}  # Dictionary for URL download
            if request.POST.get('dna_T_upload_method') == "dna_tumor_from_url": # files from URLs
                parameters['dict_urls'] = {'T.dna.R1.fastq.gz': request.POST.get('confirmed_url_dna_tumor_R1'), \
                                           'T.dna.R2.fastq.gz': request.POST.get('confirmed_url_dna_tumor_R2')}
            if request.POST.get('dna_N_upload_method') == "dna_normal_from_url": # files from URLs
                parameters['dict_urls'].update({'N.dna.R1.fastq.gz': request.POST.get('confirmed_url_dna_normal_R1'), \
                              'N.dna.R2.fastq.gz': request.POST.get('confirmed_url_dna_normal_R2')})
            if request.POST.get('dna_Ms_upload_method') == "dna_mass_from_url": # files from URLs
                parameters['dict_urls'].update({'dna.mass.fasta': request.POST.get('dna_mass_confirmed_url')})
            parameters['N_r1_file'] = N_r1_file
            parameters['N_r2_file'] = N_r2_file
            parameters['T_r1_file'] = T_r1_file
            parameters['T_r2_file'] = T_r2_file
            parameters['mass_file_path'] = mass_file_path
            parameters['mass_step'] = mass_step
            parameters['thread'] = thread
            parameters['output_path'] = UPLOAD_BASE_PATH +  '/' + upload_id
            parameters['normal_sample_name'] = normal_sample_name
            parameters['tumor_sample_name'] = tumor_sample_name
            parameters['database_path'] = DATABASE_PATH
            parameters['home_path'] = HOME_PATH
            parameters['tmp_path'] = TMP_BASE_PATH
            parameters['task_id'] = upload_id
            parameters['hla_type_ls'] = hla_type_ls
            parameters['hla_typing_step'] = hla_typing_step
            parameters['max_ic_strong'] = max_ic_strong
            parameters['max_ic_inter'] = max_ic_inter
            parameters['max_ic_weak'] = max_ic_weak
            print(uid)
            print(parameters['dict_urls'])
        except:
            msg = "Your upload files or parameters cannot not be accepted, please conform to the correct file and parameter formats"
            return render(request, 'not_allow.html', {'uid': uid, 'msg': msg})

        # Step3. getting IP
        # ip_address=get_client_ip(request)  #make sure this line work in real environment
        ip_info = get_location()
        ip_address = ip_info['ip']

        if ip_address is not None:
            print("We have a publicly-routable IP address for client")
            submitted_job_number=User_Job.objects.filter(ip=ip_address,total_status__in=["WAITING","RUNNING"]).count()
            if(submitted_job_number>2):  #block more than two jobs from single ip address
                msg="Only 2 tasks are allowed to each IP. We cannot accept it since your 2 tasks are still waiting or running on the system."
                return render(request,'not_allow.html',{'uid':uid,'msg':msg}) 
            
            try:
                country=reader.get(ip_address)['country']['names']['en']
            except:
                country="NA"        
        else:
            ip_address="NA"
            country="NA"
            print("We don't have an IP address for client or IP is private")
        
        # Step4. saving uid into model  
        try:
            mail = request.POST['email_dna']
            times = datetime.datetime.now()
            start_time = times.strftime("%Y-%m-%d %H:%M:%S")
            expected_ended_time = "10 hours"
            User_Job.objects.create(user_id=uid,
                                upload_id=upload_id,
                                ip=ip_address,mail=mail,
                                submission_time=times,
                                start_time=times,
                                end_time=times)
            ip_log.objects.create(ip=ip_address,country=country,submission_time=times,functions="DNA")
            print(f'{mail},{times},{ip_address},{country},{expected_ended_time}')
            ip_dict = {}
            ip_dict['user_id'] = uid
            ip_dict['ip_address'] = ip_address
            ip_dict['country'] = country
            ip_dict['submission_time'] = str(times)
            ip_dict['task_type'] = "DNA"
            ip_dict['mail'] = mail
            with open(f'/{UPLOAD_BASE_PATH}/{uid}/user_info.json','w',encoding = 'utf-8') as f :
                json.dump(ip_dict,f, indent=2, sort_keys=True, ensure_ascii=False)
            job_numbers=User_Job.objects.filter(total_status__in=['WAITING','RUNNING']).count()

        except:
            #return email not allowed
            msg="Your email address is not a correct one."
            return render(request,'not_allow.html',{'uid':uid,'msg':msg})    

        # Step5. running hla typing => sending jobs to task.py
        task_id = async_task('DjangoWeb.tasks.mTSA_DNAseq',data_path=UPLOAD_PATH, parameters=parameters)        
        
        # Step6. sending mail with link 
        user_status_link = "/" + uid + "/statusdnaneo"
        send_mail('Neoantigen identification Task Submitted', f'Hello,\n\nYor task for neoantigen identification with DNA-seq was sucessfully submitted to our online system. Please kindly wait for a few hours or days to receive a result. You can check the status of your submitted task.\nYour status link: {web_url}{user_status_link}\n\nBest wishes,\nNARWHAL team', from_email, [mail], fail_silently=True)
 

        # Step7. leading to user's specific status.html
        user_status_link = "/" + uid + "/statusdnaneo"
        return render(request, 'submit_response.html',
                      {'uid': uid,
                       'job_numbers': job_numbers,
                       'start_time': start_time,
                       'expected_ended_time': expected_ended_time,
                       'user_status_link': user_status_link})
    



## TSA identification with RNA-seq

def status_rnaneo(request, task_id="not_passed"):
    status_dict={}
    if(list(User_Job.objects.filter(user_id=task_id))==[]):
        return render(request,'no_id_match.html',{'task_id':task_id})
    return render(request,'status_rnaneo.html',status_dict)

def retrieve_rnaneo(request, task_id="not_passed"):
    if(list(User_Job.objects.filter(user_id=task_id))==[]):
        return render(request,'no_id_match.html',{'task_id':task_id})
    else:
        myjob = User_Job.objects.get(user_id=task_id)
        status_dict = {}
        status_dict['total_status'] = myjob.total_status
        status_dict['data_preparation_status'] = myjob.data_preparation_status        
        status_dict['quality_check_status'] = myjob.quality_check_status
        status_dict['gatk_status'] = myjob.gatk_status
        status_dict['somatic_status'] = myjob.somatic_status
        status_dict['expression_level_status'] = myjob.expression_level_status
        status_dict['filtering_status'] = myjob.filtering_status
        status_dict['hla_status'] = myjob.hla_status
        status_dict['pvactools_status'] = myjob.pvactools_status
        status_dict['aeTSA_status'] = myjob.aeTSA_status
        status_dict['aeTSA_annotation_status'] = myjob.aeTSA_annotation_status
        status_dict['mass_status'] = myjob.mass_status
        status_dict['rna_total_status'] = myjob.rna_total_status
        status_dict['task_id'] = task_id

        # Saving JSON file
        with open(f'/{UPLOAD_BASE_PATH}/{task_id}/status_report.json','w',encoding = 'utf-8') as f :
            json.dump(status_dict,f, indent=2, sort_keys=True, ensure_ascii=False)
    return JsonResponse(status_dict)

def report_rnaneo(request, task_id="not_passed"):
    if(list(User_Job.objects.filter(user_id=task_id))==[]):
        return render(request,'no_id_match.html',{'task_id':task_id})
    task=User_Job.objects.filter(user_id=task_id)[0]
    
    #overview page
    overview={}
    overview['submit_time']=task.submission_time
    overview['start_time']=task.start_time
    overview['end_time']=task.end_time
    overview['aeTSA_annotation_status'] = task.aeTSA_annotation_status
    overview['mass_status'] = task.mass_status
    success=1
    total_file=1
    mass=0
    aeTSA=0
    
    # Check success or fail
    if(task.total_status=="FAILED"):
        success=0  
        try:
            failed_step=error_map[task.error_log]
            if(task.error_log=="SYSTEM"):
                try:
                    Path(DATA+'/'+task_id+'/myjob.tar.gz').resolve()
                except:
                    total_file=0
        except:
            failed_step="SYSTEM"

        return render(request,'report_rnaneo.html',
                    {
                     'task_id':task_id,
                     'success':success,
                     'aeTSA':aeTSA,
                     'mass':mass,
                     'failed_step':failed_step,
                     'overview':overview,
                     'total_file':total_file,
                    })
    elif(task.total_status=="WAITING" or task.total_status=="RUNNING"):
        return render(request,'status_rnaneo.html',{})
    
    # Check mass result
    if(task.mass_status=="SUCCESSFUL"):
        mass=1
    
    # Check aeTSA result
    if(task.aeTSA_annotation_status=="SUCCESSFUL"):
        aeTSA=1

    # get system info tables    
    databases_df = pd.read_csv(f"{DATA}/{task_id}/mTSA_RNAseq/6-hla-binding-affinity/T/T_TSA_candidates_with_cosmic.tsv", sep="\t", engine='python')
    databases_list = databases_df[databases_df.columns[:3]].values.tolist()

    basic_dic={'success':success,
               'task_id':task_id,
               'aeTSA':aeTSA,
               'mass':mass,
               'overview':overview,
               'total_file':total_file,
               'databases_list':databases_list,
              }
    return render(request, 'report_rnaneo.html',basic_dic)

# TSA with RNA-seq table
def rna_TSA(request, task_id):
    task=User_Job.objects.filter(user_id=task_id)[0]
    #overview page
    overview={}
    overview['aeTSA_annotation_status']=task.aeTSA_annotation_status
    if(task.aeTSA_annotation_status=="SUCCESSFUL"):
        rna_TSA = open(f'/{UPLOAD_BASE_PATH}/{task_id}/total_TSA/T_mTSA_and_aeTSA.tsv', 'rb') 
    else:
        rna_TSA = open(f'/{UPLOAD_BASE_PATH}/{task_id}/total_TSA/T_TSA_candidates.tsv', 'rb')
    response = FileResponse(rna_TSA)
    return response

def rna_neo_result(request):
    # This pipeline is to run neoantigen identification with RNA-seq.
        # Step1. getting input files (R1 & R2) & user ID
        try:
            upload_id = request.POST.get('upload_id_rna')
            uid = upload_id
            print(uid)
            if upload_id == '':
                msg = "Your upload files cannot not be accepted, please conform to the correct file format and the number of your upload files."
                return render(request, 'not_allow.html', {'uid': uid, 'msg': msg})
            upload_path = str(Path(UPLOAD_BASE_PATH).resolve().joinpath(upload_id))
            N_r1_file = 'N.rna.R1.fastq.gz'
            N_r2_file = 'N.rna.R2.fastq.gz'
            T_r1_file = 'T.rna.R1.fastq.gz'
            T_r2_file = 'T.rna.R2.fastq.gz'
            mass_file = 'rna.mass.fasta.gz'
            mass_file_path = upload_path + '/' + mass_file
            if _is_path_exist(mass_file_path) == True:
                mass_step = True
            else:
                mass_step = False

        except:
            msg = "Your upload files cannot not be accepted, please conform to the correct file formats"
            return render(request, 'not_allow.html', {'uid': uid, 'msg': msg})
        
        # # Step2. parameter setting
        try:
            parameters = {}
            UPLOAD_PATH = UPLOAD_BASE_PATH + '/' + upload_id
            normal_sample_name = "N"
            tumor_sample_name = "T"
            thread = "24"
            max_ic_strong = request.POST.get('rna_max_ic_strong')
            max_ic_inter = request.POST.get('rna_max_ic_inter')
            max_ic_weak = request.POST.get('rna_max_ic_weak')
            min_coverage_tumor = request.POST.get('min_coverage_tumor')
            min_coverage_normal = request.POST.get('min_coverage_normal')
            min_coverage = request.POST.get('min_coverage') 
            tumor_expression_threshold = request.POST.get('tumor_expression_threshold')
            minimal_expression_ratio = request.POST.get('minimal_expression_ratio')
            if(len(list(request.POST.getlist('RNA-HLA-multiple')))==0):
                hla_typing_step = True
                hla_type_ls = []
            else:
                hla_typing_step = False                
                hla_type_ls =list(request.POST.getlist('RNA-HLA-multiple'))
            parameters['dict_urls']={}  # Dictionary for URL download
            print(request.POST.get('rna_T_upload_method'))
            print(request.POST.get('rna_N_upload_method'))
            print(request.POST.get('drna_Ms_upload_method'))
            if request.POST.get('rna_T_upload_method') == "rna_tumor_from_url": # files from URLs
                parameters['dict_urls'] = {'T.rna.R1.fastq.gz': request.POST.get('confirmed_url_rna_tumor_R1'), \
                                           'T.rna.R2.fastq.gz': request.POST.get('confirmed_url_rna_tumor_R2')}
            if request.POST.get('rna_N_upload_method') == "rna_normal_from_url": # files from URLs
                parameters['dict_urls'].update({'N.rna.R1.fastq.gz': request.POST.get('confirmed_url_rna_normal_R1'), \
                              'N.rna.R2.fastq.gz': request.POST.get('confirmed_url_rna_normal_R2')})
            if request.POST.get('drna_Ms_upload_method') == "rna_mass_from_url": # files from URLs
                parameters['dict_urls'].update({'rna.mass.fasta': request.POST.get('rna_mass_confirmed_url')})
            print(parameters['dict_urls'])
            parameters['N_r1_file'] = N_r1_file
            parameters['N_r2_file'] = N_r2_file
            parameters['T_r1_file'] = T_r1_file
            parameters['T_r2_file'] = T_r2_file
            parameters['mass_file_path'] = mass_file_path
            parameters['mass_step'] = mass_step
            parameters['thread'] = thread
            parameters['output_path'] = UPLOAD_BASE_PATH +  '/' + upload_id
            parameters['normal_sample_name'] = normal_sample_name
            parameters['tumor_sample_name'] = tumor_sample_name
            parameters['database_path'] = DATABASE_PATH
            parameters['home_path'] = HOME_PATH
            parameters['tmp_path'] = TMP_BASE_PATH
            parameters['task_id'] = upload_id
            parameters['hla_type_ls'] = hla_type_ls
            parameters['hla_typing_step'] = hla_typing_step
            parameters['max_ic_strong'] = max_ic_strong
            parameters['max_ic_inter'] = max_ic_inter
            parameters['max_ic_weak'] = max_ic_weak
            parameters['min_coverage_tumor'] = int(min_coverage_tumor)
            parameters['min_coverage_normal'] = int(min_coverage_normal)
            parameters['min_coverage'] = int(min_coverage)
            parameters["tumor_expression_threshold"] = float(tumor_expression_threshold)
            parameters["minimal_expression_ratio"] = minimal_expression_ratio

        except:
            msg = "Your upload files or parameters cannot not be accepted, please conform to the correct file and parameter formats"
            return render(request, 'not_allow.html', {'uid': uid, 'msg': msg})

        # Step3. getting IP
        ip_info = get_location()
        ip_address = ip_info['ip']

        if ip_address is not None:
            print("We have a publicly-routable IP address for client")
            submitted_job_number=User_Job.objects.filter(ip=ip_address,total_status__in=["WAITING","RUNNING"]).count()
            if(submitted_job_number>2):  #block more than two jobs from single ip address
                msg="Only 2 tasks are allowed to each IP. We cannot accept it since your 2 tasks are still waiting or running on the system."
                return render(request,'not_allow.html',{'uid':uid,'msg':msg}) 
            
            try:
                country=reader.get(ip_address)['country']['names']['en']
            except:
                country="NA"        
        else:
            ip_address="NA"
            country="NA"
            print("We don't have an IP address for client or IP is private")
        
        # Step4. saving uid into model
        try:  
            mail = request.POST['email_rna']
            times = datetime.datetime.now()
            start_time = times.strftime("%Y-%m-%d %H:%M:%S")
            expected_ended_time = "10 hours"
            User_Job.objects.create(user_id=uid,
                                upload_id=upload_id,
                                ip=ip_address,mail=mail,
                                submission_time=times,
                                start_time=times,
                                end_time=times)
            ip_log.objects.create(ip=ip_address,country=country,submission_time=times,functions="RNA")
            print(f'{mail},{times},{ip_address},{country},{expected_ended_time}')
            ip_dict = {}
            ip_dict['user_id'] = uid
            ip_dict['ip_address'] = ip_address
            ip_dict['country'] = country
            ip_dict['submission_time'] = str(times)
            ip_dict['task_type'] = "RNA"
            ip_dict['mail'] = mail

            with open(f'/{UPLOAD_BASE_PATH}/{uid}/user_info.json','w',encoding = 'utf-8') as f :
                json.dump(ip_dict,f, indent=2, sort_keys=True, ensure_ascii=False)
            job_numbers=User_Job.objects.filter(total_status__in=['WAITING','RUNNING']).count()

        except:
            #return email not allowed
            msg="Your email address is not a correct one."
            return render(request,'not_allow.html',{'uid':uid,'msg':msg})    

        # Step5. running hla typing => sending jobs to task.py
        task_id = async_task('DjangoWeb.tasks.TSA_RNAseq',data_path=UPLOAD_PATH, parameters=parameters)

        # Step6. sending mail with link 
        user_status_link = "/" + uid + "/statusrnaneo"
        send_mail('Neoantigen identification Task Submitted', f'Hello,\n\nYor task for neoantigen identification with DNA-seq was sucessfully submitted to our online system. Please kindly wait for a few hours or days to receive a result. You can check the status of your submitted task.\nYour status link: {web_url}{user_status_link}\n\nBest wishes,\nNARWHAL team', from_email, [mail], fail_silently=True)
 

        # Step7. leading to user's specific status.html
        user_status_link = "/" + uid + "/statusrnaneo"
        return render(request, 'submit_response.html',
                      {'uid': uid,
                       'job_numbers': job_numbers,
                       'start_time': start_time,
                       'expected_ended_time': expected_ended_time,
                       'user_status_link': user_status_link})



# TSA Identification DNA-seq + RNA-seq

def status_drnaneo(request, task_id="not_passed"):
    status_dict={}
    if(list(User_Job.objects.filter(user_id=task_id))==[]):
        return render(request,'no_id_match.html',{'task_id':task_id})
    return render(request,'status_drnaneo.html',status_dict)

def retrieve_drnaneo(request, task_id="not_passed"):
    if(list(User_Job.objects.filter(user_id=task_id))==[]):
        return render(request,'no_id_match.html',{'task_id':task_id})
    else:
        myjob = User_Job.objects.get(user_id=task_id)
        status_dict = {}
        status_dict['total_status'] = myjob.total_status
        status_dict['data_preparation_status'] = myjob.data_preparation_status  
        status_dict['quality_check_status'] = myjob.quality_check_status
        status_dict['gatk_status'] = myjob.gatk_status
        status_dict['somatic_status'] = myjob.somatic_status
        status_dict['germline_status'] = myjob.germline_status
        status_dict['phasing_status'] = myjob.phasing_status
        status_dict['mass_status'] = myjob.mass_status
        status_dict['hla_status'] = myjob.hla_status
        status_dict['pvactools_status'] = myjob.pvactools_status
        status_dict['dna_total_status'] = myjob.dna_total_status
        status_dict['expression_level_status'] = myjob.expression_level_status
        status_dict['aeTSA_status'] = myjob.aeTSA_status
        status_dict['aeTSA_annotation_status'] = myjob.aeTSA_annotation_status
        status_dict['mass_status'] = myjob.mass_status
        status_dict['rna_total_status'] = myjob.rna_total_status
        status_dict['task_id'] = task_id

        # Saving JSON file
        with open(f'/{UPLOAD_BASE_PATH}/{task_id}/status_report.json','w',encoding = 'utf-8') as f :
            json.dump(status_dict,f, indent=2, sort_keys=True, ensure_ascii=False)
    return JsonResponse(status_dict)

def report_drnaneo(request, task_id="not_passed"):
    if(list(User_Job.objects.filter(user_id=task_id))==[]):
        return render(request,'no_id_match.html',{'task_id':task_id})
    task=User_Job.objects.filter(user_id=task_id)[0]
    
    #overview page
    overview={}
    overview['submit_time']=task.submission_time
    overview['start_time']=task.start_time
    overview['end_time']=task.end_time
    overview['aeTSA_annotation_status'] = task.aeTSA_annotation_status
    overview['mass_status'] = task.mass_status
    success=1
    total_file=1
    mass=0
    aeTSA=0
    
    # Check success or fail
    if(task.total_status=="FAILED"):
        success=0  
        try:
            failed_step=error_map[task.error_log]
            if(task.error_log=="SYSTEM"):
                try:
                    Path(DATA+'/'+task_id+'/myjob.tar.gz').resolve()
                except:
                    total_file=0
        except:
            failed_step="SYSTEM"

        return render(request,'report_rnaneo.html',
                    {
                     'task_id':task_id,
                     'success':success,
                     'aeTSA':aeTSA,
                     'mass':mass,
                     'failed_step':failed_step,
                     'overview':overview,
                     'total_file':total_file,
                    })
    elif(task.total_status=="WAITING" or task.total_status=="RUNNING"):
        return render(request,'report_drnaneo.html',{})
    
    # Check mass result
    if(task.mass_status=="SUCCESSFUL"):
        mass=1
    
    # Check aeTSA result
    if(task.aeTSA_annotation_status=="SUCCESSFUL"):
        aeTSA=1

    # get system info tables    
    databases_df = pd.read_csv(DATA+'/'+task_id+'/mTSA_DNAseq/6-hla-binding-affinity/T/T_TSA_candidates.tsv', sep="\t", engine='python')
    databases_list = databases_df[databases_df.columns[:3]].values.tolist()

    basic_dic={'success':success,
               'task_id':task_id,
               'aeTSA':aeTSA,
               'mass':mass,
               'overview':overview,
               'total_file':total_file,
               'databases_list':databases_list,
              }
    return render(request, 'report_drnaneo.html',basic_dic)

# mTSA with RNA-seq table
def drna_TSA(request, task_id):
    task=User_Job.objects.filter(user_id=task_id)[0]
    #overview page
    overview={}
    overview['aeTSA_annotation_status']=task.aeTSA_annotation_status
    if(task.aeTSA_annotation_status=="SUCCESSFUL"):
        rna_TSA = open(f'/{UPLOAD_BASE_PATH}/{task_id}/total_TSA/T_mTSA_and_aeTSA.tsv', 'rb') 
    else:
        rna_TSA = open(f'/{UPLOAD_BASE_PATH}/{task_id}/mTSA_DNAseq/6-hla-binding-affinity/T/T_TSA_candidates.tsv', 'rb')
    response = FileResponse(rna_TSA)
    return response

def drna_neo_result(request):
    # This pipeline is to run neoantigen identification with RNA-seq.
        # Step1. getting input files (R1 & R2) & user ID
        try:
            upload_id = request.POST.get('upload_id_drna')
            uid = upload_id
            print(uid)
            if upload_id == '':
                msg = "Your upload files cannot not be accepted, please conform to the correct file format and the number of your upload files."
                return render(request, 'not_allow.html', {'uid': uid, 'msg': msg})
            upload_path = str(Path(UPLOAD_BASE_PATH).resolve().joinpath(upload_id))
            dna_N_r1_file = 'N.dna.R1.fastq.gz'
            dna_N_r2_file = 'N.dna.R2.fastq.gz'
            dna_T_r1_file = 'T.dna.R1.fastq.gz'
            dna_T_r2_file = 'T.dna.R2.fastq.gz'
            rna_N_r1_file = 'N.rna.R1.fastq.gz'
            rna_N_r2_file = 'N.rna.R2.fastq.gz'
            rna_T_r1_file = 'T.rna.R1.fastq.gz'
            rna_T_r2_file = 'T.rna.R2.fastq.gz'
            mass_file = 'dna.rna.mass.fasta.gz'
            mass_file_path = upload_path + '/' + mass_file
            if _is_path_exist(mass_file_path) == True:
                mass_step = True
            else:
                mass_step = False

        except:
            msg = "Your upload files cannot not be accepted, please conform to the correct file formats"
            return render(request, 'not_allow.html', {'uid': uid, 'msg': msg})
        
        # # Step2. parameter setting
        try:
            parameters = {}
            UPLOAD_PATH = UPLOAD_BASE_PATH + '/' + upload_id
            normal_sample_name = "N"
            tumor_sample_name = "T"
            thread = "24"
            max_ic_strong = request.POST.get('drna_max_ic_strong')
            max_ic_inter = request.POST.get('drna_max_ic_inter')
            max_ic_weak = request.POST.get('drna_max_ic_weak')
            tumor_expression_threshold = request.POST.get('drna_tumor_expression_threshold')
            minimal_expression_ratio = request.POST.get('drna_minimal_expression_ratio') 
            if(len(list(request.POST.getlist('DNA-RNA-HLA-multiple')))==0):
                hla_typing_step = True
                hla_type_ls = []
            else:
                hla_typing_step = False
                hla_type_ls =list(request.POST.getlist('DNA-RNA-HLA-multiple'))
            parameters['dict_urls']={}  # Dictionary for URL download
            print(request.POST.get('rdna_T_upload_method'))
            print(request.POST.get('rdna_N_upload_method'))
            print(request.POST.get('drna_T_upload_method'))
            print(request.POST.get('drna_N_upload_method'))
            print(request.POST.get('drna_mass_upload_method'))
            print(request.POST.get('confirmed_url_rdna_tumor_R1'))
            if request.POST.get('rdna_T_upload_method') == "rdna_tumor_from_url": # files from URLs
                parameters['dict_urls'].update({'T.dna.R1.fastq.gz': request.POST.get('confirmed_url_rdna_tumor_R1'), \
                                           'T.dna.R2.fastq.gz': request.POST.get('confirmed_url_rdna_tumor_R2')})
            if request.POST.get('rdna_N_upload_method') == "rdna_normal_from_url": # files from URLs
                parameters['dict_urls'].update({'N.dna.R1.fastq.gz': request.POST.get('confirmed_url_rdna_normal_R1'), \
                                        'N.dna.R2.fastq.gz': request.POST.get('confirmed_url_rdna_normal_R2')})
            if request.POST.get('drna_T_upload_method') == "drna_tumor_from_url": # files from URLs
                parameters['dict_urls'].update({'T.rna.R1.fastq.gz': request.POST.get('confirmed_url_drna_tumor_R1'), \
                                           'T.rna.R2.fastq.gz': request.POST.get('confirmed_url_drna_tumor_R2')})
            if request.POST.get('drna_N_upload_method') == "drna_normal_from_url": # files from URLs
                parameters['dict_urls'].update({'N.rna.R1.fastq.gz': request.POST.get('confirmed_url_drna_normal_R1'), \
                              'N.rna.R2.fastq.gz': request.POST.get('confirmed_url_drna_normal_R2')})
            if request.POST.get('drna_Ms_upload_method') == "drna_mass_from_url": # files from URLs
                parameters['dict_urls'].update({'dna.rna.mass.fasta': request.POST.get('drna_mass_confirmed_url')})
            print(parameters['dict_urls'])
            parameters['dna_N_r1_file'] = dna_N_r1_file
            parameters['dna_N_r2_file'] = dna_N_r2_file
            parameters['dna_T_r1_file'] = dna_T_r1_file
            parameters['dna_T_r2_file'] = dna_T_r2_file
            parameters['rna_N_r1_file'] = rna_N_r1_file
            parameters['rna_N_r2_file'] = rna_N_r2_file
            parameters['rna_T_r1_file'] = rna_T_r1_file
            parameters['rna_T_r2_file'] = rna_T_r2_file
            parameters['mass_file_path'] = mass_file_path
            parameters['mass_step'] = mass_step
            parameters['thread'] = thread
            parameters['output_path'] = UPLOAD_BASE_PATH +  '/' + upload_id
            parameters['normal_sample_name'] = normal_sample_name
            parameters['tumor_sample_name'] = tumor_sample_name
            parameters['database_path'] = DATABASE_PATH
            parameters['home_path'] = HOME_PATH
            parameters['tmp_path'] = TMP_BASE_PATH
            parameters['task_id'] = upload_id
            parameters['hla_type_ls'] = hla_type_ls
            parameters['hla_typing_step'] = hla_typing_step
            parameters['max_ic_strong'] = max_ic_strong
            parameters['max_ic_inter'] = max_ic_inter
            parameters['max_ic_weak'] = max_ic_weak
            parameters["tumor_expression_threshold"] = float(tumor_expression_threshold)
            parameters["minimal_expression_ratio"] = float(minimal_expression_ratio)

        except:
            msg = "Your upload files or parameters cannot not be accepted, please conform to the correct file and parameter formats"
            return render(request, 'not_allow.html', {'uid': uid, 'msg': msg})

        # Step3. getting IP
        ip_info = get_location()
        ip_address = ip_info['ip']

        if ip_address is not None:
            print("We have a publicly-routable IP address for client")
            submitted_job_number=User_Job.objects.filter(ip=ip_address,total_status__in=["WAITING","RUNNING"]).count()
            if(submitted_job_number>2):  #block more than two jobs from single ip address
                msg="Only 2 tasks are allowed to each IP. We cannot accept it since your 2 tasks are still waiting or running on the system."
                return render(request,'not_allow.html',{'uid':uid,'msg':msg}) 
            
            try:
                country=reader.get(ip_address)['country']['names']['en']
            except:
                country="NA"        
        else:
            ip_address="NA"
            country="NA"
            print("We don't have an IP address for client or IP is private")
        
        # Step4. saving uid into model
        try:  
            mail = request.POST['email_drna']
            times = datetime.datetime.now()
            start_time = times.strftime("%Y-%m-%d %H:%M:%S")
            expected_ended_time = "10 hours"
            User_Job.objects.create(user_id=uid,
                                upload_id=upload_id,
                                ip=ip_address,mail=mail,
                                submission_time=times,
                                start_time=times,
                                end_time=times)
            ip_log.objects.create(ip=ip_address,country=country,submission_time=times,functions="DRNA")
            print(f'{mail},{times},{ip_address},{country},{expected_ended_time}')
            ip_dict = {}
            ip_dict['user_id'] = uid
            ip_dict['ip_address'] = ip_address
            ip_dict['country'] = country
            ip_dict['submission_time'] = str(times)
            ip_dict['task_type'] = "DRNA"
            ip_dict['mail'] = mail
            with open(f'/{UPLOAD_BASE_PATH}/{uid}/user_info.json','w',encoding = 'utf-8') as f :
                json.dump(ip_dict,f, indent=2, sort_keys=True, ensure_ascii=False)
            job_numbers=User_Job.objects.filter(total_status__in=['WAITING','RUNNING']).count()

        except:
            #return email not allowed
            msg="Your email address is not a correct one."
            return render(request,'not_allow.html',{'uid':uid,'msg':msg})    

        # Step5. running hla typing => sending jobs to task.py
        task_id = async_task('DjangoWeb.tasks.TSA_DNA_and_RNAseq',data_path=UPLOAD_PATH, parameters=parameters)
  
        # Step6. sending mail with link （之後記得開）
        user_status_link = "/" + uid + "/statusdrnaneo"
        send_mail('Neoantigen identification Task Submitted', f'Hello,\n\nYor task for neoantigen identification with DNA-seq was sucessfully submitted to our online system. Please kindly wait for a few hours or days to receive a result. You can check the status of your submitted task.\nYour status link: {web_url}{user_status_link}\n\nBest wishes,\nNARWHAL team', from_email, [mail], fail_silently=True)
 
        # Step7. leading to user's specific status.html
        user_status_link = "/" + uid + "/statusdrnaneo"
        return render(request, 'submit_response.html',
                      {'uid': uid,
                       'job_numbers': job_numbers,
                       'start_time': start_time,
                       'expected_ended_time': expected_ended_time,
                       'user_status_link': user_status_link})



## find overlapped neoantigens
def status_overlapped(request, task_id="not_passed"):
    status_dict={}
    if(list(User_Job.objects.filter(user_id=task_id))==[]):
        return render(request,'no_id_match.html',{'task_id':task_id})
    return render(request,'status_overlapped.html',status_dict)

def report_overlapped(request, task_id="not_passed"):
    if(list(User_Job.objects.filter(user_id=task_id))==[]):
        return render(request,'no_id_match.html',{'task_id':task_id})
    task=User_Job.objects.filter(user_id=task_id)[0]
    
    #overview page
    overview={}
    overview['submit_time']=task.submission_time
    overview['start_time']=task.start_time
    overview['end_time']=task.end_time
    success=1
    total_file=1
    
    # Check success or fail
    if(task.total_status=="FAILED"):
        success=0      
        failed_step="SYSTEM"

        return render(request,'report_overlapped.html',
                    {'hla':task.hla,
                     'task_id':task_id,
                     'success':success,
                     'failed_step':failed_step,
                     'overview':overview,
                     'total_file':total_file,
                    })
    elif(task.total_status=="WAITING" or task.total_status=="RUNNING"):
        return render(request,'status_overlapped.html',{})
    
    # get system info tables    
    databases_df = pd.read_csv(f'{DATA}/{task_id}/shared/overlapped_shared_peptide_{task.hla}_summary.tsv', sep="\t", engine='python')
    databases_list = databases_df[databases_df.columns[:3]].values.tolist()

    basic_dic={'hla':task.hla,
               'success':success,
               'task_id':task_id,
               'overview':overview,
               'total_file':total_file,
               'databases_list':databases_list,
              }
    return render(request, 'report_overlapped.html',basic_dic)


def retrieve_overlapped(request, task_id="not_passed"):
    if(list(User_Job.objects.filter(user_id=task_id))==[]):
        return render(request,'no_id_match.html',{'task_id':task_id})
    else:
        myjob = User_Job.objects.get(user_id=task_id)
        status_dict = {}
        status_dict['total_status'] = myjob.total_status
        status_dict['shared_neoantigen_status'] = myjob.shared_neoantigen_status  
        status_dict['task_id'] = task_id

        # Saving JSON file
        with open(f'/{UPLOAD_BASE_PATH}/{task_id}/status_report.json','w',encoding = 'utf-8') as f :
            json.dump(status_dict,f, indent=2, sort_keys=True, ensure_ascii=False)
    return JsonResponse(status_dict)


def overlapped_tsv(request, task_id):
    task=User_Job.objects.filter(user_id=task_id)[0]
    hla_tsv = open(f'/{UPLOAD_BASE_PATH}/{task_id}/shared/overlapped_shared_peptide_{task.hla}_summary.tsv', 'rb')
    response = FileResponse(hla_tsv)
    return response
    

def find_overlapped_result(request):
    # This pipeline is to run find_overlapped_result.
    if request.method == 'POST':
        # Step1. getting input files (tsv) & user ID
        try:
            upload_id = re.sub(r"[\W]", "", request.POST.get('upload_id'))
            uid = upload_id
            input_list = []
            if upload_id == '':
                msg = "Your upload files cannot not be accepted, please conform to the correct file format and the number of your upload files."
                return render(request, 'not_allow.html', {'uid': uid, 'msg': msg})
            upload_path = str(Path(UPLOAD_BASE_PATH).resolve().joinpath(upload_id))
            if _is_path_exist(upload_path) == False:
                makedirs(upload_path)
            tsv_files = [file for file in os.listdir(upload_path) if file.endswith(".tsv")]
            tsv_files_sorted = sorted(tsv_files, key=lambda file: os.path.getmtime(os.path.join(upload_path, file)))
            for file in tsv_files_sorted:
                input_list.append(os.path.join(upload_path, file))

            if len(input_list)<=1:
                msg = "Please upload at least two TSV files!"
                return render(request, 'not_allow.html', {'uid': uid, 'msg': msg})
            # set sample_names
            task=User_Job.objects.filter(user_id=uid)[0]
            sample_names = ast.literal_eval(task.sample_names)

            if len(input_list) != len(sample_names):                
                msg = "The number of sample names should be equal to the number of files."
                return render(request, 'not_allow.html', {'uid': uid, 'msg': msg})
        
        except:
            msg = "Your upload files cannot not be accepted, please conform to the correct file formats."
            return render(request, 'not_allow.html', {'uid': uid, 'msg': msg})
        
        # Step2. parameter setting
        try:
            parameters = {}
            file_prefix = "shared"
            parameters['sample_names'] = sample_names
            parameters['input_list'] = input_list
            parameters['output_path'] = UPLOAD_BASE_PATH +  '/' + upload_id
            parameters['file_prefix'] = file_prefix
            parameters['database_path'] = DATABASE_PATH
            parameters['task_id'] = upload_id
            if(len(list(request.POST.getlist('HLA-multiple')))==0):
                msg = "Please choose one HLA type!"
                return render(request, 'not_allow.html', {'uid': uid, 'msg': msg})
            else:
                hla_type = request.POST.getlist('HLA-multiple')
            parameters['hla_type'] = hla_type[0].split("-")[1]
        except:
            msg = "Your upload files or parameters cannot not be accepted, please conform to the correct file and parameter formats"
            return render(request, 'not_allow.html', {'uid': uid, 'msg': msg})

        # Step3. getting IP
        # ip_address = get_client_ip(request)  #make sure this line work in real environment
        ip_info = get_location()
        ip_address = ip_info['ip']

        if ip_address is not None:
            print("We have a publicly-routable IP address for client")
            submitted_job_number=User_Job.objects.filter(ip=ip_address,total_status__in=["WAITING","RUNNING"]).count()
            # if(submitted_job_number>2):  #block more than two jobs from single ip address
            #     msg="Only 2 tasks are allowed to each IP. We cannot accept it since your 2 tasks are still waiting or running on the system."
            #     return render(request,'not_allow.html',{'uid':uid,'msg':msg}) 
            
            try:
                country=reader.get(ip_address)['country']['names']['en']
            except:
                country="NA"        
        else:
            ip_address="NA"
            country="NA"
            print("We don't have an IP address for client or IP is private")
        
        # Step4. saving uid into model 
        try: 
            mail = request.POST['email']
            times = datetime.datetime.now()
            start_time = times.strftime("%Y-%m-%d %H:%M:%S")
            expected_ended_time = "less than 5 mins"
            user = User_Job.objects.filter(user_id=uid)[0]
            user.hla=parameters['hla_type'].replace(':','_')
            user.ip=ip_address
            user.mail=mail
            user.submission_time=times
            user.start_time=times
            user.end_time = datetime.datetime.now()       
            user.save(update_fields=['hla','ip','mail','submission_time','start_time','end_time'])

            ip_log.objects.create(ip=ip_address,country=country,submission_time=times,functions="HLA")
            ip_dict = {}
            ip_dict['user_id'] = uid
            ip_dict['ip_address'] = ip_address
            ip_dict['country'] = country
            ip_dict['submission_time'] = str(times)
            ip_dict['task_type'] = "find overlapped"
            ip_dict['mail'] = mail

            with open(f'/{UPLOAD_BASE_PATH}/{uid}/user_info.json','w',encoding = 'utf-8') as f :
                json.dump(ip_dict,f, indent=2, sort_keys=True, ensure_ascii=False)
            job_numbers=User_Job.objects.filter(total_status__in=['WAITING','RUNNING']).count()
        except:
            #return email not allowed
            msg="Your email address is not a correct one."
            return render(request,'not_allow.html',{'uid':uid,'msg':msg})    
        
        task_id=async_task('DjangoWeb.tasks.run_find_overlapped', parameters=parameters)
        
        # Step6. sending mail with link 
        user_status_link = "/" + uid + "/status-overlapped"
        send_mail('Shared Neoantigen Discovery Task Submitted', f'Hello,\n\nYor task for discovering shared neoantigens was sucessfully submitted to our online system. Please kindly wait for a few hours to receive a result. You can check the status of your submitted task.\nYour status link: {web_url}{user_status_link}\n\nBest wishes,\nNARWHAL team', from_email, [mail], fail_silently=True)
 
        # Step7. leading to user's specific status.html
        user_status_link = "/" + uid + "/status-overlapped"
        return render(request, 'submit_response.html',
                      {'uid': uid,
                       'job_numbers': job_numbers,
                       'start_time': start_time,
                       'expected_ended_time': expected_ended_time,
                       'user_status_link': user_status_link})
