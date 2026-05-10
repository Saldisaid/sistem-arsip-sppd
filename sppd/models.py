from django.db import models
from accounts.models import Pegawai


class SPPD(models.Model):

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('proses', 'Proses'),
        ('lengkap', 'Lengkap'),
        ('arsip', 'Arsip'),
    ]

    nomor_surat_tugas = models.CharField(
        max_length=100
    )

    nomor_sppd = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    untuk = models.TextField()

    tujuan = models.CharField(
        max_length=255
    )

    alat_angkutan = models.CharField(
        max_length=100
    )

    tanggal_berangkat = models.DateField()

    tanggal_kembali = models.DateField()

    lama_perjalanan = models.IntegerField()

    created_by = models.ForeignKey(
        Pegawai,
        on_delete=models.SET_NULL,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.nomor_surat_tugas

class SPPDMenimbang(models.Model):

    sppd = models.ForeignKey(
        SPPD,
        on_delete=models.CASCADE,
        related_name='menimbang_list'
    )

    urutan = models.IntegerField()

    isi = models.TextField()

    def __str__(self):
        return f"Menimbang {self.urutan}"


class SPPDDasar(models.Model):

    sppd = models.ForeignKey(
        SPPD,
        on_delete=models.CASCADE,
        related_name='dasar_list'
    )

    urutan = models.IntegerField()

    isi = models.TextField()

    def __str__(self):
        return f"Dasar {self.urutan}"

class SPPDPegawai(models.Model):

    STATUS_CHOICES = [
        ('belum', 'Belum Lengkap'),
        ('lengkap', 'Lengkap'),
    ]

    sppd = models.ForeignKey(
        SPPD,
        on_delete=models.CASCADE,
        related_name='pegawai_list'
    )

    pegawai = models.ForeignKey(
        Pegawai,
        on_delete=models.CASCADE
    )

    status_kelengkapan = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='belum'
    )

    catatan = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.pegawai} - {self.sppd}"