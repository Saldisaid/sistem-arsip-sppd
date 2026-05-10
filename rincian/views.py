from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from accounts.permissions import get_role_redirect_url, is_admin_user, user_can_access_sppd
from sppd.forms import RincianBiayaItemForm
from sppd.models import SPPDPegawai
from .models import RincianBiaya, RincianBiayaItem


@login_required
@user_passes_test(is_admin_user)
def rincian_manage(request, sppd_pegawai_id, item_id=None):
    sppd_pegawai = get_object_or_404(
        SPPDPegawai.objects.select_related('sppd', 'pegawai__user'),
        id=sppd_pegawai_id,
    )
    rincian, _created = RincianBiaya.objects.get_or_create(sppd_pegawai=sppd_pegawai)
    rincian_item = None
    if item_id:
        rincian_item = get_object_or_404(
            RincianBiayaItem,
            id=item_id,
            rincian=rincian,
        )

    if request.method == 'POST':
        form = RincianBiayaItemForm(request.POST, instance=rincian_item)
        if form.is_valid():
            item = form.save(commit=False)
            item.rincian = rincian
            item.save()
            if rincian_item:
                messages.success(request, 'Rincian biaya berhasil diperbarui.')
            else:
                messages.success(request, 'Rincian biaya berhasil ditambahkan.')
            return redirect('rincian:rincian_create', sppd_pegawai_id=sppd_pegawai.id)
    else:
        form = RincianBiayaItemForm(instance=rincian_item)

    context = {
        'page_title': 'Edit Rincian Biaya' if rincian_item else 'Isi Rincian Biaya',
        'sppd_pegawai': sppd_pegawai,
        'rincian': rincian,
        'rincian_item': rincian_item,
        'form': form,
        'item_list': rincian.item_list.order_by('-created_at'),
    }
    return render(request, 'rincian/rincian_form.html', context)


@login_required
def download_rincian_pegawai(request, sppd_pegawai_id):
    sppd_pegawai = get_object_or_404(
        SPPDPegawai.objects.select_related('sppd', 'pegawai__user'),
        id=sppd_pegawai_id,
    )
    if not user_can_access_sppd(request.user, sppd_pegawai.sppd):
        return redirect(get_role_redirect_url(request.user) or 'accounts:login')

    rincian = getattr(sppd_pegawai, 'rincian_biaya', None)
    content = [
        'Rincian Biaya',
        'E-SPPD KPU Tolitoli',
        '',
        f'Pegawai: {sppd_pegawai.pegawai}',
        f'Nomor ST: {sppd_pegawai.sppd.nomor_surat_tugas}',
        f'Nomor SPPD: {sppd_pegawai.sppd.nomor_sppd or "-"}',
        f'Tujuan: {sppd_pegawai.sppd.tujuan}',
        f'Tanggal: {sppd_pegawai.sppd.tanggal_berangkat} - {sppd_pegawai.sppd.tanggal_kembali}',
        '',
        'RINCIAN',
    ]
    total = 0

    if not rincian:
        content.append('- Belum ada rincian biaya')
    else:
        for item in rincian.item_list.order_by('jenis_biaya', 'created_at'):
            total += item.jumlah
            content.append(f'- {item.get_jenis_biaya_display()} | {item.uraian} | Rp {item.jumlah}')

    content.extend(['', f'Total: Rp {total}'])

    response = HttpResponse('\n'.join(str(line) for line in content), content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename="rincian-biaya-pegawai-{sppd_pegawai.id}.txt"'
    return response
