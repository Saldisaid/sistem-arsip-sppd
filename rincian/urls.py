from django.urls import path

from . import views


app_name = 'rincian'

urlpatterns = [
    path('pegawai/<int:sppd_pegawai_id>/', views.rincian_manage, name='rincian_create'),
    path('pegawai/<int:sppd_pegawai_id>/<int:item_id>/edit/', views.rincian_manage, name='rincian_edit'),
    path('pegawai/<int:sppd_pegawai_id>/download/', views.download_rincian_pegawai, name='rincian_download'),
]
