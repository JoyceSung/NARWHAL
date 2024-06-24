"""tsa_tool URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from DjangoWeb import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path("", views.index),
    path('admin', admin.site.urls),
    path('index',views.index),
    path('homepage', views.homepage, name='homepage'),
    path('neoantigen-identification', views.neoantigen_identification, name='neoantigen_identification'),
    path('hlagenotyping', views.hlagenotyping, name='hlagenotyping'),
    path('find-overlapped', views.find_overlapped, name='find_overlapped'),
    path('tutorial', views.tutorial, name='tutorial'),
    path('about', views.about, name='about'),
    path('guide', views.guide, name='guide'),

    # data upload
    path('data_upload/', views.data_upload, name='data_upload'),
    path('delete_upload', views.delete_upload, name='delete_upload'),
    path('data_upload_rna/', views.data_upload_rna, name='data_upload_rna'),
    path('delete_upload_rna', views.delete_upload_rna, name='delete_upload_rna'),
     path('data_upload_drna/', views.data_upload_drna, name='data_upload_drna'),
    path('delete_upload_drna', views.delete_upload_drna, name='delete_upload_drna'),
    path('confirm_urls', views.confirm_urls, name='confirm_urls'),
    path('data_upload_tsv/', views.data_upload_tsv, name='data_upload_tsv'),
    path('delete_upload_tsv', views.delete_upload_tsv, name='delete_upload_tsv'),
    path('confirmed_sample_names/', views.confirmed_sample_names, name='confirmed_sample_names'),

    # HLA genotyping
    path('hla_result', views.hla_result, name='hla_result'),
    path('base', views.base, name='base'),
    path('<str:task_id>/status', views.status, name='status'),
    path('<str:task_id>/retrieve', views.retrieve, name='retrieve'),
    path('<str:task_id>/report', views.report, name='report'),
    path('<str:task_id>/report/hla_tsv', views.hla_tsv, name='hla_tsv'),
    # DNA-seq
    path('dna_neo_result', views.dna_neo_result, name='dna_neo_result'),
    path('<str:task_id>/statusdnaneo', views.status_dnaneo, name='status_dnaneo'),
    path('<str:task_id>/retrievednaneo', views.retrieve_dnaneo, name='retrieve_dnaneo'),
    path('<str:task_id>/report-dna', views.report_dnaneo, name='report_dnaneo'),
    path('<str:task_id>/report-dna/dna_mTSA', views.dna_mTSA, name='dna_mTSA'),

    # RNA-seq
    path('rna_neo_result', views.rna_neo_result, name='rna_neo_result'),
    path('<str:task_id>/statusrnaneo', views.status_rnaneo, name='status_rnaneo'),
    path('<str:task_id>/retrievernaneo', views.retrieve_rnaneo, name='retrieve_rnaneo'),
    path('<str:task_id>/report-rna', views.report_rnaneo, name='report_rnaneo'),
    path('<str:task_id>/report-rna/rna_TSA', views.rna_TSA, name='rna_TSA'),

    # DNA-seq + RNA-seq
    path('drna_neo_result', views.drna_neo_result, name='drna_neo_result'),
    path('<str:task_id>/statusdrnaneo', views.status_drnaneo, name='status_drnaneo'),
    path('<str:task_id>/retrievedrnaneo', views.retrieve_drnaneo, name='retrieve_drnaneo'),
    path('<str:task_id>/report-drna', views.report_drnaneo, name='report_drnaneo'),
    path('<str:task_id>/report-drna/drna_TSA', views.drna_TSA, name='drna_TSA'),

    # Find overlapped
    path('find_overlapped_result', views.find_overlapped_result, name='find_overlapped_result'),
    path('<str:task_id>/status-overlapped', views.status_overlapped, name='status_overlapped'),
    path('<str:task_id>/retrieve-overlapped', views.retrieve_overlapped, name='retrieve_overlapped'),
    path('<str:task_id>/report-overlapped', views.report_overlapped, name='report_overlapped'),
    path('<str:task_id>/report-overlapped/overlapped_tsv', views.overlapped_tsv, name='overlapped_tsv'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)