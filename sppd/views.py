from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from weasyprint import HTML

from accounts.permissions import get_role_redirect_url, get_user_role, is_admin_user, user_can_access_sppd
from dokumen.services import get_kelengkapan_progress
from .forms import SPPDForm, DasarFormSet, MenimbangFormSet
from .models import SPPD, SPPDPegawai


@login_required
@user_passes_test(is_admin_user)
def sppd_list(request):
    sppd_list_data = (
        SPPD.objects
        .select_related('created_by__user')
        .prefetch_related('pegawai_list__pegawai__user')
        .order_by('-created_at')
    )
    context = {
        'page_title': 'Data SPPD',
        'sppd_list': sppd_list_data,
    }
    return render(request, 'sppd/sppd_list.html', context)


@login_required
@user_passes_test(is_admin_user)
def sppd_create(request):
    if request.method == 'POST':
        form = SPPDForm(request.POST)
        menimbang_formset = MenimbangFormSet(request.POST, prefix='menimbang')
        dasar_formset = DasarFormSet(request.POST, prefix='dasar')
        if form.is_valid() and menimbang_formset.is_valid() and dasar_formset.is_valid():
            sppd = form.save(commit=False)
            sppd.created_by = request.user.pegawai
            sppd.save()
            for pegawai in form.cleaned_data['pegawai']:
                SPPDPegawai.objects.get_or_create(sppd=sppd, pegawai=pegawai)

            for index, menimbang_form in enumerate(menimbang_formset.forms, start=1):
                isi = menimbang_form.cleaned_data.get('isi')
                if isi:
                    sppd.menimbang_list.create(urutan=index, isi=isi)

            for index, dasar_form in enumerate(dasar_formset.forms, start=1):
                isi = dasar_form.cleaned_data.get('isi')
                if isi:
                    sppd.dasar_list.create(urutan=index, isi=isi)

            messages.success(request, 'Data SPPD berhasil ditambahkan.')
            return redirect('sppd:sppd')
    else:
        form = SPPDForm()
        menimbang_formset = MenimbangFormSet(prefix='menimbang')
        dasar_formset = DasarFormSet(prefix='dasar')

    context = {
        'page_title': 'Tambah SPPD',
        'form': form,
        'menimbang_formset': menimbang_formset,
        'dasar_formset': dasar_formset,
    }
    return render(request, 'sppd/sppd_form.html', context)


@login_required
@user_passes_test(is_admin_user)
def sppd_detail(request, sppd_id):
    sppd = get_object_or_404(
        SPPD.objects.select_related('created_by__user').prefetch_related('pegawai_list__pegawai__user'),
        id=sppd_id,
    )
    pegawai_list = (
        sppd.pegawai_list
        .select_related('pegawai__user')
        .prefetch_related('rincian_biaya__item_list__dokumen_list')
        .order_by('pegawai__user__first_name')
    )
    for item in pegawai_list:
        item.kelengkapan_progress = get_kelengkapan_progress(item)

    context = {
        'page_title': 'Detail SPPD',
        'sppd': sppd,
        'pegawai_list': pegawai_list,
    }
    return render(request, 'sppd/sppd_detail.html', context)


@login_required
@user_passes_test(is_admin_user)
def sppd_delete(request, sppd_id):
    sppd = get_object_or_404(SPPD, id=sppd_id)
    if request.method == 'POST':
        nomor_surat_tugas = sppd.nomor_surat_tugas
        sppd.delete()
        messages.success(request, f'SPPD {nomor_surat_tugas} berhasil dihapus.')

    return redirect('sppd:sppd')


@login_required
def download_sppd_document(request, sppd_id, jenis):
    sppd = get_object_or_404(
        SPPD.objects.prefetch_related('pegawai_list__pegawai__user', 'pegawai_list__rincian_biaya__item_list'),
        id=sppd_id,
    )
    if not user_can_access_sppd(request.user, sppd):
        return redirect(get_role_redirect_url(request.user) or 'accounts:login')

    title_map = {
        'surat-tugas': 'Surat Tugas',
        'surat-perjalanan-dinas': 'Surat Perjalanan Dinas',
        'lampiran': 'Lampiran',
        'rincian-biaya': 'Rincian Biaya',
    }
    title = title_map.get(jenis, 'Dokumen SPPD')

    peserta_list = list(
        sppd.pegawai_list
        .select_related('pegawai__user')
        .prefetch_related('rincian_biaya__item_list')
        .order_by('pegawai__user__first_name')
    )
    for peserta in peserta_list:
        rincian = getattr(peserta, 'rincian_biaya', None)
        peserta.rincian_items = rincian.item_list.all() if rincian else []

    html = render_to_string(
        'sppd/pdf_document.html',
        {
            'title': title,
            'jenis': jenis,
            'sppd': sppd,
            'peserta_list': peserta_list,
            'nomor_dokumen': sppd.nomor_sppd if jenis == 'surat-perjalanan-dinas' else sppd.nomor_surat_tugas,
            'today': timezone.localdate(),
        },
    )
    pdf_file = HTML(string=html, base_url=request.build_absolute_uri('/')).write_pdf()

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{jenis}-{sppd.id}.pdf"'
    return response


@login_required
def operator_dashboard(request):
    if get_user_role(request.user) != 'operator':
        return redirect(get_role_redirect_url(request.user) or 'accounts:login')

    context = {
        'page_title': 'Dashboard Operator',
        'role_name': 'Operator',
        'role_description': 'Operator akan menginput dan memperbarui data operasional SPPD sesuai kewenangannya.',
    }
    return render(request, 'sppd/role_dashboard.html', context)


@login_required
def user_dashboard(request):
    if get_user_role(request.user) != 'user':
        return redirect(get_role_redirect_url(request.user) or 'accounts:login')

    perjalanan_list = (
        SPPDPegawai.objects
        .select_related('sppd', 'pegawai__user')
        .prefetch_related('rincian_biaya__item_list__dokumen_list')
        .filter(pegawai=request.user.pegawai)
        .order_by('-sppd__tanggal_berangkat')
    )
    for perjalanan in perjalanan_list:
        perjalanan.kelengkapan_progress = get_kelengkapan_progress(perjalanan)

    context = {
        'page_title': 'Dashboard User',
        'role_name': 'User',
        'role_description': 'User akan melihat SPPD pribadi dan mengunggah dokumen pendukung sesuai perjalanan dinasnya.',
        'perjalanan_list': perjalanan_list,
    }
    return render(request, 'sppd/user_dashboard.html', context)
