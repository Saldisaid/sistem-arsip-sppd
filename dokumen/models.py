from pathlib import Path

from django.db import models
from django.utils import timezone
from django.utils.text import slugify

from rincian.models import RincianBiayaItem
from sppd.models import SPPD, SPPDPegawai
from accounts.models import Pegawai


def generate_dokumen_filename(instance, original_filename):
    suffix = Path(original_filename).suffix.lower() or '.pdf'
    jenis_key = getattr(instance, 'jenis_dokumen', None) or 'lainnya'
    if jenis_key not in dict(Dokumen.JENIS_DOKUMEN):
        jenis_key = 'dokumen'

    sppd_pegawai = getattr(instance, 'sppd_pegawai', None)
    sppd_nomor = None
    if sppd_pegawai is not None:
        sppd_nomor = getattr(getattr(sppd_pegawai, 'sppd', None), 'nomor_surat_tugas', None)
        if not sppd_nomor:
            sppd_nomor = f'sppd-{sppd_pegawai.id}'
    if not sppd_nomor:
        sppd_nomor = 'sppd'

    timestamp = timezone.localtime(timezone.now()).strftime('%Y%m%d%H%M%S')
    safe_name = slugify(f'{sppd_nomor}_{jenis_key}_{timestamp}', allow_unicode=False)
    return f'{safe_name}{suffix}'


def dokumen_file_upload_to(instance, filename):
    return f'dokumen/{generate_dokumen_filename(instance, filename)}'


class Dokumen(models.Model):

    JENIS_DOKUMEN = [
    ('tiket_pesawat', 'Tiket Pesawat'),
    ('boarding_pass', 'Boarding Pass'),
    ('tiket_travel', 'Tiket Travel'),
    ('tiket_kapal', 'Tiket Kapal'),
    ('hotel', 'Hotel'),
    ('bbm', 'BBM'),
    ('tol', 'Tol'),
    ('parkir', 'Parkir'),
    ('taxi', 'Taxi'),
    ('laporan', 'Laporan'),
    ('dokumentasi', 'Dokumentasi'),
    ('lainnya', 'Lainnya'),
]

    sppd_pegawai = models.ForeignKey(
        SPPDPegawai,
        on_delete=models.CASCADE,
        related_name='dokumen_list'
    )

    rincian_item = models.ForeignKey(
        RincianBiayaItem,
        on_delete=models.SET_NULL,
        related_name='dokumen_list',
        blank=True,
        null=True
    )

    jenis_dokumen = models.CharField(
        max_length=30,
        choices=JENIS_DOKUMEN
    )

    file = models.FileField(
        upload_to=dokumen_file_upload_to
    )

    nama_file = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    keterangan = models.TextField(
        blank=True,
        null=True
    )

    uploaded_by = models.ForeignKey(
        Pegawai,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.get_jenis_dokumen_display()} - {self.sppd_pegawai}"


class KwitansiSakti(models.Model):

    sppd = models.ForeignKey(
        SPPD,
        on_delete=models.CASCADE,
        related_name='kwitansi_list'
    )

    nomor_kwitansi = models.CharField(
        max_length=100
    )

    file_pdf = models.FileField(
        upload_to='kwitansi_sakti/',
        blank=True,
        null=True
    )

    uploaded_by = models.ForeignKey(
        Pegawai,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.nomor_kwitansi


class SPBY(models.Model):

    sppd = models.ForeignKey(
        SPPD,
        on_delete=models.CASCADE,
        related_name='spby_list'
    )

    nomor_spby = models.CharField(
        max_length=100
    )

    file_pdf = models.FileField(
        upload_to='spby/',
        blank=True,
        null=True
    )

    uploaded_by = models.ForeignKey(
        Pegawai,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.nomor_spby
