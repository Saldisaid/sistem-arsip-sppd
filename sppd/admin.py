from django.contrib import admin
from .models import (
    SPPD,
    SPPDMenimbang,
    SPPDDasar,
    SPPDPegawai,
    DefaultMenimbang
)


@admin.register(DefaultMenimbang)
class DefaultMenimbangAdmin(admin.ModelAdmin):
    list_display = ('urutan', 'isi_preview', 'aktif', 'updated_at')
    list_editable = ('aktif',)
    ordering = ('urutan',)
    readonly_fields = ('created_at', 'updated_at')
    
    def isi_preview(self, obj):
        return obj.isi[:60] + '...' if len(obj.isi) > 60 else obj.isi
    isi_preview.short_description = 'Isi'


admin.site.register(SPPD)
admin.site.register(SPPDMenimbang)
admin.site.register(SPPDDasar)
admin.site.register(SPPDPegawai)