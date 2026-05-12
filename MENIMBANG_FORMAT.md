# Format Surat Tugas - Default Menimbang

## Deskripsi
Sistem ini menyediakan template default menimbang untuk surat tugas yang otomatis dimuat saat membuat SPPD baru. User dapat mengedit default menimbang sebelum menyimpan.

## Cara Kerja

### 1. Default Menimbang di Database
Default menimbang tersimpan di tabel `sppd_defaultmenimbang` dengan struktur:
- **urutan**: Nomor urutan penampilan (a, b, c, dst)
- **isi**: Teks menimbang (dapat menggunakan placeholder `{untuk}`)
- **aktif**: Status aktif/tidak (hanya default aktif yang ditampilkan)

### 2. Seeding Default Data
Default menimbang sudah di-seed ke database dengan:
```bash
python manage.py seed_default_menimbang
```

**Default Template (dari dokumen KPU Tolitoli):**
1. `Bahwa dalam rangka {untuk};` → akan diganti dengan "Maksud Perjalanan" dari form
2. `Bahwa untuk melaksanakan tugas sebagaimana point a diatas perlu di keluarkan Surat Tugas;`

### 3. Membuat SPPD Baru
1. Buka halaman "Tambah SPPD"
2. Default menimbang **otomatis dimuat** di form
3. User dapat:
   - ✅ Mengedit isi menimbang
   - ✅ Menambah lebih banyak menimbang (extra form)
   - ✅ Menghapus menimbang yang tidak perlu
4. Saat menyimpan, placeholder `{untuk}` diganti dengan nilai dari field "Maksud Perjalanan"

## Mengubah Default Menimbang

### Via Django Admin
1. Buka `/admin/sppd/defaultmenimbang/`
2. Edit urutan dan isi sesuai kebutuhan
3. Centang/uncentang kolom "aktif" untuk enable/disable
4. Perubahan berlaku otomatis untuk SPPD baru

### Via Management Command (Custom)
Buat file custom command untuk update default:
```python
# sppd/management/commands/update_default_menimbang.py
from django.core.management.base import BaseCommand
from sppd.models import DefaultMenimbang

class Command(BaseCommand):
    def handle(self, *args, **options):
        DefaultMenimbang.objects.filter(urutan=1).update(
            isi='Isi menimbang baru'
        )
```

## Placeholder Tersedia

- `{untuk}` → Diganti dengan nilai field "Maksud Perjalanan" (form SPPD)

## Contoh Format Surat Tugas Output

```
Menimbang:
  a. Bahwa dalam rangka [nilai-maksud-perjalanan];
  b. Bahwa untuk melaksanakan tugas sebagaimana point a diatas perlu 
     di keluarkan Surat Tugas;
```

## Troubleshooting

### Default menimbang tidak muncul di form
- Pastikan command sudah dijalankan: `python manage.py seed_default_menimbang`
- Periksa di admin bahwa `DefaultMenimbang` tidak kosong dan `aktif=True`
- Jalankan migration: `python manage.py migrate sppd`

### Placeholder tidak diganti
- Placeholder hanya diganti saat menyimpan, bukan di form
- Pastikan placeholder benar: `{untuk}` (dengan kurung kurawal)
- Check di database bahwa template menimbang menggunakan placeholder yang benar

## File-file yang Diubah/Dibuat

1. ✅ `sppd/models.py` - Tambah model `DefaultMenimbang`
2. ✅ `sppd/views.py` - Update `sppd_create()` untuk auto-populate
3. ✅ `sppd/admin.py` - Daftarkan `DefaultMenimbang` di admin
4. ✅ `sppd/management/commands/seed_default_menimbang.py` - Management command
5. ✅ `sppd/migrations/0003_defaultmenimbang.py` - Database migration
6. ✅ `MENIMBANG_FORMAT.md` - File ini (dokumentasi)
