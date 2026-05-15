from django import forms
from django.forms import inlineformset_factory, formset_factory

from accounts.models import Pegawai
from rincian.models import RincianBiayaItem

from .models import SPPD, SPPDDasar, SPPDMenimbang


class SPPDMenimbangForm(forms.ModelForm):
    isi = forms.CharField(
        label='Menimbang',
        required=False,
        widget=forms.Textarea(
            attrs={
                'rows': 2,
                'placeholder': 'Masukkan alasan menimbang',
                'class': 'min-h-11 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-slate-900 outline-none focus:border-[#660300] focus:ring-2 focus:ring-[#660300]/10',
            },
        ),
    )

    class Meta:
        model = SPPDMenimbang
        fields = ('isi',)


class SPPDDasarForm(forms.ModelForm):
    isi = forms.CharField(
        label='Dasar',
        required=False,
        widget=forms.Textarea(
            attrs={
                'rows': 2,
                'placeholder': 'Masukkan dasar penugasan',
                'class': 'min-h-11 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-slate-900 outline-none focus:border-[#660300] focus:ring-2 focus:ring-[#660300]/10',
            },
        ),
    )

    class Meta:
        model = SPPDDasar
        fields = ('isi',)


# Formset untuk create view (standalone, bukan inline)
MenimbangFormSet = formset_factory(
    SPPDMenimbangForm,
    extra=3,
    can_delete=False,
)

DasarFormSet = formset_factory(
    SPPDDasarForm,
    extra=3,
    can_delete=False,
)

# Inline formset untuk edit view
MenimbangInlineFormSet = inlineformset_factory(
    SPPD,
    SPPDMenimbang,
    form=SPPDMenimbangForm,
    fields=('isi',),
    extra=2,
    can_delete=True,
)

DasarInlineFormSet = inlineformset_factory(
    SPPD,
    SPPDDasar,
    form=SPPDDasarForm,
    fields=('isi',),
    extra=2,
    can_delete=True,
)


class SPPDForm(forms.ModelForm):
    pegawai = forms.ModelMultipleChoiceField(
        queryset=Pegawai.objects.select_related('user').order_by('user__first_name', 'user__username'),
        label='Pegawai Perjalanan Dinas',
        widget=forms.CheckboxSelectMultiple,
    )

    penandatangan = forms.ModelChoiceField(
        queryset=Pegawai.objects.select_related('user').order_by('user__first_name', 'user__username'),
        label='Penandatangan',
        required=False,
        empty_label='-- Pilih Penandatangan --',
    )

    class Meta:
        model = SPPD
        fields = (
            'nomor_surat_tugas',
            'nomor_sppd',
            'untuk',
            'tujuan',
            'alat_angkutan',
            'tanggal_berangkat',
            'tanggal_kembali',
            'penandatangan',
        )
        labels = {
            'nomor_surat_tugas': 'Nomor Surat Tugas',
            'nomor_sppd': 'Nomor SPPD',
            'untuk': 'Maksud Perjalanan',
            'tujuan': 'Tujuan',
            'alat_angkutan': 'Alat Angkutan',
            'tanggal_berangkat': 'Tanggal Berangkat',
            'tanggal_kembali': 'Tanggal Kembali',
        }
        widgets = {
            'nomor_surat_tugas': forms.TextInput(attrs={'placeholder': 'Contoh: 001/ST/KPU-TLI/V/2026'}),
            'nomor_sppd': forms.TextInput(attrs={'placeholder': 'Opsional'}),
            'untuk': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Uraikan maksud perjalanan dinas'}),
            'tujuan': forms.TextInput(attrs={'placeholder': 'Contoh: Palu'}),
            'alat_angkutan': forms.TextInput(attrs={'placeholder': 'Contoh: Pesawat / Mobil Dinas'}),
            'tanggal_berangkat': forms.DateInput(attrs={'type': 'date'}),
            'tanggal_kembali': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        field_class = (
            'min-h-11 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 '
            'text-slate-900 outline-none focus:border-[#660300] focus:ring-2 focus:ring-[#660300]/10'
        )
        for field_name, field in self.fields.items():
            if field_name == 'pegawai':
                continue
            field.widget.attrs['class'] = field_class

    def clean(self):
        cleaned_data = super().clean()
        tanggal_berangkat = cleaned_data.get('tanggal_berangkat')
        tanggal_kembali = cleaned_data.get('tanggal_kembali')

        if tanggal_berangkat and tanggal_kembali and tanggal_kembali < tanggal_berangkat:
            self.add_error('tanggal_kembali', 'Tanggal kembali tidak boleh sebelum tanggal berangkat.')

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        lama_perjalanan = instance.tanggal_kembali - instance.tanggal_berangkat
        instance.lama_perjalanan = lama_perjalanan.days + 1

        if commit:
            instance.save()

        return instance


class RincianBiayaItemForm(forms.ModelForm):
    class Meta:
        model = RincianBiayaItem
        fields = (
            'jenis_biaya',
            'uraian',
            'jumlah_satuan',
            'harga_satuan',
            'jumlah',
            'wajib_upload',
            'jumlah_dokumen',
        )
        labels = {
            'jenis_biaya': 'Jenis Biaya',
            'uraian': 'Uraian',
            'jumlah_satuan': 'Jumlah',
            'harga_satuan': 'Harga Satuan',
            'jumlah': 'Total',
            'wajib_upload': 'Wajib Upload Bukti',
            'jumlah_dokumen': 'Jumlah Dokumen Wajib',
        }
        widgets = {
            'uraian': forms.TextInput(attrs={'placeholder': 'Contoh: Tiket pesawat Palu - Tolitoli'}),
            'jumlah': forms.NumberInput(attrs={'min': '0', 'step': '0.01', 'readonly': 'readonly', 'id': 'id_total'}),
            'jumlah_dokumen': forms.NumberInput(attrs={'min': '0'}),
            'jumlah_satuan': forms.NumberInput(attrs={'min': '1', 'id': 'id_jumlah_satuan'}),
            'harga_satuan': forms.NumberInput(attrs={'min': '0', 'step': '0.01', 'id': 'id_harga_satuan'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        field_class = (
            'min-h-11 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 '
            'text-slate-900 outline-none focus:border-[#660300] focus:ring-2 focus:ring-[#660300]/10'
        )
        for field_name, field in self.fields.items():
            if field_name == 'wajib_upload':
                field.widget.attrs['class'] = 'h-5 w-5 rounded border-slate-300 text-[#660300]'
                continue
            field.widget.attrs['class'] = field_class
