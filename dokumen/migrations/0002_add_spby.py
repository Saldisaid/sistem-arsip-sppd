from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dokumen', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SPBY',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nomor_spby', models.CharField(max_length=100)),
                ('file_pdf', models.FileField(blank=True, null=True, upload_to='spby/')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('sppd', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='spby_list', to='sppd.sppd')),
                ('uploaded_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='accounts.pegawai')),
            ],
        ),
    ]
