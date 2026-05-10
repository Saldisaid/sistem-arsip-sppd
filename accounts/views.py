from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView
from django.db.models import Count, Sum
from django.shortcuts import render
from django.urls import reverse

from dokumen.models import Dokumen, KwitansiSakti
from rincian.models import RincianBiayaItem
from sppd.models import SPPD, SPPDPegawai
from .models import Pegawai
from .permissions import get_role_redirect_url, is_admin_user


LAPORAN_MODULE = {
    'title': 'Laporan',
    'description': 'Lihat rekap SPPD, biaya perjalanan, kelengkapan dokumen, dan status arsip.',
}


class RoleBasedLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        redirect_url = get_role_redirect_url(self.request.user)
        if redirect_url:
            return redirect_url

        logout(self.request)
        messages.error(self.request, 'Akun belum memiliki role aplikasi. Hubungi developer.')
        return reverse('accounts:login')


@login_required
@user_passes_test(is_admin_user)
def dashboard(request):
    status_counts = {
        item['status']: item['total']
        for item in SPPD.objects.values('status').annotate(total=Count('id'))
    }
    kelengkapan_counts = {
        item['status_kelengkapan']: item['total']
        for item in SPPDPegawai.objects.values('status_kelengkapan').annotate(total=Count('id'))
    }

    total_biaya = RincianBiayaItem.objects.aggregate(total=Sum('jumlah'))['total'] or 0
    dokumen_terbaru = (
        Dokumen.objects
        .select_related('sppd_pegawai__sppd', 'sppd_pegawai__pegawai__user', 'uploaded_by__user')
        .order_by('-uploaded_at')[:5]
    )
    sppd_terbaru = (
        SPPD.objects
        .select_related('created_by__user')
        .order_by('-created_at')[:5]
    )

    context = {
        'page_title': 'Dashboard',
        'total_sppd': SPPD.objects.count(),
        'total_pegawai': Pegawai.objects.count(),
        'total_dokumen': Dokumen.objects.count(),
        'total_kwitansi': KwitansiSakti.objects.count(),
        'total_biaya': total_biaya,
        'status_counts': status_counts,
        'kelengkapan_counts': kelengkapan_counts,
        'dokumen_terbaru': dokumen_terbaru,
        'sppd_terbaru': sppd_terbaru,
    }
    return render(request, 'accounts/dashboard.html', context)


@login_required
@user_passes_test(is_admin_user)
def laporan(request):
    sppd_list = (
        SPPD.objects
        .prefetch_related('pegawai_list__rincian_biaya__item_list')
        .order_by('-created_at')
    )
    for sppd in sppd_list:
        peserta = list(sppd.pegawai_list.all())
        sppd.total_peserta = len(peserta)
        sppd.total_lengkap = sum(1 for item in peserta if item.status_kelengkapan == 'lengkap')
        total_biaya = 0
        for peserta_item in peserta:
            rincian = getattr(peserta_item, 'rincian_biaya', None)
            if rincian:
                total_biaya += sum(item.jumlah for item in rincian.item_list.all())
        sppd.total_biaya = total_biaya

    context = {
        'page_title': LAPORAN_MODULE['title'],
        'module_description': LAPORAN_MODULE['description'],
        'total_sppd': SPPD.objects.count(),
        'total_dokumen': Dokumen.objects.count(),
        'total_kwitansi': KwitansiSakti.objects.count(),
        'total_biaya': RincianBiayaItem.objects.aggregate(total=Sum('jumlah'))['total'] or 0,
        'sppd_list': sppd_list,
    }
    return render(request, 'laporan/laporan.html', context)
