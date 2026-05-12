from django.core.management.base import BaseCommand
from sppd.models import DefaultMenimbang


class Command(BaseCommand):
    help = 'Seed default menimbang template untuk surat tugas'

    def handle(self, *args, **options):
        DEFAULT_MENIMBANG_LIST = [
            {
                'urutan': 1,
                'isi': 'Bahwa dalam rangka {untuk};'
            },
            {
                'urutan': 2,
                'isi': 'Bahwa untuk melaksanakan tugas sebagaimana point a diatas perlu di keluarkan Surat Tugas;'
            }
        ]

        created_count = 0
        for menimbang_data in DEFAULT_MENIMBANG_LIST:
            obj, created = DefaultMenimbang.objects.get_or_create(
                urutan=menimbang_data['urutan'],
                defaults={
                    'isi': menimbang_data['isi'],
                    'aktif': True
                }
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Created: {obj}'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'⊘ Already exists: {obj}'
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Selesai! {created_count} default menimbang berhasil dibuat.'
            )
        )
