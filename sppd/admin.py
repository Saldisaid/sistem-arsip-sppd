from django.contrib import admin
from .models import (
    SPPD,
    SPPDMenimbang,
    SPPDDasar,
    SPPDPegawai
)

admin.site.register(SPPD)
admin.site.register(SPPDMenimbang)
admin.site.register(SPPDDasar)
admin.site.register(SPPDPegawai)