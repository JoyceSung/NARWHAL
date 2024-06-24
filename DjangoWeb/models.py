from django.db import models
'''
class StageStatus(ChoiceEnum):
    WAITING = _("Waiting")
    RUNNING = _("Running")
    SUCCESSFUL = _("Successful")
    FAILED = _("Failed")
    SKIPED = _("Skiped")
    
''' 
'''
Total Status Available:
WAITING 
RUNNING 
SUCCESSFUL 
FAILED 
SKIPPED 
Tool Status Available:
'''
class bac_species(models.Model):
    collection=models.CharField(max_length=15,default="NA")
    file_name=models.CharField(max_length=100,default="NA")
    tax_id=models.IntegerField(default=-1)
    s_name=models.CharField(max_length=120,default="NA")


class ip_log(models.Model):
    ip=models.CharField(max_length=25)
    country=models.CharField(max_length=50,default="NA")
    functions=models.CharField(max_length=25,default="NA")
    submission_time=models.DateTimeField(auto_now_add=True)
    
class User_Job(models.Model):
    user_id=models.CharField(max_length=50)
    upload_id=models.CharField(max_length=64)
    ip=models.CharField(max_length=25)
    mail=models.EmailField(max_length=254)
    submission_time=models.DateTimeField(auto_now_add=True)
    start_time=models.DateTimeField(auto_now_add=True)
    end_time=models.DateTimeField(auto_now_add=True)
    total_status=models.CharField(max_length=10,default='WAITING')
    quality_check_status=models.CharField(max_length=10,default='WAITING')
    hla_status=models.CharField(max_length=10,default='WAITING')
    hla_result_status=models.CharField(max_length=10,default='WAITING')
    gatk_status=models.CharField(max_length=10,default='WAITING')
    somatic_status=models.CharField(max_length=10,default='WAITING')
    germline_status=models.CharField(max_length=10,default='WAITING')
    phasing_status=models.CharField(max_length=10,default='WAITING')
    expression_level_status=models.CharField(max_length=10,default='WAITING')
    filtering_status=models.CharField(max_length=10,default='WAITING') 
    mass_status=models.CharField(max_length=10,default='WAITING')  
    aeTSA_status=models.CharField(max_length=10,default='WAITING')  
    aeTSA_annotation_status=models.CharField(max_length=10,default='WAITING')  
    pvactools_status=models.CharField(max_length=10,default='WAITING')
    dna_total_status=models.CharField(max_length=10,default='WAITING')
    rna_total_status=models.CharField(max_length=10,default='WAITING')
    error_log=models.CharField(max_length=50,default='NA')
    data_preparation_status=models.CharField(max_length=50,default='WAITING')   
    shared_neoantigen_status=models.CharField(max_length=50,default='WAITING') 
    hla=models.CharField(max_length=254,default='hla')
    sample_names=models.CharField(max_length=254,default='sample_names')


  