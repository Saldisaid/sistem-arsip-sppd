from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import Pegawai


class Command(BaseCommand):
    help = 'Membuat user penandatangan (Ovelio dan Junaidi)'

    def handle(self, *args, **options):
        # Data penandatangan
        penandatangan_data = [
            {
                'username': 'ovelio',
                'first_name': 'Ovelio',
                'last_name': '',
                'email': 'ovelio@kpu.test',
                'jabatan': 'Sekretaris KPU Kabupaten Tolitoli',
            },
            {
                'username': 'junaidi',
                'first_name': 'Junaidi',
                'last_name': '',
                'email': 'junaidi@kpu.test',
                'jabatan': 'Ketua KPU Kabupaten Tolitoli',
            },
        ]

        for data in penandatangan_data:
            username = data['username']
            
            # Cek jika user sudah ada
            if User.objects.filter(username=username).exists():
                user = User.objects.get(username=username)
                self.stdout.write(
                    self.style.WARNING(f'User {username} sudah ada')
                )
                # Update jabatan jika Pegawai sudah ada
                if hasattr(user, 'pegawai'):
                    user.pegawai.jabatan = data['jabatan']
                    user.pegawai.save()
                continue

            # Buat user baru
            user = User.objects.create_user(
                username=username,
                first_name=data['first_name'],
                last_name=data['last_name'],
                email=data['email'],
            )

            # Buat Pegawai untuk user
            pegawai = Pegawai.objects.create(
                user=user,
                jabatan=data['jabatan'],
                role='user',
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f'User dan Pegawai {username} ({data["jabatan"]}) berhasil dibuat'
                )
            )

        self.stdout.write(self.style.SUCCESS('Selesai membuat penandatangan'))
