import subprocess as sp
from pathlib import Path
from os import path, environ, makedirs
import os
import time
import datetime
import pandas as pd
from collections import Counter
import ast
import pickle
import json
from django.core.mail import send_mail
from .models import User_Job,ip_log,bac_species
from .views import UPLOAD_BASE_PATH
from django.utils.html import mark_safe
from django.conf import settings
import shutil
import re
import gzip
import requests, requests_ftp
from .googledrive_downloader import GoogleDriveDownloader
import sys
from django.conf import settings
from_email = settings.DEFAULT_FROM_EMAIL


web_url = settings.WEB_URL 

def _is_path_exist(dir, error_msg=False):
    if dir == None: 
        return -1
    elif path.exists(dir): 
        return 0
    else: 
        return -1

def failed_email(mail, uid, task, report):
    #send mail for failed task
    send_mail(f'{task} Task Failed!', f'Hello,\n\nYor task for {task} is failed. Please kindly check the report of your submitted task.\nYour report link: ' + web_url + "/" + uid + f"/{report}\n\nBest wishes,\nNARWHAL team", from_email, [mail], fail_silently=True)
    return 0

def successful_email(mail, uid, task, report):
    #send mail for successful task
    send_mail(f'{task} Task Successful!', f'Hello,\n\nYor task for {task} is successful. Please kindly check the report of your submitted task.\nYour report link: ' + web_url + "/" + uid + f"/{report}\n\nBest wishes,\nNARWHAL team", from_email, [mail], fail_silently=True)
    return 0

def Cat(input_fasta, output_fasta):
    try:
        cmd = f"cat {input_fasta} >> {output_fasta}"
        p = sp.Popen(cmd, stdout=sp.PIPE, stderr=sp.PIPE, shell=True)
        stdout, stderr = p.communicate()
        print(cmd)
        if p.returncode != 0:
            stderr = stderr.decode(encoding='utf-8')
            sys.stderr.write("Fail.\nError %d: %s\n" % (p.returncode, stderr))
            sys.exit(1)
        return 0
    except:
        return -1

def Remove(data):
    try:
        cmd = f"rm {data}"
        p = sp.Popen(cmd, stdout=sp.PIPE, stderr=sp.PIPE, shell=True)
        stdout, stderr = p.communicate()
        print(cmd)
        if p.returncode != 0:
            stderr = stderr.decode(encoding='utf-8')
            sys.stderr.write("Fail.\nError %d: %s\n" % (p.returncode, stderr))
            sys.exit(1)
        return 0
    except:
        return -1

def Makedir(dir):
    try:
        cmd = f"mkdir -p {dir}"
        p = sp.Popen(cmd, stdout=sp.PIPE, stderr=sp.PIPE, shell=True)
        stdout, stderr = p.communicate()
        print(cmd)
        if p.returncode != 0:
            stderr = stderr.decode(encoding='utf-8')
            sys.stderr.write("Fail.\nError %d: %s\n" % (p.returncode, stderr))
            sys.exit(1)
        return 0
    except:
        return -1

def Move(dir1, dir2):
    try:
        cmd = f"mv {dir1} {dir2}"
        p = sp.Popen(cmd, stdout=sp.PIPE, stderr=sp.PIPE, shell=True)
        stdout, stderr = p.communicate()
        print(cmd)
        if p.returncode != 0:
            stderr = stderr.decode(encoding='utf-8')
            sys.stderr.write("Fail.\nError %d: %s\n" % (p.returncode, stderr))
            sys.exit(1)
        return 0
    except:
        return -1

#taken from this StackOverflow answer: https://stackoverflow.com/a/39225039
import requests

def download_file_from_google_drive(id, destination):
    URL = "https://docs.google.com/uc?export=download"

    session = requests.Session()

    response = session.get(URL, params = { 'id' : id }, stream = True)
    token = get_confirm_token(response)

    if token:
        params = { 'id' : id, 'confirm' : token }
        response = session.get(URL, params = params, stream = True)

    save_response_content(response, destination)    

def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value

    return None

def save_response_content(response, destination):
    CHUNK_SIZE = 32768

    with open(destination, "wb") as f:
        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)

## download input files from URLs
def run_data_preparation(source_path, destination_path, dict_urls):
    try:
        print("Data preparation.")
        if not path.exists(destination_path):
            makedirs(destination_path)
        dest_raw_path = str(Path(destination_path).resolve().joinpath('raw'))
        if not path.exists(dest_raw_path):
            makedirs(dest_raw_path)
        if not path.exists(source_path):
            makedirs(source_path)
        if len(dict_urls): # data come from URLs
            for new_file_name, url in dict_urls.items():
                file_types = ['','dna.','rna.']
                # m1 = re.search('google\.com.+id=(.+)\&*', url) ## Retired
                m1 = re.search('google\.com\/file\/d\/(.+)\/', url)
                upload_raw_file = source_path + new_file_name
                if m1:
                    # Use GoogleDriveDownloader module
                    id = m1.group(1)
                    response = GoogleDriveDownloader.get_response(id)
                    # download_file_from_google_drive(id, upload_raw_file) # new added
                else:
                    # Direct download
                    if not re.match(r'^(http|https|ftp)://', url):
                        url = 'http://'+url
                    requests_ftp.monkeypatch_session()
                    session = requests.Session()
                    response = session.get(url, stream=True)
                # Check file existing
                # if response.ok == False:
                #     return -1
                # else:
                # Get the file name and extension
                if m1:
                    m2 = re.search('filename="(.+)"', response.headers['Content-Disposition'])
                    file_name = m2.group(1)
                else:
                    file_name = response.url.split('/')[-1]
                    extension = path.splitext(file_name)[1]
                    # Check file format
                if new_file_name.endswith('.mass.fasta'):
                    if not re.search('\.(fasta|fa|fna)+(\.gz)*$', file_name):
                        return -1
                    # Save a downloaded file to disk
                    if extension == '.gz':
                        with open(str(Path(source_path).resolve().joinpath(new_file_name)), "wb") as destination:
                            with gzip.GzipFile(fileobj=response.raw) as source:
                                shutil.copyfileobj(source, destination)
                    else:
                        with open(str(Path(source_path).resolve().joinpath(new_file_name)), "wb") as destination:
                            for chunk in response.iter_content(32768):
                                if chunk:  # filter out keep-alive new chunks
                                    destination.write(chunk)
                else:
                    with open(str(Path(source_path).resolve().joinpath(new_file_name)), "wb") as destination:
                        for chunk in response.iter_content(32768):
                            if chunk:  # filter out keep-alive new chunks
                                    destination.write(chunk)                 
        # save files to UID/raw
        # shutil.copy2(str(Path(source_path).resolve()), dest_raw_path)
        for type in file_types:
            if path.exists(str(Path(source_path).resolve().joinpath(f'N.{type}R1.fastq.gz'))):
                shutil.copy2(str(Path(source_path).resolve().joinpath(f'N.{type}R1.fastq.gz')), dest_raw_path)
            elif path.exists(str(Path(source_path).resolve().joinpath(f'N.{type}R2.fastq.gz'))):        
                shutil.copy2(str(Path(source_path).resolve().joinpath(f'N.{type}R2.fastq.gz')), dest_raw_path)
            if path.exists(str(Path(source_path).resolve().joinpath(f'T.{type}R1.fastq.gz'))):
                shutil.copy2(str(Path(source_path).resolve().joinpath(f'T.{type}R1.fastq.gz')), dest_raw_path)
            if path.exists(str(Path(source_path).resolve().joinpath(f'T.{type}R2.fastq.gz'))):        
                shutil.copy2(str(Path(source_path).resolve().joinpath(f'T.{type}R2.fastq.gz')), dest_raw_path)
            if path.exists(str(Path(source_path).resolve().joinpath(f'{type}mass.fasta'))):
                shutil.copy2(str(Path(source_path).resolve().joinpath(f'{type}mass.fasta')), dest_raw_path)
        shutil.rmtree(dest_raw_path)
        print("Data preparation is successful!")
        return 0
        
    except Exception as e:
        return -1

## HLA genotyping

def HLA_typing_1_QC(r1_file_path, r2_file_path, thread, database_path, output_path, sample_name):
    print("HLA_typing_1_QC")
    try:
        cmd1 = f"HLA_typing_1_QC.py -n1 {r1_file_path} -n2 {r2_file_path} -t {thread} -dir {database_path} -o {output_path} -n {sample_name}" 
        p = sp.Popen(cmd1, stdout=sp.PIPE, stderr=sp.PIPE, shell=True)
        print(cmd1)
        stdout, stderr = p.communicate()
        if p.returncode != 0:
            stderr = stderr.decode(encoding='utf-8')
            sys.stderr.write("Fail.\nError %d: %s\n" % (p.returncode, stderr))
            sys.exit(1)
        print("HLA_typing_1_QC is successful!")
        return 0
    except:
        return -1
    

def HLA_typing_2_genotyping(r1_trimmed_file_path, r2_trimmed_file_path, database_path, output_path, sample_name, sample_type):
    try:
        cmd2 = f"HLA_typing_2_genotyping.py -n1 {r1_trimmed_file_path} -n2 {r2_trimmed_file_path} -dir {database_path} -o {output_path} -n {sample_name} {sample_type}"
        print(cmd2)
        p = sp.Popen(cmd2, stdout=sp.PIPE, stderr=sp.PIPE, shell=True)
        stdout, stderr = p.communicate()
        if p.returncode != 0:
            stderr = stderr.decode(encoding='utf-8')
            sys.stderr.write("Fail.\nError %d: %s\n" % (p.returncode, stderr))
            sys.exit(1)
        print("HLA_typing_2_genotyping is successful!")
        return 0
    except:
        return -1
    

def run_hla_typing(data_path, parameters):
    # Step1-1 Set parameters
    uid = parameters['task_id']
    user = User_Job.objects.filter(user_id=uid)[0]
    user.total_status = "RUNNING"
    user.start_time = datetime.datetime.now()
    user.save(update_fields=['total_status', 'start_time'])
    r1_file = parameters['r1_file']
    r2_file = parameters['r2_file']
    thread = parameters['thread']
    database_path = parameters['database_path']
    output_path = parameters['output_path']
    sample_name = parameters['sample_name']
    dict_urls = parameters['dict_urls']
    sample_type = parameters['sample_type']
    r1_file_path = data_path + '/' + r1_file
    r2_file_path = data_path + '/' + r2_file
    mail = user.mail
    task = "HLA Genotyping"
    
    try:
        # check if the file exists
        hla_tsv = output_path + f"/HLA_typing/{sample_name}/2-hla-typing/{sample_name}_result.tsv"
        r1_trimmed_file_path = f"{output_path}/HLA_typing/{sample_name}/1-fastq/trimmed/{sample_name}_R1.trimmed.paired.fastq.gz"
        r2_trimmed_file_path = f"{output_path}/HLA_typing/{sample_name}/1-fastq/trimmed/{sample_name}_R2.trimmed.paired.fastq.gz"
        r1_un_trimmed_file_path = f"{output_path}/HLA_typing/{sample_name}/1-fastq/trimmed/{sample_name}_R1.trimmed.unpaired.fastq.gz"
        r2_un_trimmed_file_path = f"{output_path}/HLA_typing/{sample_name}/1-fastq/trimmed/{sample_name}_R2.trimmed.unpaired.fastq.gz"

        if _is_path_exist(hla_tsv)!=0: 
            # Step1-2 start data preparation
            if bool(dict_urls != {})== True:
                user.data_preparation_status="RUNNING"
                user.save(update_fields=['data_preparation_status'])
                data_tmp_path = str(Path(UPLOAD_BASE_PATH).resolve().joinpath(uid))
                data_preparation_stat = run_data_preparation(data_tmp_path, data_path, dict_urls)
                if(data_preparation_stat!=0):
                    print("pipeline stop at data preparation")
                    user.error_log="INPUT DATA"
                    user.data_preparation_status="FAILED"
                    user.quality_check="FAILED"
                    user.total_status="FAILED"
                    user.end_time=datetime.datetime.now()
                    user.save(update_fields=['error_log','data_preparation_status','total_status','end_time'])
                    failed_email(mail, uid, task, report="report")
                    return -1
                else:
                    user.data_preparation_status="SUCCESSFUL"
                    user.save(update_fields=['data_preparation_status'])
            else:
                user.data_preparation_status="SUCCESSFUL"
                user.save(update_fields=['data_preparation_status']) 
               
            # Step2-1. Run quality check
            user.quality_check_status="RUNNING"
            user.save(update_fields=['quality_check_status'])
            run_QC = HLA_typing_1_QC(r1_file_path, r2_file_path, thread, database_path, output_path, sample_name)
            if(run_QC!=0):
                user.error_log="QC"
                user.quality_check_status="FAILED"
                user.total_status="FAILED"
                user.end_time=datetime.datetime.now()
                user.save(update_fields=['error_log','quality_check_status','total_status','end_time'])
                failed_email(mail, uid, task, report="report")
            else:
                user.quality_check_status="SUCCESSFUL"
                user.save(update_fields=['quality_check_status'])

            # Step2-2. Run optitype
            user.hla_status="RUNNING"
            user.save(update_fields=['hla_status'])
            run_optitype = HLA_typing_2_genotyping(r1_trimmed_file_path, r2_trimmed_file_path, database_path, output_path, sample_name, sample_type)
            if(run_optitype!=0):
                user.error_log="HLA_typing"
                user.hla_status="FAILED"
                user.total_status="FAILED"
                user.end_time=datetime.datetime.now()
                user.save(update_fields=['error_log','hla_status','total_status','end_time'])
                failed_email(mail, uid, task, report="report")
            else:
                user.hla_status="SUCCESSFUL"
                user.save(update_fields=['hla_status'])
        
            # Step2-3. Results confirmation
            hla_tsv = output_path + f"/HLA_typing/{sample_name}/2-hla-typing/{sample_name}_result.tsv"
            if _is_path_exist(hla_tsv)!=0:
                user.error_log="HLA_typing"
                user.hla_result_status="FAILED"
                user.total_status="FAILED"
                user.end_time=datetime.datetime.now()
                user.save(update_fields=['error_log','hla_result_status','total_status','end_time'])
                failed_email(mail, uid, task, report="report")
            else:
                user.hla_result_status="SUCCESSFUL"
                user.total_status = "SUCCESSFUL"
                user.end_time = datetime.datetime.now()
                user.save(update_fields=['data_preparation_status','quality_check_status','hla_status','hla_result_status','total_status','end_time'])
                successful_email(mail, uid, task, report="report")
            
            # Step2-4. Remove raw data
            if _is_path_exist(r1_file_path)!=0:
                Remove(r1_file_path)
            if _is_path_exist(r2_file_path)!=0:
                Remove(r2_file_path)
            if _is_path_exist(r1_trimmed_file_path)!=0:
                Remove(r1_trimmed_file_path)
            if _is_path_exist(r2_trimmed_file_path)!=0:
                Remove(r2_trimmed_file_path)
            if _is_path_exist(r1_un_trimmed_file_path)!=0:
                Remove(r1_un_trimmed_file_path)
            if _is_path_exist(r2_un_trimmed_file_path)!=0:
                Remove(r2_un_trimmed_file_path)
                
        else:
            user.quality_check_status="SUCCESSFUL"
            user.hla_result_status="SUCCESSFUL"
            user.hla_status="SUCCESSFUL"
            user.total_status = "SUCCESSFUL"
            user.end_time = datetime.datetime.now()     
            user.save(update_fields=['data_preparation_status','quality_check_status','hla_status','hla_result_status','total_status','end_time'])        
            successful_email(mail, uid, task, report="report")
            return 0        
    except:
        uid = parameters['task_id']
        user = User_Job.objects.filter(user_id=uid)[0]
        user.total_status="FAILED"
        user.error_log="Data_format"
        user.end_time = datetime.datetime.now()       
        user.save(update_fields=['error_log','total_status','end_time'])
        failed_email(mail, uid, task, report="report")
        return -1

## find overlpaaed
def find_overlapped(input_files, hla_type, output_path, file_prefix, sample_name):
    try:
        cmd = f"find_overlapped.py -i {input_files} -HLA {hla_type} -o {output_path} --file_prefix {file_prefix} --sample_name {sample_name}"
        print(cmd)
        p = sp.Popen(cmd, stdout=sp.PIPE, stderr=sp.PIPE, shell=True)
        stdout, stderr = p.communicate()
        if p.returncode != 0:
            stderr = stderr.decode(encoding='utf-8')
            sys.stderr.write("Fail.\nError %d: %s\n" % (p.returncode, stderr))
            sys.exit(1)
        return 0
    except:
        return -1

def run_find_overlapped(parameters):
    # Step1-1 Set parameters
    try:
        uid = parameters['task_id']
        user = User_Job.objects.filter(user_id=uid)[0]
        user.total_status = "RUNNING"
        user.start_time = datetime.datetime.now()
        user.save(update_fields=['total_status', 'start_time'])
        input_list = parameters['input_list']
        hla_type = parameters['hla_type']
        file_prefix = parameters['file_prefix']
        sample_names = parameters['sample_names'] 
        output_path = parameters['output_path']
        mail = user.mail
        task = "Overlapped Neoantigen Discovery"
        # sample_name = " ".join(map(str, list(range(1,input_len+1))))
        sample_names = " ".join(map(str, sample_names))
        input_files = " ".join(map(str, input_list))
        # Step2-1. Run shared neoantigen discovery
        user.shared_neoantigen_status="RUNNING"
        user.save(update_fields=['shared_neoantigen_status'])
        run_shared = find_overlapped(input_files, hla_type, output_path, file_prefix, sample_names)
        if(run_shared!=0):
            user.error_log="shared_neoantigen_discovery"
            user.shared_neoantigen_status="FAILED"
            user.total_status="FAILED"
            user.end_time=datetime.datetime.now()
            user.save(update_fields=['error_log','shared_neoantigen_status','total_status','end_time'])
            failed_email(mail, uid, task, report="report-overlapped")
        else:
            user.shared_neoantigen_status="SUCCESSFUL"
            user.total_status="SUCCESSFUL"
            user.save(update_fields=['shared_neoantigen_status','total_status'])
            successful_email(mail, uid, task, report="report-overlapped")
    except:
        uid = parameters['task_id']
        user = User_Job.objects.filter(user_id=uid)[0]
        user.shared_neoantigen_status="FAILED"
        user.total_status="FAILED"
        user.error_log="Data_format"
        user.end_time = datetime.datetime.now()       
        user.save(update_fields=['error_log','shared_neoantigen_status','total_status','end_time'])
        failed_email(mail, uid, task, report="report-overlapped")
        return -1

    



    
## mTSA with DNA-seq

def DNA_1_data_processing(T_r1_file_path, T_r2_file_path, N_r1_file_path, N_r2_file_path, thread, DNA_reference,illuminaclip, output_path, normal_sample_name, tumor_sample_name):
    try:
        cmd1 = f"DNA_1_data_processing.py -t1 {T_r1_file_path} -t2 {T_r2_file_path} -n1 {N_r1_file_path} -n2 {N_r2_file_path} -t {thread} -r {DNA_reference} --illuminaclip {illuminaclip} -o {output_path} --sample_name_tumor {tumor_sample_name} --sample_name_normal {normal_sample_name}" 
        print(cmd1)
        p = sp.Popen(cmd1, stdout=sp.PIPE, stderr=sp.PIPE, shell=True)
        stdout, stderr = p.communicate()
        if p.returncode != 0:
            stderr = stderr.decode(encoding='utf-8')
            sys.stderr.write("Fail.\nError %d: %s\n" % (p.returncode, stderr))
            sys.exit(1)
        return 0
    except:
        return -1

def DNA_2_gatk(T_alignment_bam, N_alignment_bam, S31285117_Covered, ref_vcf, tmp, DNA_reference, output_path, normal_sample_name, tumor_sample_name):
    try:
        cmd2_T = f"DNA_2_gatk.py -i {T_alignment_bam} -l {S31285117_Covered} -tmp {tmp} -r {DNA_reference} -o {output_path} -n {tumor_sample_name} --create_index true -k {ref_vcf}" 
        print(cmd2_T)
        p = sp.Popen(cmd2_T, stdout=sp.PIPE, stderr=sp.PIPE, shell=True)
        stdout, stderr = p.communicate()
        if p.returncode != 0:
            stderr = stderr.decode(encoding='utf-8')
            sys.stderr.write("Fail.\nError %d: %s\n" % (p.returncode, stderr))
            sys.exit(1)
        
        cmd2_N = f"DNA_2_gatk.py -i {N_alignment_bam} -l {S31285117_Covered} -tmp {tmp} -r {DNA_reference} -o {output_path} -n {normal_sample_name} --create_index true -k {ref_vcf}" 
        print(cmd2_N)
        p = sp.Popen(cmd2_N, stdout=sp.PIPE, stderr=sp.PIPE, shell=True)
        stdout, stderr = p.communicate()
        if p.returncode != 0:
            stderr = stderr.decode(encoding='utf-8')
            sys.stderr.write("Fail.\nError %d: %s\n" % (p.returncode, stderr))
            sys.exit(1)
        return 0
    except:
        return -1

def DNA_3_SM_calling(N_bam, T_bam, S31285117_Covered, gnomad, pan, small_exac_common_vcf, ip, DNA_reference, output_path, normal_sample_name, tumor_sample_name, tmp):
    try:
        cmd3 = f"DNA_3_SM_calling.py -nb {N_bam} -tb {T_bam} -l {S31285117_Covered} -ip {ip} -v {small_exac_common_vcf} -pan {pan} -g {gnomad} -r {DNA_reference} -o {output_path} --sample_name_tumor {tumor_sample_name} --sample_name_normal {normal_sample_name} -tmp {tmp}" 
        print(cmd3)
        p = sp.Popen(cmd3, stdout=sp.PIPE, stderr=sp.PIPE, shell=True)
        stdout, stderr = p.communicate()
        if p.returncode != 0:
            stderr = stderr.decode(encoding='utf-8')
            sys.stderr.write("Fail.\nError %d: %s\n" % (p.returncode, stderr))
            sys.exit(1)
        return 0
    except:
        return -1
    
def DNA_4_GM_calling(T_r1_file_path, T_r2_file_path, N_r1_file_path, N_r2_file_path, S31285117_Covered, DNA_reference, thread, dragen_reference, output_path, str_table, normal_sample_name, tumor_sample_name, tmp):
    try:
        cmd4 = f"DNA_4_GM_calling.py -t1 {T_r1_file_path} -t2 {T_r2_file_path} -n1 {N_r1_file_path} -n2 {N_r2_file_path} -l {S31285117_Covered} -r {DNA_reference} -t {thread} --dragen_reference_path {dragen_reference} --RGID Cancer -o {output_path} -str {str_table} --sample_name_tumor {tumor_sample_name} --sample_name_normal {normal_sample_name} -tmp {tmp}" 
        print(cmd4)
        p = sp.Popen(cmd4, stdout=sp.PIPE, stderr=sp.PIPE, shell=True)
        stdout, stderr = p.communicate()
        if p.returncode != 0:
            stderr = stderr.decode(encoding='utf-8')
            sys.stderr.write("Fail.\nError %d: %s\n" % (p.returncode, stderr))
            sys.exit(1)
        return 0
    except:
        return -1
    
def DNA_5_phasing(somatic_vcf, germline_vcf, T_bam, S31285117_Covered, DNA_reference, gatk3_jar_file, dir_plugins, dir_cache, sequence_dictionary, output_path, tumor_sample_name, tmp):
    try:
        cmd5 = f"DNA_5_phasing.py -svcf {somatic_vcf} -gvcf {germline_vcf} -r {DNA_reference} -tb {T_bam} -v {S31285117_Covered} --gatk3_jar_file {gatk3_jar_file} --dir_plugins {dir_plugins} --dir_cache {dir_cache} --sequence_dictionary {sequence_dictionary} -o {output_path} -nt {tumor_sample_name} -tmp {tmp}" 
        print(cmd5)
        p = sp.Popen(cmd5, stdout=sp.PIPE, stderr=sp.PIPE, shell=True)
        stdout, stderr = p.communicate()
        if p.returncode != 0:
            stderr = stderr.decode(encoding='utf-8')
            sys.stderr.write("Fail.\nError %d: %s\n" % (p.returncode, stderr))
            sys.exit(1)
        return 0
    except:
        return -1
    
def DNA_6_pvacseq(somatic_vcf, phasing_vcf, hla_type, iedb_install_directory, cosmic_database, output_path, tumor_sample_name, thread, max_strong, max_intermediate, max_weak ,RNA_expression_level = "None", tumor_expression_threshold = 1.0, minimal_expression_ratio = "None"):
    try:
        cmd6 = f"DNA_6_pvacseq.py -i {somatic_vcf} -p {phasing_vcf} -HLA {hla_type} --iedb_install_directory {iedb_install_directory} --cosmic_database {cosmic_database} -o {output_path} -n {tumor_sample_name} -t {thread} --max_strong {max_strong} --max_intermediate {max_intermediate} --max_weak {max_weak} --RNA_expression_level {RNA_expression_level} --tumor_expression_threshold {tumor_expression_threshold} --minimal_expression_ratio {minimal_expression_ratio}" 
        print(cmd6)
        p = sp.Popen(cmd6, stdout=sp.PIPE, stderr=sp.PIPE, shell=True)
        stdout, stderr = p.communicate()
        if p.returncode != 0:
            stderr = stderr.decode(encoding='utf-8')
            sys.stderr.write("Fail.\nError %d: %s\n" % (p.returncode, stderr))
            sys.exit(1)
        return 0
    except:
        return -1

def DNA_7_mass_merge(dna_fasta, mass_fasta, output_path, name, mass_name):
    try:
        cmd7 = f"DNA_7_mass_merge.py -r {dna_fasta} -m {mass_fasta} -o {output_path} -n {name} -mn {mass_name}" 
        print(cmd7)
        p = sp.Popen(cmd7, stdout=sp.PIPE, stderr=sp.PIPE, shell=True)
        stdout, stderr = p.communicate()
        if p.returncode != 0:
            stderr = stderr.decode(encoding='utf-8')
            sys.stderr.write("Fail.\nError %d: %s\n" % (p.returncode, stderr))
            sys.exit(1)
        return 0
    except:
        return -1

def mTSA_DNAseq(data_path, parameters):
    print("Run mTSA_DNAseq")
    # Step1-1. Set parameters
    uid = parameters['task_id']
    user = User_Job.objects.filter(user_id=uid)[0]
    user.total_status = "RUNNING"
    user.start_time = datetime.datetime.now()
    user.save(update_fields=['total_status', 'start_time'])
    N_r1_file = parameters['N_r1_file']
    N_r2_file = parameters['N_r2_file']
    T_r1_file = parameters['T_r1_file']
    T_r2_file = parameters['T_r2_file']
    dict_urls = parameters['dict_urls']
    mass_file_path = parameters['mass_file_path'] 
    mass_step = parameters['mass_step']
    mass_sample_name = "mass.peptide"  
    thread = parameters['thread']
    ip = 15
    database_path = parameters['database_path']
    output_path = parameters['output_path']
    normal_sample_name = parameters['normal_sample_name']
    tumor_sample_name = parameters['tumor_sample_name']
    hla_type_ls = parameters['hla_type_ls']
    hla_typing_step = parameters['hla_typing_step']
    max_strong = parameters['max_ic_strong'] 
    max_intermediate = parameters['max_ic_inter'] 
    max_weak =parameters['max_ic_weak'] 
    hla_type = ','.join(hla_type_ls)
    N_r1_file_path = data_path + '/' + N_r1_file
    N_r2_file_path = data_path + '/' + N_r2_file
    T_r1_file_path = data_path + '/' + T_r1_file
    T_r2_file_path = data_path + '/' + T_r2_file
    mail = user.mail
    task = "Neoantigen Identification"
    DNA_reference = database_path + "/DNA_ref/ref/GRCh38.d1.vd1.fa"
    illuminaclip = database_path + "/adapters/TruSeq3-PE-2.fa:2:30:10:8:true"
    S31285117_Covered = database_path + "/hg38/S31285117_Covered.bed"
    ref_vcf = f"{database_path}/hg38/Homo_sapiens_assembly38.dbsnp138.vcf {database_path}/hg38/1000G_omni2.5.hg38.vcf {database_path}/hg38/Mills_and_1000G_gold_standard.indels.hg38.vcf"
    gnomad = database_path + "/hg38/af-only-gnomad.hg38.vcf"
    pan = database_path + "/hg38/1000g_pon.hg38.vcf.gz"
    small_exac_common_vcf = database_path + "/hg38/small_exac_common_3.hg38.vcf.gz"
    dragen_reference = database_path + "/dragmap/"
    str_table = database_path + "/dragmap/GRCh38.d1.vd1.str.table.tsv"
    gatk3_jar_file = database_path + "/gatk38/opt/gatk-3.8/GenomeAnalysisTK.jar"
    dir_plugins = database_path + "/iedb/VEP_plugins" 
    dir_cache = database_path + "/GRCh38.104_vep"
    sequence_dictionary = database_path + "/hg38/Homo_sapiens_assembly38.dict"
    iedb_install_directory = database_path + '/iedb'
    cosmic_database = database_path + '/cosmic/Census_allMon.csv'
    tmp = parameters['tmp_path']

    try:
        # check if the file exists
        final_tsv = output_path + f"/mTSA_DNAseq/6-hla-binding-affinity/{tumor_sample_name}/MHC_Class_I/{tumor_sample_name}.all_epitopes.aggregated.tsv" 
        if _is_path_exist(final_tsv)!=0: 
            # Step1-2 start data preparation
            if bool(dict_urls != {})== True:
                user.data_preparation_status="RUNNING"
                user.save(update_fields=['data_preparation_status'])
                data_tmp_path = str(Path(UPLOAD_BASE_PATH).resolve().joinpath(uid))
                data_preparation_stat = run_data_preparation(data_tmp_path, data_path, dict_urls)
                if(data_preparation_stat!=0):
                    print("pipeline stop at data preparation")
                    user.error_log="INPUT DATA"
                    user.data_preparation_status="FAILED"
                    user.total_status="FAILED"
                    user.end_time=datetime.datetime.now()
                    user.save(update_fields=['error_log','data_preparation_status','total_status','end_time'])
                    failed_email(mail, uid, task, report="report-dna")
                    return -1
                else:
                    user.data_preparation_status="SUCCESSFUL"
                    user.save(update_fields=['data_preparation_status'])
            else:
                user.data_preparation_status="SUCCESSFUL"
                user.save(update_fields=['data_preparation_status']) 

            # Step2-1. Run quality check
            user.quality_check_status="RUNNING"
            user.save(update_fields=['quality_check_status'])
            print("Run QC")
            run_QC = DNA_1_data_processing(T_r1_file_path, T_r2_file_path, N_r1_file_path, N_r2_file_path, thread, DNA_reference,illuminaclip, output_path, normal_sample_name, tumor_sample_name)
            if(run_QC!=0):
                print("pipeline stop at QC")    
                user.error_log="QC"
                user.quality_check_status="FAILED"
                user.total_status="FAILED"
                user.end_time=datetime.datetime.now()
                user.save(update_fields=['error_log','quality_check_status','total_status','end_time'])
                failed_email(mail, uid, task, report="report-dna")
            else:
                user.quality_check_status="SUCCESSFUL"
                user.save(update_fields=['quality_check_status'])

            # Step2-2. Run GATK4
            user.gatk_status="RUNNING"
            user.save(update_fields=['gatk_status'])
            T_alignment_bam = f"{output_path}/mTSA_DNAseq/1-fastq/aligment/{tumor_sample_name}_alignment.bam"
            N_alignment_bam = f"{output_path}/mTSA_DNAseq/1-fastq/aligment/{normal_sample_name}_alignment.bam"
            run_gatk4 = DNA_2_gatk(T_alignment_bam, N_alignment_bam, S31285117_Covered, ref_vcf, tmp, DNA_reference, output_path, normal_sample_name, tumor_sample_name)
            if(run_gatk4!=0):
                print("pipeline stop at gatk4")
                user.error_log="Data preprocessing"
                user.gatk_status="FAILED"
                user.total_status="FAILED"
                user.end_time=datetime.datetime.now()
                user.save(update_fields=['error_log','gatk_status','total_status','end_time'])
                failed_email(mail, uid, task, report="report-dna")
            else:
                user.gatk_status="SUCCESSFUL"
                user.save(update_fields=['gatk_status'])

            # Step2-3. Run Somatic mutation
            user.somatic_status="RUNNING"
            user.save(update_fields=['somatic_status'])
            T_bam = f"{output_path}/mTSA_DNAseq/2-gatk/{tumor_sample_name}/{tumor_sample_name}_recal.bam"
            N_bam = f"{output_path}/mTSA_DNAseq/2-gatk/{normal_sample_name}/{normal_sample_name}_recal.bam"
            run_somatic = DNA_3_SM_calling(N_bam, T_bam, S31285117_Covered, gnomad, pan, small_exac_common_vcf, ip, DNA_reference, output_path, normal_sample_name, tumor_sample_name, tmp)
            if(run_somatic!=0):
                print("pipeline stop at somatic mutation calling")
                user.error_log="Somatic mutation calling"
                user.somatic_status="FAILED"
                user.total_status="FAILED"
                user.end_time=datetime.datetime.now()
                user.save(update_fields=['error_log','somatic_status','total_status','end_time'])
                failed_email(mail, uid, task, report="report-dna")
            else:
                user.somatic_status="SUCCESSFUL"
                user.save(update_fields=['somatic_status'])
            
            # Step2-4. Run Germline mutation
            user.germline_status="RUNNING"
            user.save(update_fields=['germline_status'])
            TPR1 = f"{output_path}/mTSA_DNAseq/1-fastq/trimmed/T_R1.trimmed.paired.fastq.gz"
            TPR2 = f"{output_path}/mTSA_DNAseq/1-fastq/trimmed/T_R2.trimmed.paired.fastq.gz"
            NPR1 = f"{output_path}/mTSA_DNAseq/1-fastq/trimmed/N_R1.trimmed.paired.fastq.gz"
            NPR2 = f"{output_path}/mTSA_DNAseq/1-fastq/trimmed/N_R2.trimmed.paired.fastq.gz"
            T_bam = f"{output_path}/mTSA_DNAseq/2-gatk/{tumor_sample_name}/{tumor_sample_name}_recal.bam"
            N_bam = f"{output_path}/mTSA_DNAseq/2-gatk/{normal_sample_name}/{normal_sample_name}_recal.bam"
            run_germline = DNA_4_GM_calling(TPR1, TPR2, NPR1, NPR2, S31285117_Covered, DNA_reference, thread, dragen_reference, output_path, str_table, normal_sample_name, tumor_sample_name, tmp)
            if(run_germline!=0):
                print("pipeline stop at germline mutation calling")
                user.error_log="Germline mutation calling"
                user.germline_status="FAILED"
                user.total_status="FAILED"
                user.end_time=datetime.datetime.now()
                user.save(update_fields=['error_log','germline_status','total_status','end_time'])
                failed_email(mail, uid, task, report="report-dna")
            else:
                user.germline_status="SUCCESSFUL"
                user.save(update_fields=['germline_status'])

            # Step2-5. Run phasing
            user.phasing_status="RUNNING"
            user.save(update_fields=['phasing_status'])
            somatic_vcf = f"{output_path}/mTSA_DNAseq/3-somatic-mutation/{tumor_sample_name}/SelectVariants/{tumor_sample_name}.final.vcf"
            germline_vcf = f"{output_path}/mTSA_DNAseq/4-germline-mutation/{tumor_sample_name}/SelectVariants/{tumor_sample_name}.final.vcf"
            run_phasing = DNA_5_phasing(somatic_vcf, germline_vcf, T_bam, S31285117_Covered, DNA_reference, gatk3_jar_file, dir_plugins, dir_cache, sequence_dictionary, output_path, tumor_sample_name, tmp)
            if(run_phasing!=0):
                print("pipeline stop at phasing")
                user.error_log="Phasing"
                user.phasing_status="FAILED"
                user.total_status="FAILED"
                user.end_time=datetime.datetime.now()
                user.save(update_fields=['error_log','phasing_status','total_status','end_time'])
                failed_email(mail, uid, task, report="report-dna")
            else:
                user.phasing_status="SUCCESSFUL"
                user.save(update_fields=['phasing_status'])
            
            # Step 2-6-0 HLA genotyping
            if hla_typing_step == True:
                user.hla_status="RUNNING"
                user.save(update_fields=['hla_status'])
                run_optitype = HLA_typing_2_genotyping(NPR1, NPR2, database_path, output_path, normal_sample_name, "-DNA")
                if(run_optitype!=0):
                    user.error_log="HLA_typing"
                    user.hla_status="FAILED"
                    user.total_status="FAILED"
                    user.end_time=datetime.datetime.now()
                    user.save(update_fields=['error_log','hla_status','total_status','end_time'])
                    failed_email(mail, uid, task, report="report-dna")
                else:
                    hla_tsv = output_path + f"/HLA_typing/{normal_sample_name}/2-hla-typing/{normal_sample_name}_result.tsv"
                    optitype_tsv = pd.read_csv(hla_tsv, sep="\t")
                    optitype_A1 = optitype_tsv["A1"]
                    optitype_A2 = optitype_tsv["A2"]
                    optitype_B1 = optitype_tsv["B1"]
                    optitype_B2 = optitype_tsv["B2"]
                    optitype_C1 = optitype_tsv["C1"]
                    optitype_C2 = optitype_tsv["C2"]
                    hla_type_ls = [f"HLA-{optitype_A1[0]}",f"HLA-{optitype_A2[0]}",f"HLA-{optitype_B1[0]}",f"HLA-{optitype_B2[0]}",f"HLA-{optitype_C1[0]}",f"HLA-{optitype_C2[0]}"]
                    hla_type = f"HLA-{optitype_A1[0]},HLA-{optitype_A2[0]},HLA-{optitype_B1[0]},HLA-{optitype_B2[0]},HLA-{optitype_C1[0]},HLA-{optitype_C2[0]}"
                    print(hla_type)
                    user.hla_status="SUCCESSFUL"
                    user.save(update_fields=['hla_status'])
            else:
                print("HLA genotyping step has been skipped.")
                user.hla_status="SKIPPED"
                user.end_time=datetime.datetime.now()
                user.save(update_fields=['hla_status'])

            # Step2-6-1 Run Pvactools
            user.pvactools_status="RUNNING"
            user.save(update_fields=['pvactools_status'])
            somatic_vcf_gz = f"{output_path}/mTSA_DNAseq/5-phasing/{tumor_sample_name}/vep/{tumor_sample_name}.somatic.sn.vep.vcf.gz"
            phasing_vcf_gz = f"{output_path}/mTSA_DNAseq/5-phasing/{tumor_sample_name}/vep/{tumor_sample_name}.phased.vep.vcf.gz"
            run_pvactools = DNA_6_pvacseq(somatic_vcf_gz, phasing_vcf_gz, hla_type, iedb_install_directory, cosmic_database, output_path, tumor_sample_name, thread, max_strong, max_intermediate, max_weak)
            if(run_pvactools!=0):
                print("pipeline stop at Pvactools")
                user.error_log="Pvactools"
                user.pvactools_status="FAILED"
                user.total_status="FAILED"
                user.end_time=datetime.datetime.now()
                user.save(update_fields=['error_log','pvactools_status','total_status','end_time'])
                failed_email(mail, uid, task, report="report-dna")
            else:
                user.pvactools_status="SUCCESSFUL"
                user.save(update_fields=['pvactools_status'])

            # Step2-7. Run MASS
            if mass_step != True: 
                IEDB_list = []
                for hla in hla_type_ls:
                    if _is_path_exist(f"{iedb_install_directory}/MHC_fasta/IEDB_MHC_{hla}.fasta") == 0: 
                        IEDB_list.append(f"{iedb_install_directory}/MHC_fasta/IEDB_MHC_{hla}.fasta")
                input_fasta = ' '.join(IEDB_list)
                print(input_fasta)
                mass_file_path = f"{output_path}/dna.mass.fasta"
                Cat(input_fasta, mass_file_path)
            user.mass_status="RUNNING"
            user.save(update_fields=['mass_status'])
            dna_fasta = f"{output_path}/mTSA_DNAseq/6-hla-binding-affinity/{tumor_sample_name}/{tumor_sample_name}_filtered.fasta"
            dna_name = "dna.peptide"
            run_mass = DNA_7_mass_merge(dna_fasta, mass_file_path, output_path, dna_name, mass_sample_name)
            if(run_mass!=0):
                print("MASS merging step has errors.")
                user.error_log="MASS"
                user.mass_status="FAILED"
                user.end_time=datetime.datetime.now()
                user.save(update_fields=['error_log','mass_status'])
            else:
                user.mass_status="SUCCESSFUL"
                user.save(update_fields=['mass_status'])
        
            # Step2-8. Results confirmation
            final_tsv = output_path + f"/mTSA_DNAseq/6-hla-binding-affinity/{tumor_sample_name}/{tumor_sample_name}_TSA_candidates_with_cosmic.tsv"
            if _is_path_exist(final_tsv)!=0:
                user.error_log="result generation"
                user.dna_total_status="FAILED"
                user.total_status="FAILED"
                user.end_time=datetime.datetime.now()
                user.save(update_fields=['error_log','dna_total_status','total_status','end_time'])
                failed_email(mail, uid, task, report="report-dna")
            else:
                user.dna_total_status="SUCCESSFUL"
                user.total_status = "SUCCESSFUL"
                user.end_time = datetime.datetime.now()
                user.save(update_fields=['quality_check_status','gatk_status','somatic_status','germline_status','phasing_status','pvactools_status','mass_status','dna_total_status','total_status','end_time'])                
                successful_email(mail, uid, task, report="report-dna")

            # Step2-9. Remove raw data
            if _is_path_exist(N_r1_file_path)!=0:
                Remove(N_r1_file_path)
            if _is_path_exist(N_r2_file_path)!=0:
                Remove(N_r2_file_path)
            if _is_path_exist(T_r1_file_path)!=0:
                Remove(T_r1_file_path)
            if _is_path_exist(T_r2_file_path)!=0:
                Remove(T_r2_file_path)
            if _is_path_exist(TPR1)!=0:
                Remove(TPR1)
            if _is_path_exist(TPR2)!=0:
                Remove(TPR2)
            if _is_path_exist(NPR1)!=0:
                Remove(NPR1)
            if _is_path_exist(NPR2)!=0:
                Remove(NPR2)
            if _is_path_exist(T_bam)!=0:
                Remove(T_bam)
            if _is_path_exist(N_bam)!=0:
                Remove(N_bam)
            if _is_path_exist(T_alignment_bam)!=0:
                Remove(T_alignment_bam)
            if _is_path_exist(N_alignment_bam)!=0:
                Remove(N_alignment_bam) 

        else:
            user.quality_check_status="SUCCESSFUL"
            user.dna_total_status="SUCCESSFUL"
            user.gatk_status="SUCCESSFUL"
            user.total_status = "SUCCESSFUL"
            user.end_time = datetime.datetime.now()
            # times = datetime.datetime.now()
            # user.end_time  = times.strftime("%Y-%m-%d %H:%M:%S")       
            user.save(update_fields=['data_preparation_status','quality_check_status','gatk_status','somatic_status','germline_status','phasing_status','pvactools_status','mass_status','dna_total_status','total_status','end_time'])        
            successful_email(mail, uid, task, report="report-dna")
            return 0        
    except:
        uid = parameters['task_id']
        user = User_Job.objects.filter(user_id=uid)[0]
        mail = user.mail
        user.total_status="FAILED"
        user.error_log="Data_format"
        user.end_time = datetime.datetime.now()       
        user.save(update_fields=['error_log','total_status','end_time'])
        failed_email(mail, uid, task, report="report-dna")
        return -1
        

        
## mTSA with RNA-seq
def mTSA_1_data_preprocessing(T_r1_file_path, T_r2_file_path, N_r1_file_path, N_r2_file_path, genomeDir, illuminaclip, output_path, normal_sample_name, tumor_sample_name):
    try:
        cmd1 = f"mTSA_1_data_preprocessing.py -t1 {T_r1_file_path} -t2 {T_r2_file_path} -n1 {N_r1_file_path} -n2 {N_r2_file_path} --genomeDir {genomeDir} --illuminaclip {illuminaclip} -o {output_path} --sample_name_tumor {tumor_sample_name} --sample_name_normal {normal_sample_name}" 
        print(cmd1)
        p = sp.Popen(cmd1, stdout=sp.PIPE, stderr=sp.PIPE, shell=True)
        stdout, stderr = p.communicate()
        if p.returncode != 0:
            stderr = stderr.decode(encoding='utf-8')
            sys.stderr.write("Fail.\nError %d: %s\n" % (p.returncode, stderr))
            sys.exit(1)
        return 0
    except:
        return -1

def mTSA_2_gatk(T_alignment_bam, N_alignment_bam, ref, ref_vcf, output_path, normal_sample_name, tumor_sample_name, tmp):
    try:
        cmd2_T = f"mTSA_2_gatk.py -i {T_alignment_bam} -r {ref} -o {output_path} -n {tumor_sample_name} --create_index true -k {ref_vcf} -tmp {tmp}" 
        print(cmd2_T)
        p = sp.Popen(cmd2_T, stdout=sp.PIPE, stderr=sp.PIPE, shell=True)
        stdout, stderr = p.communicate()
        if p.returncode != 0:
            stderr = stderr.decode(encoding='utf-8')
            sys.stderr.write("Fail.\nError %d: %s\n" % (p.returncode, stderr))
            sys.exit(1)
        
        cmd2_N = f"mTSA_2_gatk.py -i {N_alignment_bam} -r {ref} -o {output_path} -n {normal_sample_name} --create_index true -k {ref_vcf} -tmp {tmp}" 
        print(cmd2_N)
        p = sp.Popen(cmd2_N, stdout=sp.PIPE, stderr=sp.PIPE, shell=True)
        stdout, stderr = p.communicate()
        if p.returncode != 0:
            stderr = stderr.decode(encoding='utf-8')
            sys.stderr.write("Fail.\nError %d: %s\n" % (p.returncode, stderr))
            sys.exit(1)
        return 0
    except:
        return -1

def mTSA_3_variant_calling(N_bam, T_bam, ref, output_path, dir_plugins, sequence_dictionary, dir_cache, min_coverage_tumor, min_coverage_normal, min_coverage, normal_sample_name, tumor_sample_name):
    try:
        cmd3 = f"mTSA_3_variant_calling.py -nb {N_bam} -tb {T_bam} -r {ref} --dir_plugins {dir_plugins} --sequence_dictionary {sequence_dictionary} --dir_cache {dir_cache} --min_coverage_tumor {min_coverage_tumor} --min_coverage_normal {min_coverage_normal} --min_coverage {min_coverage} -o {output_path} --sample_name_tumor {tumor_sample_name} --sample_name_normal {normal_sample_name}" 
        print(cmd3)
        p = sp.Popen(cmd3, stdout=sp.PIPE, stderr=sp.PIPE, shell=True)
        stdout, stderr = p.communicate()
        if p.returncode != 0:
            stderr = stderr.decode(encoding='utf-8')
            sys.stderr.write("Fail.\nError %d: %s\n" % (p.returncode, stderr))
            sys.exit(1)
        return 0
    except:
        return -1

def mTSA_4_run_kallisto(T_r1_file_path, T_r2_file_path, N_r1_file_path, N_r2_file_path, index, output_path, vep_txt, tumor_sample_name, header = 60):
    try:
        cmd4_1 = "export HDF5_DISABLE_VERSION_CHECK=2"
        cmd4_2 = "export HDF5_USE_FILE_LOCKING=FALSE"
        cmd4_3 = f"mTSA_4_run_kallisto.py -t1 {T_r1_file_path} -t2 {T_r2_file_path} -n1 {N_r1_file_path} -n2 {N_r2_file_path} --vep_txt {vep_txt} -i {index} -o {output_path} -n {tumor_sample_name} --header {header}" 
        print(cmd4_3)
        p = sp.Popen(cmd4_1, stdout=sp.PIPE, stderr=sp.PIPE, shell=True)
        p = sp.Popen(cmd4_2, stdout=sp.PIPE, stderr=sp.PIPE, shell=True)
        p = sp.Popen(cmd4_3, stdout=sp.PIPE, stderr=sp.PIPE, shell=True)
        stdout, stderr = p.communicate()
        if p.returncode != 0:
            stderr = stderr.decode(encoding='utf-8')
            sys.stderr.write("Fail.\nError %d: %s\n" % (p.returncode, stderr))
            sys.exit(1)
        return 0
    except:
        return -1
    
def mTSA_5_translation(tsv, output_path, tumor_sample_name):
    try:
        cmd5 = f"mTSA_5_translation.py -v {tsv} -o {output_path} -n {tumor_sample_name}" 
        print(cmd5)
        p = sp.Popen(cmd5, stdout=sp.PIPE, stderr=sp.PIPE, shell=True)
        stdout, stderr = p.communicate()
        if p.returncode != 0:
            stderr = stderr.decode(encoding='utf-8')
            sys.stderr.write("Fail.\nError %d: %s\n" % (p.returncode, stderr))
            sys.exit(1)
        return 0
    except:
        return -1
def mTSA_6_expression_level_filtering(peptide_tsv, output_path, tumor_expression_threshold, minimal_expression_ratio, tumor_sample_name):
    try:
        cmd6 = f"mTSA_6_expression_level_filtering.py -p {peptide_tsv} --tumor_expression_threshold {tumor_expression_threshold} --minimal_expression_ratio {minimal_expression_ratio} -o {output_path} -n {tumor_sample_name}" 
        print(cmd6)
        p = sp.Popen(cmd6, stdout=sp.PIPE, stderr=sp.PIPE, shell=True)
        stdout, stderr = p.communicate()
        if p.returncode != 0:
            stderr = stderr.decode(encoding='utf-8')
            sys.stderr.write("Fail.\nError %d: %s\n" % (p.returncode, stderr))
            sys.exit(1)
        return 0
    except:
        return -1
        
def mTSA_7_pvactools(fasta, tsv, hla_type, iedb_install_directory, cosmic_database, output_path, tumor_sample_name, max_strong=50, max_intermediate=250, max_weak=500):
    try:
        cmd7 = f"mTSA_7_pvactools.py -p {fasta} -t {tsv} -HLA {hla_type} --iedb_install_directory {iedb_install_directory} --cosmic_database {cosmic_database} -o {output_path} -n {tumor_sample_name} --max_strong {max_strong} --max_intermediate {max_intermediate} --max_weak {max_weak}" 
        print(cmd7)
        p = sp.Popen(cmd7, stdout=sp.PIPE, stderr=sp.PIPE, shell=True)
        stdout, stderr = p.communicate()
        if p.returncode != 0:
            stderr = stderr.decode(encoding='utf-8')
            sys.stderr.write("Fail.\nError %d: %s\n" % (p.returncode, stderr))
            sys.exit(1)
        return 0
    except:
        return -1

def mTSA_8_mass_merge(rna_fasta, mass_fasta, output_path, name, mass_name):
    try:
        cmd8 = f"mTSA_8_mass_merge.py -r {rna_fasta} -m {mass_fasta} -o {output_path} -n {name} -mn {mass_name}" 
        print(cmd8)
        p = sp.Popen(cmd8, stdout=sp.PIPE, stderr=sp.PIPE, shell=True)
        stdout, stderr = p.communicate()
        if p.returncode != 0:
            stderr = stderr.decode(encoding='utf-8')
            sys.stderr.write("Fail.\nError %d: %s\n" % (p.returncode, stderr))
            sys.exit(1)
        return 0
    except:
        return -1


def aeTSA_pipeline(t1, t2, n1, n2, nektar_assembly, illuminaclip, translation_py, mass_peptide_fasta, output_path, mass_sample_name, normal_sample_name, tumor_sample_name, kmer_len = 33, threads_kmer = 3, ash_size = '1G', minimal_kmer_depth = 5):
    try:
        # This step is to do data preprocessing 
        output_path_aeTSA = output_path + '/aeTSA_RNAseq/'
        TPR1 = f"{output_path}/mTSA_RNAseq/1-fastq/trimmed/T_R1.trimmed.paired.fastq.gz"
        TPR2 = f"{output_path}/mTSA_RNAseq/1-fastq/trimmed/T_R2.trimmed.paired.fastq.gz"
        TUR1 = f"{output_path}/mTSA_RNAseq/1-fastq/trimmed/T_R1.trimmed.unpaired.fastq.gz"
        TUR2 = f"{output_path}/mTSA_RNAseq/1-fastq/trimmed/T_R2.trimmed.unpaired.fastq.gz"
        NPR1 = f"{output_path}/mTSA_RNAseq/1-fastq/trimmed/N_R1.trimmed.paired.fastq.gz"
        NPR2 = f"{output_path}/mTSA_RNAseq/1-fastq/trimmed/N_R2.trimmed.paired.fastq.gz"
        NUR1 = f"{output_path}/mTSA_RNAseq/1-fastq/trimmed/N_R1.trimmed.unpaired.fastq.gz"
        NUR2 = f"{output_path}/mTSA_RNAseq/1-fastq/trimmed/N_R2.trimmed.unpaired.fastq.gz"
        if (_is_path_exist(TPR1)!=0) or (_is_path_exist(TPR2)!=0) or (_is_path_exist(TUR1)!=0) or (_is_path_exist(TUR2)!=0) or (_is_path_exist(NPR1)!=0) or (_is_path_exist(NPR2)!=0) or (_is_path_exist(NUR1)!=0) or (_is_path_exist(NUR2)!=0):
            cmd9 = f"aeTSA_1_data_preprocessing_small.py -t1 {t1} -t2 {t2} -n1 {n1} -n2 {n2} -o {output_path_aeTSA} --sample_name_tumor {tumor_sample_name} --sample_name_normal {normal_sample_name} --illuminaclip {illuminaclip}" 
            print(cmd9)
            p = sp.Popen(cmd9, stdout=sp.PIPE, stderr=sp.PIPE, shell=True)
            stdout, stderr = p.communicate()
            if p.returncode != 0:
                stderr = stderr.decode(encoding='utf-8')
                sys.stderr.write("Fail.\nError %d: %s\n" % (p.returncode, stderr))
                sys.exit(1)
        else:
            Makedir(f"{output_path}/aeTSA_RNAseq/1-fastq/trimmed/")
            Move(f"{output_path}/mTSA_RNAseq/1-fastq/trimmed/", f"{output_path}/aeTSA_RNAseq/1-fastq/")
        
        TPR1 = f"{output_path}/aeTSA_RNAseq/1-fastq/trimmed/T_R1.trimmed.paired.fastq.gz"
        TPR2 = f"{output_path}/aeTSA_RNAseq/1-fastq/trimmed/T_R2.trimmed.paired.fastq.gz"
        TUR1 = f"{output_path}/aeTSA_RNAseq/1-fastq/trimmed/T_R1.trimmed.unpaired.fastq.gz"
        TUR2 = f"{output_path}/aeTSA_RNAseq/1-fastq/trimmed/T_R2.trimmed.unpaired.fastq.gz"
        NPR1 = f"{output_path}/aeTSA_RNAseq/1-fastq/trimmed/N_R1.trimmed.paired.fastq.gz"
        NPR2 = f"{output_path}/aeTSA_RNAseq/1-fastq/trimmed/N_R2.trimmed.paired.fastq.gz"
        NUR1 = f"{output_path}/aeTSA_RNAseq/1-fastq/trimmed/N_R1.trimmed.unpaired.fastq.gz"
        NUR2 = f"{output_path}/aeTSA_RNAseq/1-fastq/trimmed/N_R2.trimmed.unpaired.fastq.gz"
        
        # This step is to generate k-mer 
        cmd9_1 = f"aeTSA_2_kmer_generation.py -PR1 {TPR1} -PR2 {TPR2} -UR1 {TUR1} -UR2 {TUR2} -o {output_path_aeTSA} -n {tumor_sample_name} -s {ash_size} -m {kmer_len} -t {threads_kmer}" 
        print(cmd9_1)
        p = sp.Popen(cmd9_1, stdout=sp.PIPE, stderr=sp.PIPE, shell=True)
        stdout, stderr = p.communicate()
        if p.returncode != 0:
            stderr = stderr.decode(encoding='utf-8')
            sys.stderr.write("Fail.\nError %d: %s\n" % (p.returncode, stderr))
            sys.exit(1)
        
        cmd9_2 = f"aeTSA_2_kmer_generation.py -PR1 {NPR1} -PR2 {NPR2} -UR1 {NUR1} -UR2 {NUR2} -o {output_path_aeTSA} -n {normal_sample_name} -s {ash_size} -m {kmer_len} -t {threads_kmer}" 
        print(cmd9_2)
        p = sp.Popen(cmd9_2, stdout=sp.PIPE, stderr=sp.PIPE, shell=True)
        stdout, stderr = p.communicate()
        if p.returncode != 0:
            stderr = stderr.decode(encoding='utf-8')
            sys.stderr.write("Fail.\nError %d: %s\n" % (p.returncode, stderr))
            sys.exit(1)
        
        # This step is to filter k-mer
        tumor_jf_file = output_path_aeTSA + f'/2-jf-database/kmer_generation/{tumor_sample_name}_trim_{kmer_len}.jf'
        normal_jf_file = output_path_aeTSA + f'/2-jf-database/kmer_generation/{normal_sample_name}_trim_{kmer_len}.jf'
        cmd10 = f"aeTSA_3_kmer_filtering.py --tumor_jf_file {tumor_jf_file} --normal_jf_file {normal_jf_file} -o {output_path_aeTSA} -tn {tumor_sample_name} -nn {normal_sample_name} -mm {minimal_kmer_depth} -m {kmer_len}" 
        print(cmd10)
        p = sp.Popen(cmd10, stdout=sp.PIPE, stderr=sp.PIPE, shell=True)
        stdout, stderr = p.communicate()
        if p.returncode != 0:
            stderr = stderr.decode(encoding='utf-8')
            sys.stderr.write("Fail.\nError %d: %s\n" % (p.returncode, stderr))
            sys.exit(1)
        
        # This step is to assemble k-mer
        normal_count_file = output_path_aeTSA + f'/2-jf-database/kmer_filtering_{kmer_len}/4_filtering_k-mers/{tumor_sample_name}.{minimal_kmer_depth}.{normal_sample_name}.0.count'
        cmd11 = f"aeTSA_4_kmer_assembly.py --tumor_jf_file {tumor_jf_file} --normal_count_file {normal_count_file} --nektar_assembly {nektar_assembly} -o {output_path_aeTSA} -tn {tumor_sample_name} -nn {normal_sample_name} -m {kmer_len}" 
        print(cmd11)
        p = sp.Popen(cmd11, stdout=sp.PIPE, stderr=sp.PIPE, shell=True)
        stdout, stderr = p.communicate()
        if p.returncode != 0:
            stderr = stderr.decode(encoding='utf-8')
            sys.stderr.write("Fail.\nError %d: %s\n" % (p.returncode, stderr))
            sys.exit(1)
        
        # This step is to translate k-mer
        assembly_fasta = output_path_aeTSA + f'/2-jf-database/kmer_assembly_k{kmer_len}/assembly_{tumor_sample_name}_result/assembly.fasta'
        assembly_tab = output_path_aeTSA + f'/2-jf-database/kmer_assembly_k{kmer_len}/assembly_{tumor_sample_name}_result/assembly.tab'
        cmd12 = f"aeTSA_5_three_frame_translation.py --assembly_fasta {assembly_fasta} --assembly_tab {assembly_tab} --translation_py {translation_py} -o {output_path_aeTSA} -tn {tumor_sample_name} -nn {normal_sample_name} -m {kmer_len}" 
        print(cmd12)
        p = sp.Popen(cmd12, stdout=sp.PIPE, stderr=sp.PIPE, shell=True)
        stdout, stderr = p.communicate()
        if p.returncode != 0:
            stderr = stderr.decode(encoding='utf-8')
            sys.stderr.write("Fail.\nError %d: %s\n" % (p.returncode, stderr))
            sys.exit(1)

        # Merge with LC-MS/MS peptides      
        RNA_peptide_fasta =  output_path_aeTSA + f'/2-jf-database/translation_k{kmer_len}/{tumor_sample_name}_3-frame.fasta'
        cmd13 = f"aeTSA_6_mass_merge.py -r {RNA_peptide_fasta} -m {mass_peptide_fasta} -o {output_path_aeTSA} -n {tumor_sample_name} -mn {mass_sample_name}" 
        print(cmd13)
        p = sp.Popen(cmd13, stdout=sp.PIPE, stderr=sp.PIPE, shell=True)
        stdout, stderr = p.communicate()
        if p.returncode != 0:
            stderr = stderr.decode(encoding='utf-8')
            sys.stderr.write("Fail.\nError %d: %s\n" % (p.returncode, stderr))
            sys.exit(1)
        return 0
    except:
        return -1

def aeTSA_7_pvactools(tsv, hla_type, iedb_install_directory, cosmic_database, output_path, tumor_sample_name, max_strong, max_intermediate, max_weak):
    try:
        output_path_aeTSA = output_path + '/aeTSA_RNAseq'
        cmd14 = f"aeTSA_7_pvactools.py -i {tsv} -HLA {hla_type} --iedb_install_directory {iedb_install_directory} --cosmic_database {cosmic_database} -o {output_path_aeTSA} -n {tumor_sample_name} --max_strong {max_strong} --max_intermediate {max_intermediate} --max_weak {max_weak}" 
        print(cmd14)
        p = sp.Popen(cmd14, stdout=sp.PIPE, stderr=sp.PIPE, shell=True)
        stdout, stderr = p.communicate()
        if p.returncode != 0:
            stderr = stderr.decode(encoding='utf-8')
            sys.stderr.write("Fail.\nError %d: %s\n" % (p.returncode, stderr))
            sys.exit(1)
        return 0
    except:
        return -1

def aeTSA_8_tsa_annotation(T_bam, N_bam, genomeDir, peptide, output_path, normal_sample_name, tumor_sample_name, thread, samtools, tmp):
    try:
        output_path_aeTSA = output_path + '/aeTSA_RNAseq'
        cmd15 = f"aeTSA_8_tsa_annotation.py -bt {T_bam} -bn {N_bam} --genomeDir {genomeDir} -p {peptide} -o {output_path_aeTSA} --sample_name_tumor {tumor_sample_name} --sample_name_normal {normal_sample_name} -t {thread} --samtools_bin {samtools} -tmp {tmp}" 
        print(cmd15)
        p = sp.Popen(cmd15, stdout=sp.PIPE, stderr=sp.PIPE, shell=True)
        stdout, stderr = p.communicate()
        if p.returncode != 0:
            stderr = stderr.decode(encoding='utf-8')
            sys.stderr.write("Fail.\nError %d: %s\n" % (p.returncode, stderr))
            sys.exit(1)
        return 0
    except:
        return -1

def mTSA_aeTSA_pie_chart(mTSA, output_path, name, aeTSA = False):
    try:
        cmd16 = f"mTSA_aeTSA_pie_chart.py -mTSA {mTSA} -aeTSA {aeTSA} -o {output_path} -n {name}" 
        print(cmd16)
        p = sp.Popen(cmd16, stdout=sp.PIPE, stderr=sp.PIPE, shell=True)
        stdout, stderr = p.communicate()
        if p.returncode != 0:
            stderr = stderr.decode(encoding='utf-8')
            sys.stderr.write("Fail.\nError %d: %s\n" % (p.returncode, stderr))
            sys.exit(1)
        return 0
    except:
        return -1

def mTSA_aeTSA_merge(mTSA, aeTSA, output_path, sample_name, aeTSA_status=True):
    try:
        if aeTSA_status == True:
            mTSA_df = pd.read_csv(mTSA, sep='\t') 
            aeTSA_df = pd.read_csv(aeTSA, sep='\t') 
            merged_file = pd.concat([mTSA_df,aeTSA_df])
            directory_path=f"{output_path}/total_TSA/"
            if not os.path.exists(directory_path): # Create the directory
                os.makedirs(directory_path)
            merged_file.to_csv(f'{output_path}/total_TSA/{sample_name}_mTSA_and_aeTSA.tsv', sep='\t', index = False)
            print("mTSA_aeTSA_merge is successful!")
        else:
            mTSA_df = pd.read_csv(mTSA, sep='\t')
            mTSA_df.to_csv(f'{output_path}/total_TSA/{sample_name}_mTSA_and_aeTSA.tsv', sep='\t', index = False)
            print("mTSA_aeTSA_merge is successful!")
        return 0
    except:
        print("mTSA_aeTSA_merge is fail!")
        return -1


def TSA_RNAseq(data_path, parameters):
    print("Run TSA_RNAseq")
    uid = parameters['task_id']
    user = User_Job.objects.filter(user_id=uid)[0]
    user.total_status = "RUNNING"
    user.start_time = datetime.datetime.now()
    user.save(update_fields=['total_status', 'start_time'])
    # Step1. Set parameters
    N_r1_file = parameters['N_r1_file']
    N_r2_file = parameters['N_r2_file']
    T_r1_file = parameters['T_r1_file']
    T_r2_file = parameters['T_r2_file']
    dict_urls = parameters['dict_urls']
    thread = parameters['thread']
    ip = 15
    database_path = parameters['database_path']
    home_path = parameters['home_path']
    output_path = parameters['output_path']
    normal_sample_name = parameters['normal_sample_name']
    tumor_sample_name = parameters['tumor_sample_name']
    min_coverage_tumor = parameters['min_coverage_tumor']
    min_coverage_normal = parameters['min_coverage_normal']
    min_coverage = parameters['min_coverage']
    tumor_expression_threshold = parameters["tumor_expression_threshold"]
    minimal_expression_ratio = parameters["minimal_expression_ratio"]
    if str(minimal_expression_ratio) == "0.0" or "0":
            minimal_expression_ratio = None
    hla_type_ls = parameters['hla_type_ls']
    hla_typing_step = parameters['hla_typing_step']
    max_strong = parameters['max_ic_strong'] 
    max_intermediate = parameters['max_ic_inter'] 
    max_weak =parameters['max_ic_weak'] 
    hla_type = ','.join(hla_type_ls)
    mass_file_path = parameters['mass_file_path'] 
    mass_step = parameters['mass_step']
    mass_sample_name = "mass.peptide"  
    N_r1_file_path = data_path + '/' + N_r1_file
    N_r2_file_path = data_path + '/' + N_r2_file
    T_r1_file_path = data_path + '/' + T_r1_file
    T_r2_file_path = data_path + '/' + T_r2_file
    mail = user.mail
    task = "Neoantigen Identification"
    ## set parameters
    genomeDir = database_path + "/STAR_idx/"
    illuminaclip = database_path + "/adapters/TruSeq3-PE-2.fa:2:30:10:8:true"
    ref = f"{database_path}/hg38/Homo_sapiens_assembly38.fasta"
    ref_vcf = f"{database_path}/hg38/Homo_sapiens_assembly38.dbsnp138.vcf {database_path}/hg38/1000G_omni2.5.hg38.vcf {database_path}/hg38/Mills_and_1000G_gold_standard.indels.hg38.vcf"
    dir_plugins = database_path + "/iedb/VEP_plugins" 
    dir_cache = database_path + "/GRCh38.104_vep"
    sequence_dictionary = database_path + "/hg38/Homo_sapiens_assembly38.dict"
    index = database_path + "/hg38/Homo_sapiens.GRCh38.cdna.all.fa.index"
    iedb_install_directory = database_path + '/iedb'
    cosmic_database = database_path + '/cosmic/Census_allMon.csv'
    iedb_fasta_database = database_path + '/iedb_fasta/IEDB_MHC.fasta'
    nektar_assembly = database_path + '/nektar/kmer_assembly'
    translation_py = database_path + '/../scripts/aeTSA_translation.py'
    samtools = home_path + '/samtools' 
    tmp = parameters['tmp_path']
    print(dict_urls)
    try:
        # check if the file exists
        hla_tsv = output_path + f"{output_path}/{tumor_sample_name}_mTSA_and_aeTSA.tsv" 
        if _is_path_exist(hla_tsv)!=0: 
            # download data
            if bool(dict_urls != {})== True:
                print("Download data from URLs.")
                user.data_preparation_status="RUNNING"
                user.save(update_fields=['data_preparation_status'])
                data_tmp_path = str(Path(UPLOAD_BASE_PATH).resolve().joinpath(uid))
                data_preparation_stat = run_data_preparation(data_tmp_path, data_path, dict_urls)
                if(data_preparation_stat!=0):
                    print("pipeline stop at data preparation")
                    user.error_log="INPUT DATA"
                    user.data_preparation_status="FAILED"
                    user.quality_check="FAILED"
                    user.total_status="FAILED"
                    user.end_time=datetime.datetime.now()
                    user.save(update_fields=['error_log','data_preparation_status','total_status','end_time'])
                    failed_email(mail, uid, task, report="report-rna")
                    return -1
                else:
                    user.data_preparation_status="SUCCESSFUL"
                    user.save(update_fields=['data_preparation_status'])
            else:
                user.data_preparation_status="SUCCESSFUL"
                user.save(update_fields=['data_preparation_status']) 

            # Step2-1. Run quality check
            user.quality_check_status="RUNNING"
            user.save(update_fields=['quality_check_status'])
            print("Run QC")
            run_QC = mTSA_1_data_preprocessing(T_r1_file_path, T_r2_file_path, N_r1_file_path, N_r2_file_path, genomeDir, illuminaclip, output_path, normal_sample_name, tumor_sample_name)
            if(run_QC!=0):
                print("pipeline stop at QC")    
                user.error_log="QC"
                user.quality_check_status="FAILED"
                user.rna_total_status="FAILED"
                user.total_status="FAILED"
                user.end_time=datetime.datetime.now()
                user.save(update_fields=['error_log','quality_check_status','rna_total_status','total_status','end_time'])
                failed_email(mail, uid, task, report="report-rna")
            else:
                user.quality_check_status="SUCCESSFUL"
                user.save(update_fields=['quality_check_status'])

            # Step2-2. Run GATK4
            user.gatk_status="RUNNING"
            user.save(update_fields=['gatk_status'])
            T_alignment_bam = f"{output_path}/mTSA_RNAseq/1-fastq/aligment/{tumor_sample_name}_Aligned.sortedByCoord.out.bam"  
            N_alignment_bam = f"{output_path}/mTSA_RNAseq/1-fastq/aligment/{normal_sample_name}_Aligned.sortedByCoord.out.bam"  
            run_gatk4 = mTSA_2_gatk(T_alignment_bam, N_alignment_bam, ref, ref_vcf, output_path, normal_sample_name, tumor_sample_name, tmp)
            if(run_gatk4!=0):
                print("pipeline stop at gatk4")
                user.error_log="Data preprocessing"
                user.gatk_status="FAILED"
                user.rna_total_status="FAILED"
                user.total_status="FAILED"
                user.end_time=datetime.datetime.now()
                user.save(update_fields=['error_log','gatk_status','rna_total_status','total_status','end_time'])
                failed_email(mail, uid, task)
            else:
                user.gatk_status="SUCCESSFUL"
                user.save(update_fields=['gatk_status'])

            # Step2-3. Run Somatic mutation
            user.somatic_status="RUNNING"
            user.save(update_fields=['somatic_status'])
            T_bam = f"{output_path}/mTSA_RNAseq/2-gatk/{tumor_sample_name}/{tumor_sample_name}_recal.bam"
            N_bam = f"{output_path}/mTSA_RNAseq/2-gatk/{normal_sample_name}/{normal_sample_name}_recal.bam"
            run_somatic = mTSA_3_variant_calling(N_bam, T_bam, ref, output_path, dir_plugins, sequence_dictionary, dir_cache, min_coverage_tumor, min_coverage_normal, min_coverage, normal_sample_name, tumor_sample_name)
            if(run_somatic!=0):
                print("pipeline stop at somatic mutation calling")
                user.error_log="Somatic mutation calling"
                user.somatic_status="FAILED"
                user.rna_total_status="FAILED"
                user.total_status="FAILED"
                user.end_time=datetime.datetime.now()
                user.save(update_fields=['error_log','somatic_status','rna_total_status','total_status','end_time'])
                failed_email(mail, uid, task, report="report-rna")
            else:
                user.somatic_status="SUCCESSFUL"
                user.save(update_fields=['somatic_status'])
            
            # Step2-4. Run kallisto
            user.expression_level_status="RUNNING"
            user.save(update_fields=['expression_level_status'])
            vep_txt = f"{output_path}/mTSA_RNAseq/3-variant/{tumor_sample_name}/{tumor_sample_name}_somatic_VEP_annotation_sorted.txt"
            run_kallisto = mTSA_4_run_kallisto(T_r1_file_path, T_r2_file_path, N_r1_file_path, N_r2_file_path, index, output_path, vep_txt, tumor_sample_name, header = 60)
            if(run_kallisto!=0):
                print("pipeline stop at RNA expression level calculation")
                user.error_log="RNA expression level calculation"
                user.expression_level_status="FAILED"
                user.rna_total_status="FAILED"
                user.total_status="FAILED"
                user.end_time=datetime.datetime.now()
                user.save(update_fields=['error_log','expression_level_status','rna_total_status','total_status','end_time'])
                failed_email(mail, uid, task, report="report-rna")
            
            tsv = f"{output_path}/mTSA_RNAseq/4-quantification/{tumor_sample_name}/{tumor_sample_name}_RNA_expression_level.tsv"
            run_transloation = mTSA_5_translation(tsv, output_path, tumor_sample_name)
            if(run_transloation!=0):
                print("pipeline stop at peptide translation")
                user.error_log="Peptide translation"
                user.expression_level_status="FAILED"
                user.rna_total_status="FAILED"
                user.total_status="FAILED"
                user.end_time=datetime.datetime.now()
                user.save(update_fields=['error_log','expression_level_status','rna_total_status','total_status','end_time'])
                failed_email(mail, uid, task, report="report-rna")

            else:
                user.expression_level_status="SUCCESSFUL"
                user.save(update_fields=['expression_level_status'])

            # Step2-5. Run TPM filtering
            user.filtering_status="RUNNING"
            user.save(update_fields=['filtering_status'])
            peptide_tsv = f"{output_path}/mTSA_RNAseq/5-translation/{tumor_sample_name}_peptide_translation.tsv"
            run_filtering = mTSA_6_expression_level_filtering(peptide_tsv, output_path, tumor_expression_threshold, minimal_expression_ratio, tumor_sample_name)
            if(run_filtering!=0):
                print("pipeline stop at expression level filtering")
                user.error_log="Phasing"
                user.filtering_status="FAILED"
                user.rna_total_status="FAILED"
                user.total_status="FAILED"
                user.end_time=datetime.datetime.now()
                user.save(update_fields=['error_log','filtering_status','rna_total_status','total_status','end_time'])
                failed_email(mail, uid, task, report="report-rna")
            else:
                user.filtering_status="SUCCESSFUL"
                user.save(update_fields=['filtering_status'])
            
            # Step 2-6 HLA genotyping
            if hla_typing_step == True:
                user.hla_status="RUNNING"
                user.save(update_fields=['hla_status'])
                r1_trimmed_file_path = f"{output_path}/mTSA_RNAseq/1-fastq/trimmed/{normal_sample_name}_R1.trimmed.paired.fastq.gz"
                r2_trimmed_file_path = f"{output_path}/mTSA_RNAseq/1-fastq/trimmed/{normal_sample_name}_R2.trimmed.paired.fastq.gz"
                run_optitype = HLA_typing_2_genotyping(r1_trimmed_file_path, r2_trimmed_file_path, database_path, output_path, normal_sample_name, "-RNA")
                if(run_optitype!=0):
                    user.error_log="HLA_typing"
                    user.hla_status="FAILED"
                    user.total_status="FAILED"
                    user.end_time=datetime.datetime.now()
                    user.save(update_fields=['error_log','hla_status','total_status','end_time'])
                    failed_email(mail, uid, task, report="report-rna")
                else:
                    hla_tsv = output_path + f"/HLA_typing/{normal_sample_name}/2-hla-typing/{normal_sample_name}_result.tsv"
                    optitype_tsv = pd.read_csv(hla_tsv, sep="\t")
                    optitype_A1 = optitype_tsv["A1"]
                    optitype_A2 = optitype_tsv["A2"]
                    optitype_B1 = optitype_tsv["B1"]
                    optitype_B2 = optitype_tsv["B2"]
                    optitype_C1 = optitype_tsv["C1"]
                    optitype_C2 = optitype_tsv["C2"]
                    hla_type_ls = [f"HLA-{optitype_A1[0]}",f"HLA-{optitype_A2[0]}",f"HLA-{optitype_B1[0]}",f"HLA-{optitype_B2[0]}",f"HLA-{optitype_C1[0]}",f"HLA-{optitype_C2[0]}"]
                    hla_type = f"HLA-{optitype_A1[0]},HLA-{optitype_A2[0]},HLA-{optitype_B1[0]},HLA-{optitype_B2[0]},HLA-{optitype_C1[0]},HLA-{optitype_C2[0]}"
                    print(hla_type)
                    user.hla_status="SUCCESSFUL"
                    user.save(update_fields=['hla_status'])
            else:
                print("HLA genotyping step has been skipped.")
                user.hla_status="SKIPPED"
                user.end_time=datetime.datetime.now()
                user.save(update_fields=['hla_status'])

            # Step2-7-0. Run aeTSA pipeline
            if mass_step != True: 
                try:
                    IEDB_list = []
                    for hla in hla_type_ls:
                        if _is_path_exist(f"{iedb_install_directory}/MHC_fasta/IEDB_MHC_{hla}.fasta") == 0: 
                            IEDB_list.append(f"{iedb_install_directory}/MHC_fasta/IEDB_MHC_{hla}.fasta")
                    input_fasta = ' '.join(IEDB_list)
                    mass_file_path = f"{output_path}/rna.mass.fasta"
                    Cat(input_fasta, mass_file_path)
                except:
                    mass_file_path = iedb_fasta_database
            user.aeTSA_status="RUNNING"
            user.save(update_fields=['aeTSA_status'])
            run_asTSA = aeTSA_pipeline(T_r1_file_path, T_r2_file_path, N_r1_file_path, N_r2_file_path, nektar_assembly, illuminaclip, translation_py, mass_file_path, output_path, mass_sample_name, normal_sample_name, tumor_sample_name, kmer_len = 33, threads_kmer = 3, ash_size = '1G', minimal_kmer_depth = 5)
            if(run_asTSA!=0):
                print("aeTSA generation step has errors.")
                user.error_log="aeTSA generation"
                user.aeTSA_status="FAILED"
                user.end_time=datetime.datetime.now()
                user.save(update_fields=['error_log','aeTSA_status'])
            else:
                user.aeTSA_status="SUCCESSFUL"
                user.save(update_fields=['aeTSA_status'])

            # Step 2-7-1 Run Pvactools
            user.pvactools_status="RUNNING"
            user.save(update_fields=['pvactools_status'])
            filtered_fasta = f"{output_path}/mTSA_RNAseq/5-translation/{tumor_sample_name}_expression_level_filtered_short.fasta"
            filtered_tsv = f"{output_path}/mTSA_RNAseq/5-translation/{tumor_sample_name}_expression_level_filtered.tsv"

            # mTSA
            run_pvactools = mTSA_7_pvactools(filtered_fasta, filtered_tsv, hla_type, iedb_install_directory, cosmic_database, output_path, tumor_sample_name, max_strong, max_intermediate, max_weak)
            if(run_pvactools!=0):
                print("pipeline stop at Pvactools")
                user.error_log="Pvactools"
                user.pvactools_status="FAILED"
                user.rna_total_status="FAILED"
                user.total_status="FAILED"
                user.end_time=datetime.datetime.now()
                user.save(update_fields=['error_log','pvactools_status','rna_total_status','total_status','end_time'])
                failed_email(mail, uid, task, report="report-rna")          
            
            # aeTSA
            if (user.aeTSA_status == "SUCCESSFUL") and (user.pvactools_status == "RUNNING"): 
                tsv = f"{output_path}/aeTSA_RNAseq/3-blastp/{tumor_sample_name}_{mass_sample_name}_full_length.tsv"
                run_pvactools = aeTSA_7_pvactools(tsv, hla_type, iedb_install_directory, cosmic_database, output_path, tumor_sample_name, max_strong, max_intermediate, max_weak)
                if(run_pvactools!=0):
                    print("pipeline stop at Pvactools")
                    user.error_log="Pvactools"
                    user.pvactools_status="FAILED"
                    user.end_time=datetime.datetime.now()
                    user.save(update_fields=['error_log','pvactools_status', 'end_time'])
                    failed_email(mail, uid, task, report="report-rna")
                else:
                    user.pvactools_status="SUCCESSFUL"
                    user.save(update_fields=['pvactools_status']) 

            # Step2-8. Run MASS
            if mass_step != True:
                IEDB_list = []
                for hla in hla_type_ls:
                    if _is_path_exist(f"{iedb_install_directory}/MHC_fasta/IEDB_MHC_{hla}.fasta") == 0: 
                        IEDB_list.append(f"{iedb_install_directory}/MHC_fasta/IEDB_MHC_{hla}.fasta")
                input_fasta = ' '.join(IEDB_list)
                print(input_fasta)
                mass_file_path = f"{output_path}/rna.mass.fasta"
                Cat(input_fasta, mass_file_path) 
            user.mass_status="RUNNING"
            user.save(update_fields=['mass_status'])
            rna_fasta = f"{output_path}/mTSA_RNAseq/5-translation/{tumor_sample_name}_expression_level_filtered.fasta"
            rna_name = "rna.peptide"
            run_mass = mTSA_8_mass_merge(rna_fasta, mass_file_path, output_path, rna_name, mass_sample_name)
            if(run_mass!=0):
                print("MASS merging step has errors.")
                user.error_log="MASS"
                user.mass_status="FAILED"
                user.end_time=datetime.datetime.now()
                user.save(update_fields=['error_log','mass_status'])
            else:
                user.mass_status="SUCCESSFUL"
                user.save(update_fields=['mass_status'])
            
            # Step2-9. Run aeTSA annotation
            if user.aeTSA_status == "SUCCESSFUL": 
                user.aeTSA_annotation_status="RUNNING"
                user.save(update_fields=['aeTSA_annotation_status'])
                peptide = f"{output_path}/aeTSA_RNAseq/4-hla-binding-affinity/{tumor_sample_name}/2_runing_pvacbind/{tumor_sample_name}_TSA_candidates.tsv"
                run_aeTSA_annotation = aeTSA_8_tsa_annotation(T_bam, N_bam, genomeDir, peptide, output_path, normal_sample_name, tumor_sample_name, thread, samtools, tmp)
                if(run_aeTSA_annotation!=0):
                    print("aeTSA annotation step has errors.")
                    user.error_log="aeTSA annotation"
                    user.aeTSA_annotation_status="FAILED"
                    user.end_time=datetime.datetime.now()
                    user.save(update_fields=['error_log','aeTSA_annotation_status'])
                else:
                    user.aeTSA_annotation_status="SUCCESSFUL"
                    user.save(update_fields=['aeTSA_annotation_status'])
            else:
                print("aeTSA annotation step has been skipped.")
                user.aeTSA_annotation_status="SKIPPED"
                user.end_time=datetime.datetime.now()
                user.save(update_fields=['aeTSA_annotation_status'])

            # Step2-10. Results confirmation
            mTSA = f"{output_path}/mTSA_RNAseq/6-hla-binding-affinity/{tumor_sample_name}/{tumor_sample_name}_TSA_candidates.tsv"
            name_plot = "T.plot"
            if user.aeTSA_annotation_status == "SUCCESSFUL": 
                aeTSA = f"{output_path}/aeTSA_RNAseq/4-hla-binding-affinity/{tumor_sample_name}/2_runing_pvacbind/{tumor_sample_name}_TSA_candidates.tsv"
                run_plot = mTSA_aeTSA_pie_chart(mTSA, output_path, name_plot, aeTSA)
                mTSA_aeTSA_merge(mTSA, aeTSA, output_path, tumor_sample_name, aeTSA_status=True)
            else:
                mTSA_aeTSA_merge(mTSA, aeTSA, output_path, tumor_sample_name, aeTSA_status=False)
                run_plot = mTSA_aeTSA_pie_chart(mTSA, output_path, name_plot, aeTSA = False)
            if _is_path_exist(run_plot)!=0:
                user.error_log="result generation"
                user.rna_total_status="FAILED"
                user.total_status="FAILED"
                user.end_time=datetime.datetime.now()
                user.save(update_fields=['error_log','rna_total_status','total_status','end_time'])
                failed_email(mail, uid, tas, report="report-rna")
            else:
                user.rna_total_status="SUCCESSFUL"
                user.total_status = "SUCCESSFUL"
                user.end_time = datetime.datetime.now()
                user.save(update_fields=['quality_check_status','gatk_status','somatic_status','expression_level_status','filtering_status','aeTSA_status','pvactools_status','aeTSA_annotation_status','mass_status','rna_total_status','total_status','end_time'])
                successful_email(mail, uid, task, report="report-rna")
        else:
            user.quality_check_status="SUCCESSFUL"
            user.rna_total_status="SUCCESSFUL"
            user.gatk_status="SUCCESSFUL"
            user.total_status = "SUCCESSFUL"
            user.end_time = datetime.datetime.now()
            # times = datetime.datetime.now()
            # user.end_time  = times.strftime("%Y-%m-%d %H:%M:%S")       
            user.save(update_fields=['quality_check_status','gatk_status','somatic_status','expression_level_status','filtering_status','aeTSA_status','pvactools_status','aeTSA_annotation_status','mass_status','rna_total_status','total_status','end_time'])        
            successful_email(mail, uid, task, report="report-rna")
            return 0        
    except:
        uid = parameters['task_id']
        user = User_Job.objects.filter(user_id=uid)[0]
        user.rna_total_status="FAILED"
        user.total_status="FAILED"
        user.error_log="Data_format"
        user.end_time = datetime.datetime.now()       
        user.save(update_fields=['error_log','rna_total_status','total_status','end_time'])
        mail = user.mail
        failed_email(mail, uid, task, report="report-rna")
        return -1

# DNA + RNA-seq

def aeTSA_with_dna_pipeline(t1, t2, n1, n2, nektar_assembly, illuminaclip, translation_py, mass_peptide_fasta, output_path, mass_sample_name, normal_sample_name, tumor_sample_name, kmer_len = 33, threads_kmer = 3, ash_size = '1G', minimal_kmer_depth = 5):
    try:
        # This step is to do data preprocessing 
        output_path_aeTSA = output_path + '/aeTSA_RNAseq/'
        cmd9 = f"aeTSA_1_data_preprocessing.py -t1 {t1} -t2 {t2} -n1 {n1} -n2 {n2} -o {output_path_aeTSA} --sample_name_tumor {tumor_sample_name} --sample_name_normal {normal_sample_name} --illuminaclip {illuminaclip}" 
        print(cmd9)
        p = sp.Popen(cmd9, stdout=sp.PIPE, stderr=sp.PIPE, shell=True)
        stdout, stderr = p.communicate()
        if p.returncode != 0:
            stderr = stderr.decode(encoding='utf-8')
            sys.stderr.write("Fail.\nError %d: %s\n" % (p.returncode, stderr))
            sys.exit(1)

        TPR1 = f"{output_path}/aeTSA_RNAseq/1-fastq/trimmed/T_R1.trimmed.paired.fastq.gz"
        TPR2 = f"{output_path}/aeTSA_RNAseq/1-fastq/trimmed/T_R2.trimmed.paired.fastq.gz"
        TUR1 = f"{output_path}/aeTSA_RNAseq/1-fastq/trimmed/T_R1.trimmed.unpaired.fastq.gz"
        TUR2 = f"{output_path}/aeTSA_RNAseq/1-fastq/trimmed/T_R2.trimmed.unpaired.fastq.gz"
        NPR1 = f"{output_path}/aeTSA_RNAseq/1-fastq/trimmed/N_R1.trimmed.paired.fastq.gz"
        NPR2 = f"{output_path}/aeTSA_RNAseq/1-fastq/trimmed/N_R2.trimmed.paired.fastq.gz"
        NUR1 = f"{output_path}/aeTSA_RNAseq/1-fastq/trimmed/N_R1.trimmed.unpaired.fastq.gz"
        NUR2 = f"{output_path}/aeTSA_RNAseq/1-fastq/trimmed/N_R2.trimmed.unpaired.fastq.gz"
        
        # This step is to generate k-mer 
        cmd9_1 = f"aeTSA_2_kmer_generation.py -PR1 {TPR1} -PR2 {TPR2} -UR1 {TUR1} -UR2 {TUR2} -o {output_path_aeTSA} -n {tumor_sample_name} -s {ash_size} -m {kmer_len} -t {threads_kmer}" 
        print(cmd9_1)
        p = sp.Popen(cmd9_1, stdout=sp.PIPE, stderr=sp.PIPE, shell=True)
        stdout, stderr = p.communicate()
        if p.returncode != 0:
            stderr = stderr.decode(encoding='utf-8')
            sys.stderr.write("Fail.\nError %d: %s\n" % (p.returncode, stderr))
            sys.exit(1)
        
        cmd9_2 = f"aeTSA_2_kmer_generation.py -PR1 {NPR1} -PR2 {NPR2} -UR1 {NUR1} -UR2 {NUR2} -o {output_path_aeTSA} -n {normal_sample_name} -s {ash_size} -m {kmer_len} -t {threads_kmer}" 
        print(cmd9_2)
        p = sp.Popen(cmd9_2, stdout=sp.PIPE, stderr=sp.PIPE, shell=True)
        stdout, stderr = p.communicate()
        if p.returncode != 0:
            stderr = stderr.decode(encoding='utf-8')
            sys.stderr.write("Fail.\nError %d: %s\n" % (p.returncode, stderr))
            sys.exit(1)
        
        # This step is to filter k-mer
        tumor_jf_file = output_path_aeTSA + f'/2-jf-database/kmer_generation/{tumor_sample_name}_trim_{kmer_len}.jf'
        normal_jf_file = output_path_aeTSA + f'/2-jf-database/kmer_generation/{normal_sample_name}_trim_{kmer_len}.jf'
        cmd10 = f"aeTSA_3_kmer_filtering.py --tumor_jf_file {tumor_jf_file} --normal_jf_file {normal_jf_file} -o {output_path_aeTSA} -tn {tumor_sample_name} -nn {normal_sample_name} -mm {minimal_kmer_depth} -m {kmer_len}" 
        print(cmd10)
        p = sp.Popen(cmd10, stdout=sp.PIPE, stderr=sp.PIPE, shell=True)
        stdout, stderr = p.communicate()
        if p.returncode != 0:
            stderr = stderr.decode(encoding='utf-8')
            sys.stderr.write("Fail.\nError %d: %s\n" % (p.returncode, stderr))
            sys.exit(1)
        
        # This step is to assemble k-mer
        normal_count_file = output_path_aeTSA + f'/2-jf-database/kmer_filtering_{kmer_len}/4_filtering_k-mers/{tumor_sample_name}.{minimal_kmer_depth}.{normal_sample_name}.0.count'
        cmd11 = f"aeTSA_4_kmer_assembly.py --tumor_jf_file {tumor_jf_file} --normal_count_file {normal_count_file} --nektar_assembly {nektar_assembly} -o {output_path_aeTSA} -tn {tumor_sample_name} -nn {normal_sample_name} -m {kmer_len}" 
        print(cmd11)
        p = sp.Popen(cmd11, stdout=sp.PIPE, stderr=sp.PIPE, shell=True)
        stdout, stderr = p.communicate()
        if p.returncode != 0:
            stderr = stderr.decode(encoding='utf-8')
            sys.stderr.write("Fail.\nError %d: %s\n" % (p.returncode, stderr))
            sys.exit(1)
        
        # This step is to translate k-mer
        assembly_fasta = output_path_aeTSA + f'/2-jf-database/kmer_assembly_k{kmer_len}/assembly_{tumor_sample_name}_result/assembly.fasta'
        assembly_tab = output_path_aeTSA + f'/2-jf-database/kmer_assembly_k{kmer_len}/assembly_{tumor_sample_name}_result/assembly.tab'
        cmd12 = f"aeTSA_5_three_frame_translation.py --assembly_fasta {assembly_fasta} --assembly_tab {assembly_tab} --translation_py {translation_py} -o {output_path_aeTSA} -tn {tumor_sample_name} -nn {normal_sample_name} -m {kmer_len}" 
        print(cmd12)
        p = sp.Popen(cmd12, stdout=sp.PIPE, stderr=sp.PIPE, shell=True)
        stdout, stderr = p.communicate()
        if p.returncode != 0:
            stderr = stderr.decode(encoding='utf-8')
            sys.stderr.write("Fail.\nError %d: %s\n" % (p.returncode, stderr))
            sys.exit(1)

        # Merge with LC-MS/MS peptides      
        RNA_peptide_fasta =  output_path_aeTSA + f'/2-jf-database/translation_k{kmer_len}/{tumor_sample_name}_3-frame.fasta'
        cmd13 = f"aeTSA_6_mass_merge.py -r {RNA_peptide_fasta} -m {mass_peptide_fasta} -o {output_path_aeTSA} -n {tumor_sample_name} -mn {mass_sample_name}" 
        print(cmd13)
        p = sp.Popen(cmd13, stdout=sp.PIPE, stderr=sp.PIPE, shell=True)
        stdout, stderr = p.communicate()
        if p.returncode != 0:
            stderr = stderr.decode(encoding='utf-8')
            sys.stderr.write("Fail.\nError %d: %s\n" % (p.returncode, stderr))
            sys.exit(1)
        return 0
    except:
        return -1
    
def TSA_DNA_and_RNAseq(data_path, parameters):
    print("Run TSA with DNA-seq and RNAseq")
    uid = parameters['task_id']
    user = User_Job.objects.filter(user_id=uid)[0]
    user.total_status = "RUNNING"
    user.start_time = datetime.datetime.now()
    user.save(update_fields=['total_status', 'start_time'])
    # Step1. Set parameters
    dna_N_r1_file = parameters['dna_N_r1_file']
    dna_N_r2_file = parameters['dna_N_r2_file']
    dna_T_r1_file = parameters['dna_T_r1_file']
    dna_T_r2_file = parameters['dna_T_r2_file']
    rna_N_r1_file = parameters['rna_N_r1_file']
    rna_N_r2_file = parameters['rna_N_r2_file']
    rna_T_r1_file = parameters['rna_T_r1_file']
    rna_T_r2_file = parameters['rna_T_r2_file']
    dict_urls = parameters['dict_urls']
    thread = parameters['thread']
    ip = 15
    database_path = parameters['database_path']
    home_path = parameters['home_path']
    output_path = parameters['output_path']
    normal_sample_name = parameters['normal_sample_name']
    tumor_sample_name = parameters['tumor_sample_name']
    tumor_expression_threshold = parameters["tumor_expression_threshold"]
    minimal_expression_ratio = parameters["minimal_expression_ratio"]
    if str(minimal_expression_ratio) == "0.0" or "0":
            minimal_expression_ratio = None
    hla_type_ls = parameters['hla_type_ls']
    hla_typing_step = parameters['hla_typing_step']
    max_strong = parameters['max_ic_strong'] 
    max_intermediate = parameters['max_ic_inter'] 
    max_weak =parameters['max_ic_weak'] 
    hla_type = ','.join(hla_type_ls)
    mass_file_path = parameters['mass_file_path'] 
    mass_step = parameters['mass_step']
    mass_sample_name = "mass.peptide"  
    dna_N_r1_file_path = data_path + '/' + dna_N_r1_file
    dna_N_r2_file_path = data_path + '/' + dna_N_r2_file
    dna_T_r1_file_path = data_path + '/' + dna_T_r1_file
    dna_T_r2_file_path = data_path + '/' + dna_T_r2_file
    rna_N_r1_file_path = data_path + '/' + rna_N_r1_file
    rna_N_r2_file_path = data_path + '/' + rna_N_r2_file
    rna_T_r1_file_path = data_path + '/' + rna_T_r1_file
    rna_T_r2_file_path = data_path + '/' + rna_T_r2_file
    mail = user.mail
    task = "Neoantigen Identification"
    ## set parameters
    DNA_reference = database_path + "/DNA_ref/ref/GRCh38.d1.vd1.fa"
    illuminaclip = database_path + "/adapters/TruSeq3-PE-2.fa:2:30:10:8:true"
    S31285117_Covered = database_path + "/hg38/S31285117_Covered.bed"
    ref_vcf = f"{database_path}/hg38/Homo_sapiens_assembly38.dbsnp138.vcf {database_path}/hg38/1000G_omni2.5.hg38.vcf {database_path}/hg38/Mills_and_1000G_gold_standard.indels.hg38.vcf"
    gnomad = database_path + "/hg38/af-only-gnomad.hg38.vcf"
    pan = database_path + "/hg38/1000g_pon.hg38.vcf.gz"
    small_exac_common_vcf = database_path + "/hg38/small_exac_common_3.hg38.vcf.gz"
    dragen_reference = database_path + "/dragmap/"
    str_table = database_path + "/dragmap/GRCh38.d1.vd1.str.table.tsv"
    gatk3_jar_file = database_path + "/gatk38/opt/gatk-3.8/GenomeAnalysisTK.jar"
    dir_plugins = database_path + "/iedb/VEP_plugins" 
    dir_cache = database_path + "/GRCh38.104_vep"
    sequence_dictionary = database_path + "/hg38/Homo_sapiens_assembly38.dict"
    iedb_install_directory = database_path + '/iedb'
    iedb_fasta_database = database_path + '/iedb_fasta/IEDB_MHC.fasta'
    cosmic_database = database_path + '/cosmic/Census_allMon.csv'
    genomeDir = database_path + "/STAR_idx/"
    index = database_path + "/hg38/Homo_sapiens.GRCh38.cdna.all.fa.index"
    nektar_assembly = database_path + '/nektar/kmer_assembly'
    translation_py = database_path + '/../scripts/aeTSA_translation.py'
    samtools = home_path + '/samtools' 
    tmp = parameters['tmp_path']

        # check if the file exists
    try:
        hla_tsv = output_path + f"{output_path}/{tumor_sample_name}_mTSA_and_aeTSA.tsv" 
        if _is_path_exist(hla_tsv)!=0: 
            # download data
            if bool(dict_urls != {})== True:
                user.data_preparation_status="RUNNING"
                user.save(update_fields=['data_preparation_status'])
                data_tmp_path = str(Path(UPLOAD_BASE_PATH).resolve().joinpath(uid))
                data_preparation_stat = run_data_preparation(data_tmp_path, data_path, dict_urls)
                if(data_preparation_stat!=0):
                    print("pipeline stop at data preparation")
                    user.error_log="INPUT DATA"
                    user.data_preparation_status="FAILED"
                    user.quality_check="FAILED"
                    user.total_status="FAILED"
                    user.end_time=datetime.datetime.now()
                    user.save(update_fields=['error_log','data_preparation_status','total_status','end_time'])
                    failed_email(mail, uid, task, report="report-drna")
                    return -1
                else:
                    user.data_preparation_status="SUCCESSFUL"
                    user.save(update_fields=['data_preparation_status'])
            else:
                user.data_preparation_status="SUCCESSFUL"
                user.save(update_fields=['data_preparation_status']) 

            # DNA-seq part
            # Step2-1. Run quality check
            user.quality_check_status="RUNNING"
            user.save(update_fields=['quality_check_status'])
            print("Run QC")
            run_QC = DNA_1_data_processing(dna_T_r1_file_path, dna_T_r2_file_path, dna_N_r1_file_path, dna_N_r2_file_path, thread, DNA_reference,illuminaclip, output_path, normal_sample_name, tumor_sample_name)
            if(run_QC!=0):
                print("pipeline stop at QC")    
                user.error_log="QC"
                user.quality_check_status="FAILED"
                user.total_status="FAILED"
                user.end_time=datetime.datetime.now()
                user.save(update_fields=['error_log','quality_check_status','total_status','end_time'])
                failed_email(mail, uid, task, report="report-drna")
            else:
                user.quality_check_status="SUCCESSFUL"
                user.save(update_fields=['quality_check_status'])
                print("Step 1 is successful!")

            # Step2-2. Run GATK4
            user.gatk_status="RUNNING"
            user.save(update_fields=['gatk_status'])

            T_alignment_bam = f"{output_path}/mTSA_DNAseq/1-fastq/aligment/{tumor_sample_name}_alignment.bam"
            N_alignment_bam = f"{output_path}/mTSA_DNAseq/1-fastq/aligment/{normal_sample_name}_alignment.bam"
            run_gatk4 = DNA_2_gatk(T_alignment_bam, N_alignment_bam, S31285117_Covered, ref_vcf, tmp, DNA_reference, output_path, normal_sample_name, tumor_sample_name)
            if(run_gatk4!=0):
                print("pipeline stop at gatk4")
                user.error_log="Data preprocessing"
                user.gatk_status="FAILED"
                user.total_status="FAILED"
                user.end_time=datetime.datetime.now()
                user.save(update_fields=['error_log','gatk_status','total_status','end_time'])
                failed_email(mail, uid, task, report="report-drna")
            else:
                user.gatk_status="SUCCESSFUL"
                user.save(update_fields=['gatk_status'])

            # Step2-3. Run Somatic mutation
            user.somatic_status="RUNNING"
            user.save(update_fields=['somatic_status'])
            T_bam = f"{output_path}/mTSA_DNAseq/2-gatk/{tumor_sample_name}/{tumor_sample_name}_recal.bam"
            N_bam = f"{output_path}/mTSA_DNAseq/2-gatk/{normal_sample_name}/{normal_sample_name}_recal.bam"
            run_somatic = DNA_3_SM_calling(N_bam, T_bam, S31285117_Covered, gnomad, pan, small_exac_common_vcf, ip, DNA_reference, output_path, normal_sample_name, tumor_sample_name, tmp)
            if(run_somatic!=0):
                print("pipeline stop at somatic mutation calling")
                user.error_log="Somatic mutation calling"
                user.somatic_status="FAILED"
                user.total_status="FAILED"
                user.end_time=datetime.datetime.now()
                user.save(update_fields=['error_log','somatic_status','total_status','end_time'])
                failed_email(mail, uid, task, report="report-drna")
            else:
                user.somatic_status="SUCCESSFUL"
                user.save(update_fields=['somatic_status'])
            
            # Step2-4. Run Germline mutation
            user.germline_status="RUNNING"
            user.save(update_fields=['germline_status'])
            TPR1 = f"{output_path}/mTSA_DNAseq/1-fastq/trimmed/T_R1.trimmed.paired.fastq.gz"
            TPR2 = f"{output_path}/mTSA_DNAseq/1-fastq/trimmed/T_R2.trimmed.paired.fastq.gz"
            NPR1 = f"{output_path}/mTSA_DNAseq/1-fastq/trimmed/N_R1.trimmed.paired.fastq.gz"
            NPR2 = f"{output_path}/mTSA_DNAseq/1-fastq/trimmed/N_R2.trimmed.paired.fastq.gz"
            T_bam = f"{output_path}/mTSA_DNAseq/2-gatk/{tumor_sample_name}/{tumor_sample_name}_recal.bam"
            N_bam = f"{output_path}/mTSA_DNAseq/2-gatk/{normal_sample_name}/{normal_sample_name}_recal.bam"
            run_germline = DNA_4_GM_calling(TPR1, TPR2, NPR1, NPR2, S31285117_Covered, DNA_reference, thread, dragen_reference, output_path, str_table, normal_sample_name, tumor_sample_name, tmp)
            if(run_germline!=0):
                print("pipeline stop at germline mutation calling")
                user.error_log="Germline mutation calling"
                user.germline_status="FAILED"
                user.total_status="FAILED"
                user.end_time=datetime.datetime.now()
                user.save(update_fields=['error_log','germline_status','total_status','end_time'])
                failed_email(mail, uid, task, report="report-drna")
            else:
                user.germline_status="SUCCESSFUL"
                user.save(update_fields=['germline_status'])

            # Step2-5. Run phasing
            user.phasing_status="RUNNING"
            user.save(update_fields=['phasing_status'])
            T_bam = f"{output_path}/mTSA_DNAseq/2-gatk/{tumor_sample_name}/{tumor_sample_name}_recal.bam"
            somatic_vcf = f"{output_path}/mTSA_DNAseq/3-somatic-mutation/{tumor_sample_name}/SelectVariants/{tumor_sample_name}.final.vcf"
            germline_vcf = f"{output_path}/mTSA_DNAseq/4-germline-mutation/{tumor_sample_name}/SelectVariants/{tumor_sample_name}.final.vcf"
            run_phasing = DNA_5_phasing(somatic_vcf, germline_vcf, T_bam, S31285117_Covered, DNA_reference, gatk3_jar_file, dir_plugins, dir_cache, sequence_dictionary, output_path, tumor_sample_name, tmp)
            if(run_phasing!=0):
                print("pipeline stop at phasing")
                user.error_log="Phasing"
                user.phasing_status="FAILED"
                user.total_status="FAILED"
                user.end_time=datetime.datetime.now()
                user.save(update_fields=['error_log','phasing_status','total_status','end_time'])
                failed_email(mail, uid, task, report="report-drna")
            else:
                user.phasing_status="SUCCESSFUL"
                user.save(update_fields=['phasing_status'])

            # Step2-6. Run kallisto
            user.expression_level_status="RUNNING"
            user.save(update_fields=['expression_level_status'])
            vep_txt = f"{output_path}/mTSA_DNAseq/5-phasing/{tumor_sample_name}/vep/{tumor_sample_name}.somatic.sn.vep.txt"
            run_kallisto = mTSA_4_run_kallisto(rna_N_r1_file_path, rna_N_r2_file_path, rna_T_r1_file_path, rna_T_r2_file_path, index, output_path, vep_txt, tumor_sample_name, header = 49)
            if(run_kallisto!=0):
                print("pipeline stop at RNA expression level calculation")
                user.error_log="RNA expression level calculation"
                user.expression_level_status="FAILED"
                user.rna_total_status="FAILED"
                user.total_status="FAILED"
                user.end_time=datetime.datetime.now()
                user.save(update_fields=['error_log','expression_level_status','rna_total_status','total_status','end_time'])
                failed_email(mail, uid, task, report="report-drna")
            else:
                user.expression_level_status="SUCCESSFUL"
                user.save(update_fields=['expression_level_status'])

            # Step 2-6 HLA genotyping
            if hla_typing_step == True:
                user.hla_status="RUNNING"
                user.save(update_fields=['hla_status'])
                run_optitype = HLA_typing_2_genotyping(NPR1, NPR2, database_path, output_path, normal_sample_name, "-DNA")
                if(run_optitype!=0):
                    user.error_log="HLA_typing"
                    user.hla_status="FAILED"
                    user.total_status="FAILED"
                    user.end_time=datetime.datetime.now()
                    user.save(update_fields=['error_log','hla_status','total_status','end_time'])
                    failed_email(mail, uid, task, report="report-drna")
                else:
                    hla_tsv = output_path + f"/HLA_typing/{normal_sample_name}/2-hla-typing/{normal_sample_name}_result.tsv"
                    optitype_tsv = pd.read_csv(hla_tsv, sep="\t")
                    optitype_A1 = optitype_tsv["A1"]
                    optitype_A2 = optitype_tsv["A2"]
                    optitype_B1 = optitype_tsv["B1"]
                    optitype_B2 = optitype_tsv["B2"]
                    optitype_C1 = optitype_tsv["C1"]
                    optitype_C2 = optitype_tsv["C2"]
                    hla_type_ls = [f"HLA-{optitype_A1[0]}",f"HLA-{optitype_A2[0]}",f"HLA-{optitype_B1[0]}",f"HLA-{optitype_B2[0]}",f"HLA-{optitype_C1[0]}",f"HLA-{optitype_C2[0]}"]
                    hla_type = f"HLA-{optitype_A1[0]},HLA-{optitype_A2[0]},HLA-{optitype_B1[0]},HLA-{optitype_B2[0]},HLA-{optitype_C1[0]},HLA-{optitype_C2[0]}"
                    print(hla_type)
                    user.hla_status="SUCCESSFUL"
                    user.save(update_fields=['hla_status'])
            else:
                print("HLA genotyping step has been skipped.")
                user.hla_status="SKIPPED"
                user.end_time=datetime.datetime.now()
                user.save(update_fields=['hla_status'])

            # Step2-7-0. Run aeTSA pipeline
            if mass_step != True: 
                try:
                    IEDB_list = []
                    for hla in hla_type_ls:
                        if _is_path_exist(f"{iedb_install_directory}/MHC_fasta/IEDB_MHC_{hla}.fasta") == 0: 
                            IEDB_list.append(f"{iedb_install_directory}/MHC_fasta/IEDB_MHC_{hla}.fasta")
                    input_fasta = ' '.join(IEDB_list)
                    mass_file_path = f"{output_path}/dna.rna.mass.fasta"
                    Cat(input_fasta, mass_file_path)
                except:
                    mass_file_path = iedb_fasta_database
            user.aeTSA_status="RUNNING"
            user.save(update_fields=['aeTSA_status'])
            run_asTSA = aeTSA_with_dna_pipeline(rna_T_r1_file_path, rna_T_r2_file_path, rna_N_r1_file_path, rna_N_r2_file_path, nektar_assembly, illuminaclip, translation_py, mass_file_path, output_path, mass_sample_name, normal_sample_name, tumor_sample_name, kmer_len = 33, threads_kmer = 3, ash_size = '1G', minimal_kmer_depth = 5)
            if(run_asTSA!=0):
                print("aeTSA generation step has errors.")
                user.error_log="aeTSA generation"
                user.aeTSA_status="FAILED"
                user.end_time=datetime.datetime.now()
                user.save(update_fields=['error_log','aeTSA_status'])
            else:
                user.aeTSA_status="SUCCESSFUL"
                user.save(update_fields=['aeTSA_status'])
            
            # Step 2-7-1 Run DNA-seq Pvactools
            user.pvactools_status="RUNNING"
            user.save(update_fields=['pvactools_status'])
            T_bam = f"{output_path}/mTSA_DNAseq/2-gatk/{tumor_sample_name}/{tumor_sample_name}_recal.bam"
            somatic_vcf_gz = f"{output_path}/mTSA_DNAseq/5-phasing/{tumor_sample_name}/vep/{tumor_sample_name}.somatic.sn.vep.vcf.gz"
            phasing_vcf_gz = f"{output_path}/mTSA_DNAseq/5-phasing/{tumor_sample_name}/vep/{tumor_sample_name}.phased.vep.vcf.gz"
            RNA_expression_level = f"{output_path}/mTSA_RNAseq/4-quantification/{tumor_sample_name}/{tumor_sample_name}_RNA_expression_level.tsv"
            run_pvactools = DNA_6_pvacseq(somatic_vcf_gz, phasing_vcf_gz, hla_type, iedb_install_directory, cosmic_database, output_path, tumor_sample_name, thread, max_strong, max_intermediate, max_weak, RNA_expression_level, tumor_expression_threshold, minimal_expression_ratio)
            if(run_pvactools!=0):
                print("pipeline stop at Pvactools")
                user.error_log="Pvactools"
                user.pvactools_status="FAILED"
                user.total_status="FAILED"
                user.end_time=datetime.datetime.now()
                user.save(update_fields=['error_log','pvactools_status','total_status','end_time'])
                failed_email(mail, uid, task, report="report-drna")
            
            # Step3-2. Run aeTSA pvactools
            if user.aeTSA_status == "SUCCESSFUL": 
                tsv = f"{output_path}/aeTSA_RNAseq/3-blastp/{tumor_sample_name}_{mass_sample_name}_full_length.tsv"
                run_pvactools = aeTSA_7_pvactools(tsv, hla_type, iedb_install_directory, cosmic_database, output_path, tumor_sample_name, max_strong, max_intermediate, max_weak)
                if(run_pvactools!=0):
                    print("pipeline stop at Pvactools")
                    user.error_log="Pvactools"
                    user.pvactools_status="FAILED"
                    user.end_time=datetime.datetime.now()
                    user.save(update_fields=['error_log','pvactools_status', 'end_time'])
                    failed_email(mail, uid, task, report="report-drna")
                else:
                    user.pvactools_status="SUCCESSFUL"
                    user.save(update_fields=['pvactools_status']) 
            
            # Step3-3. Run aeTSA annotation
            if user.aeTSA_status == "SUCCESSFUL": 
                user.aeTSA_annotation_status="RUNNING"
                user.save(update_fields=['aeTSA_annotation_status'])
                peptide = f"{output_path}/aeTSA_RNAseq/4-hla-binding-affinity/{tumor_sample_name}/2_runing_pvacbind/{tumor_sample_name}_TSA_candidates.tsv"
                run_aeTSA_annotation = aeTSA_8_tsa_annotation(T_bam, N_bam, genomeDir, peptide, output_path, normal_sample_name, tumor_sample_name, thread, samtools, tmp)
                if(run_aeTSA_annotation!=0):
                    print("aeTSA annotation step has errors.")
                    user.error_log="aeTSA annotation"
                    user.aeTSA_annotation_status="FAILED"
                    user.end_time=datetime.datetime.now()
                    user.save(update_fields=['error_log','aeTSA_annotation_status'])
                else:
                    user.aeTSA_annotation_status="SUCCESSFUL"
                    user.save(update_fields=['aeTSA_annotation_status'])
            else:
                print("aeTSA annotation step has been skipped.")
                user.aeTSA_annotation_status="SKIPPED"
                user.end_time=datetime.datetime.now()
                user.save(update_fields=['aeTSA_annotation_status'])
            
            # Step2-8. Run MASS
            if mass_step != True:
                IEDB_list = []
                for hla in hla_type_ls:
                    if _is_path_exist(f"{iedb_install_directory}/MHC_fasta/IEDB_MHC_{hla}.fasta") == 0: 
                        IEDB_list.append(f"{iedb_install_directory}/MHC_fasta/IEDB_MHC_{hla}.fasta")
                input_fasta = ' '.join(IEDB_list)
                print(input_fasta)
                mass_file_path = f"{output_path}/dna.rna.mass.fasta"
                Cat(input_fasta, mass_file_path) 
            user.mass_status="RUNNING"
            user.save(update_fields=['mass_status'])
            dna_fasta = f"{output_path}/mTSA_DNAseq/6-hla-binding-affinity/{tumor_sample_name}/{tumor_sample_name}_filtered.fasta"
            dna_name = "dna.peptide"
            run_mass = DNA_7_mass_merge(dna_fasta, mass_file_path, output_path, dna_name, mass_sample_name)
            if(run_mass!=0):
                print("MASS merging step has errors.")
                user.error_log="MASS"
                user.mass_status="FAILED"
                user.end_time=datetime.datetime.now()
                user.save(update_fields=['error_log','mass_status'])
            else:
                user.mass_status="SUCCESSFUL"
                user.save(update_fields=['mass_status'])

            # Step2-9. Results confirmation
            hla_tsv = output_path + f"/mTSA_DNAseq/6-hla-binding-affinity/{tumor_sample_name}/{tumor_sample_name}_TSA_candidates.tsv"
            if _is_path_exist(hla_tsv)!=0:
                user.error_log="result generation"
                user.dna_total_status="FAILED"
                user.total_status="FAILED"
                user.end_time=datetime.datetime.now()
                user.save(update_fields=['error_log','dna_total_status','total_status','end_time'])
                failed_email(mail, uid, task, report="report-drna")
            else:
                user.dna_total_status="SUCCESSFUL"
                user.total_status = "SUCCESSFUL"
                user.end_time = datetime.datetime.now()
                user.save(update_fields=['quality_check_status','gatk_status','somatic_status','germline_status','phasing_status','expression_level_status','pvactools_status','mass_status','dna_total_status','total_status','end_time'])
                successful_email(mail, uid, task, report="report-drna")

            # Step3-4. Results confirmation
            mTSA = f"{output_path}/mTSA_DNAseq/6-hla-binding-affinity/{tumor_sample_name}/{tumor_sample_name}_TSA_candidates.tsv"
            name_plot = "T.plot"
            if user.aeTSA_annotation_status == "SUCCESSFUL": 
                aeTSA = f"{output_path}/aeTSA_RNAseq/4-hla-binding-affinity/{tumor_sample_name}/2_runing_pvacbind/{tumor_sample_name}_TSA_candidates.tsv"
                run_plot = mTSA_aeTSA_pie_chart(mTSA, output_path, name_plot, aeTSA)
                mTSA_aeTSA_merge(mTSA, aeTSA, output_path, tumor_sample_name)
            else:
                mTSA_aeTSA_merge(mTSA, aeTSA, output_path, tumor_sample_name, aeTSA_status=False)
                run_plot = mTSA_aeTSA_pie_chart(mTSA, output_path, name_plot, aeTSA = False)
            if _is_path_exist(run_plot)!=0:
                user.error_log="result generation"
                user.rna_total_status="FAILED"
                user.total_status="FAILED"
                user.end_time=datetime.datetime.now()
                user.save(update_fields=['error_log','rna_total_status','total_status','end_time'])
                failed_email(mail, uid, task, report="report-drna")
            else:
                user.rna_total_status="SUCCESSFUL"
                user.total_status = "SUCCESSFUL"
                user.end_time = datetime.datetime.now()
                user.save(update_fields=['quality_check_status','gatk_status','somatic_status','germline_status','phasing_status','expression_level_status','pvactools_status','mass_status','dna_total_status','aeTSA_status','aeTSA_annotation_status','rna_total_status','total_status','end_time'])
                successful_email(mail, uid, task, report="report-drna")

        else:
            user.quality_check_status="SUCCESSFUL"
            user.dna_total_status="SUCCESSFUL"
            user.gatk_status="SUCCESSFUL"
            user.total_status = "SUCCESSFUL"
            user.end_time = datetime.datetime.now()
            # times = datetime.datetime.now()
            # user.end_time  = times.strftime("%Y-%m-%d %H:%M:%S")       
            user.save(update_fields=['quality_check_status','gatk_status','somatic_status','germline_status','phasing_status','expression_level_status','pvactools_status','mass_status','dna_total_status','aeTSA_status','aeTSA_annotation_status','rna_total_status','total_status','end_time'])        
            successful_email(mail, uid, task, report="report-drna")
            return 0  

    except:
        uid = parameters['task_id']
        user = User_Job.objects.filter(user_id=uid)[0]
        mail = user.mail
        user.total_status="FAILED"
        user.error_log="Data_format"
        user.end_time = datetime.datetime.now()       
        user.save(update_fields=['error_log','total_status','end_time'])
        failed_email(mail, uid, task, report="report-drna")
        return -1