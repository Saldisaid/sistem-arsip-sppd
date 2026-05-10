from django.contrib import admin
from .models import RincianBiaya, RincianBiayaItem

class RincianBiayaItemInline(admin.TabularInline):
    model = RincianBiayaItem
    extra = 1
    

@admin.register(RincianBiaya)
class RincianBiayaAdmin(admin.ModelAdmin):
    list_display = (
        'sppd_pegawai',
        'total_biaya',
        'created_at',
        'updated_at'
    )
    
    search_fields = (
        'sppd_pegawai__sppd__nomor_surat_tugas',
        'sppd_pegawai__sppd__nomor_sppd',
        'sppd_pegawai__pegawai__user__first_name',
        'sppd_pegawai__pegawai__user__last_name',
    )

    inlines = [RincianBiayaItemInline]
    
@admin.register(RincianBiayaItem)
class RincianBiayaItemAdmin(admin.ModelAdmin):

    list_display = (
        'rincian',
        'jenis_biaya',
        'uraian',
        'jumlah',
        'created_at'
    )

    list_filter = (
        'jenis_biaya',
    )

    search_fields = (
        'uraian',
        'rincian__sppd_pegawai__sppd__nomor_surat_tugas',
    )