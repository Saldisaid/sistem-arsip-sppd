from django.contrib import admin
from .models import Dokumen, KwitansiSakti


@admin.register(Dokumen)
class DokumenAdmin(admin.ModelAdmin):

    list_display = (
        'jenis_dokumen',
        'sppd_pegawai',
        'rincian_item',
        'nama_file',
        'uploaded_by',
        'uploaded_at'
    )

    list_filter = (
        'jenis_dokumen',
        'uploaded_at',
    )

    search_fields = (
        'nama_file',
        'keterangan',
        'sppd_pegawai__sppd__nomor_surat_tugas',
        'sppd_pegawai__sppd__nomor_sppd',
        'sppd_pegawai__pegawai__user__first_name',
        'sppd_pegawai__pegawai__user__last_name',
        'sppd_pegawai__pegawai__user__username',
        'uploaded_by__user__first_name',
        'uploaded_by__user__last_name',
        'uploaded_by__user__username',
    )

    readonly_fields = (
        'uploaded_at',
        'updated_at',
    )


@admin.register(KwitansiSakti)
class KwitansiSaktiAdmin(admin.ModelAdmin):

    list_display = (
        'nomor_kwitansi',
        'sppd',
        'uploaded_by',
        'uploaded_at'
    )

    list_filter = (
        'uploaded_at',
    )

    search_fields = (
        'nomor_kwitansi',
        'sppd__nomor_surat_tugas',
        'sppd__nomor_sppd',
        'uploaded_by__user__first_name',
        'uploaded_by__user__last_name',
        'uploaded_by__user__username',
    )

    readonly_fields = (
        'uploaded_at',
        'updated_at',
    )
