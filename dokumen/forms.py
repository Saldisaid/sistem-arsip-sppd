from django import forms

from .models import Dokumen, KwitansiSakti


class DokumenUploadForm(forms.ModelForm):
    class Meta:
        model = Dokumen
        fields = (
            'jenis_dokumen',
            'file',
            'keterangan',
        )
        labels = {
            'jenis_dokumen': 'Jenis Dokumen',
            'file': 'File',
            'keterangan': 'Keterangan',
        }
        widgets = {
            'keterangan': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Catatan tambahan jika diperlukan'}),
        }

    def __init__(self, *args, fixed_jenis_dokumen=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fixed_jenis_dokumen = fixed_jenis_dokumen
        if fixed_jenis_dokumen:
            self.fields.pop('jenis_dokumen')

        field_class = (
            'min-h-11 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 '
            'text-slate-900 outline-none focus:border-[#660300] focus:ring-2 focus:ring-[#660300]/10'
        )
        for field in self.fields.values():
            field.widget.attrs['class'] = field_class

        if 'file' in self.fields:
            self.fields['file'].widget.attrs['accept'] = 'image/*,application/pdf'


class KwitansiSaktiForm(forms.ModelForm):
    class Meta:
        model = KwitansiSakti
        fields = (
            'sppd',
            'nomor_kwitansi',
            'file_pdf',
        )
        labels = {
            'sppd': 'SPPD',
            'nomor_kwitansi': 'Nomor Kwitansi',
            'file_pdf': 'File PDF',
        }
        widgets = {
            'nomor_kwitansi': forms.TextInput(attrs={'placeholder': 'Contoh: KWT-001/2026'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        field_class = (
            'min-h-11 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 '
            'text-slate-900 outline-none focus:border-[#660300] focus:ring-2 focus:ring-[#660300]/10'
        )
        for field in self.fields.values():
            field.widget.attrs['class'] = field_class
        self.fields['file_pdf'].widget.attrs['accept'] = 'application/pdf'
