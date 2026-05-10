from django.urls import path

from . import views


app_name = 'dokumen'

urlpatterns = [
    path('', views.module_page, {'module': 'dokumen'}, name='dokumen'),
    path('kwitansi/', views.module_page, {'module': 'kwitansi'}, name='kwitansi'),
    path('file/<int:dokumen_id>/download/', views.download_dokumen, name='download_dokumen'),
    path('sppd/<int:sppd_pegawai_id>/', views.user_sppd_detail, name='user_sppd_detail'),
    path('sppd/<int:sppd_pegawai_id>/upload/', views.user_upload_dokumen, name='user_upload_dokumen_umum'),
    path(
        'sppd/<int:sppd_pegawai_id>/upload/<int:rincian_item_id>/',
        views.user_upload_dokumen,
        name='user_upload_dokumen',
    ),
]
