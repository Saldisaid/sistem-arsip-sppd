# Generated manually because Django is not installed in this shell environment.

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('sppd', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='RincianBiaya',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('keterangan', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('sppd', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='rincian_biaya', to='sppd.sppd')),
            ],
        ),
        migrations.CreateModel(
            name='RincianBiayaItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('jenis_biaya', models.CharField(choices=[('transport', 'Transport'), ('penginapan', 'Penginapan'), ('uang_harian', 'Uang Harian'), ('representasi', 'Representasi'), ('lainnya', 'Lainnya')], max_length=30)),
                ('uraian', models.CharField(max_length=255)),
                ('jumlah', models.DecimalField(decimal_places=2, max_digits=12)),
                ('bukti', models.FileField(blank=True, null=True, upload_to='bukti_rincian/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('rincian', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='item_list', to='rincian.rincianbiaya')),
            ],
        ),
    ]
