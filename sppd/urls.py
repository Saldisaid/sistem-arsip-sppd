from django.urls import path

from . import views


app_name = 'sppd'

urlpatterns = [
    path('', views.sppd_list, name='sppd'),
    path('search/', views.sppd_search, name='search'),
    path('tambah/', views.sppd_create, name='sppd_create'),
    path('<int:sppd_id>/', views.sppd_detail, name='sppd_detail'),
    path('<int:sppd_id>/hapus/', views.sppd_delete, name='sppd_delete'),
    path('<int:sppd_id>/download/<slug:jenis>/', views.download_sppd_document, name='sppd_download'),
    path('operator/', views.operator_dashboard, name='operator_dashboard'),
    path('saya/', views.user_dashboard, name='user_dashboard'),
]
