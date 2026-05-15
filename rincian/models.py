from django.db import models
from sppd.models import SPPDPegawai

class RincianBiaya(models.Model):
    
    sppd_pegawai = models.OneToOneField(
        SPPDPegawai,
        on_delete=models.CASCADE,
        related_name='rincian_biaya'
    )
    
    keterangan = models.TextField(
        blank=True,
        null=True
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )
    
    @property
    def total_biaya(self):
        return sum(item.jumlah for item in self.item_list.all())
    
    def __str__(self):
        return f"Rincian Biaya - {self.sppd_pegawai}"

class RincianBiayaItem(models.Model):

    JENIS_BIAYA_CHOICES = [
        ('transport', 'Transport'),
        ('penginapan', 'Penginapan'),
        ('uang_harian', 'Uang Harian'),
        ('representasi', 'Representasi'),
        ('tiket_pesawat', 'Tiket Pesawat'),
        ('tiket_travel', 'Tiket Travel'),
        ('tiket_kapal', 'Tiket Kapal'),
        ('bbm', 'BBM'),
        ('tol', 'Tol'),
        ('parkir', 'Parkir'),
        ('taxi', 'Taxi'),
        ('lainnya', 'Lainnya'),
    ]
    
    rincian = models.ForeignKey(
        RincianBiaya,
        on_delete=models.CASCADE,
        related_name='item_list'
    )
    
    jenis_biaya = models.CharField(
        max_length=30,
        choices=JENIS_BIAYA_CHOICES
    )

    uraian = models.CharField(
        max_length=255
    )

    satuan = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    jumlah_satuan = models.PositiveIntegerField(
        default=1
    )

    harga_satuan = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    jumlah = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    wajib_upload = models.BooleanField(
        default=True
    )

    jumlah_dokumen = models.IntegerField(
        default=1
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )
    
    def save(self, *args, **kwargs):
        if self.harga_satuan and self.jumlah_satuan:
            self.jumlah = self.harga_satuan * self.jumlah_satuan
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.get_jenis_biaya_display()} - {self.jumlah}"