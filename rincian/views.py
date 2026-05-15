from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.utils import timezone
from weasyprint import HTML

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
    item_list = rincian.item_list.order_by('jenis_biaya', 'created_at') if rincian else []
    total = sum(item.jumlah for item in item_list)
    
    penandatangan = sppd_pegawai.sppd.penandatangan if sppd_pegawai.sppd.penandatangan else None

    html = render_to_string(
        'rincian/rincian_pdf.html',
        {
            'sppd_pegawai': sppd_pegawai,
            'rincian': rincian,
            'item_list': item_list,
            'total': total,
            'penandatangan': penandatangan,
            'today': timezone.localdate(),
        },
    )
    pdf_file = HTML(string=html, base_url=request.build_absolute_uri('/')).write_pdf()

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="rincian-biaya-pegawai-{sppd_pegawai.id}.pdf"'
    return response
