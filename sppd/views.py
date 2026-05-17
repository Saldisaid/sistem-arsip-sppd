from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from weasyprint import HTML

from accounts.permissions import get_role_redirect_url, get_user_role, is_admin_user, user_can_access_sppd
from dokumen.services import get_kelengkapan_progress
from .forms import SPPDForm, DasarFormSet, MenimbangFormSet, MenimbangInlineFormSet, DasarInlineFormSet
from .models import SPPD, SPPDPegawai, DefaultMenimbang, SPPDMenimbang, SPPDDasar


def get_menimbang_formset_with_defaults(data=None, prefix='menimbang'):
    """
    Membuat MenimbangFormSet dengan pre-populated default values.
    """
    # Get active default menimbang dari database
    default_menimbang_list = DefaultMenimbang.objects.filter(aktif=True).order_by('urutan')
    
    # Prepare initial data
    initial_data = []
    for default_item in default_menimbang_list:
        initial_data.append({
            'isi': default_item.isi
        })
    
    if data is not None:
        # POST request
        return MenimbangFormSet(data, prefix=prefix)
    
    # GET request dengan initial data
    formset = MenimbangFormSet(prefix=prefix, initial=initial_data)
    return formset


@login_required
@user_passes_test(is_admin_user)
def sppd_list(request):
    """List SPPD with optional filters for year, month, and tujuan."""
    qs = (
        SPPD.objects
        .select_related('created_by__user')
        .prefetch_related('pegawai_list__pegawai__user')
        .order_by('-created_at')
    )

    tahun = request.GET.get('tahun')
    bulan = request.GET.get('bulan')
    tujuan = request.GET.get('tujuan')

    if tahun:
        try:
            qs = qs.filter(tanggal_berangkat__year=int(tahun))
        except ValueError:
            pass

    if bulan:
        try:
            qs = qs.filter(tanggal_berangkat__month=int(bulan))
        except ValueError:
            pass

    if tujuan:
        qs = qs.filter(tujuan__icontains=tujuan)

    # available years for filter dropdown
    years_qs = SPPD.objects.dates('tanggal_berangkat', 'year', order='DESC')
    years = [d.year for d in years_qs]

    months = [
        (1, 'Januari'), (2, 'Februari'), (3, 'Maret'), (4, 'April'),
        (5, 'Mei'), (6, 'Juni'), (7, 'Juli'), (8, 'Agustus'),
        (9, 'September'), (10, 'Oktober'), (11, 'November'), (12, 'Desember'),
    ]

    # Pagination
    paginator = Paginator(qs, 15)
    page_number = request.GET.get('page', 1)
    try:
        page_obj = paginator.page(page_number)
    except:
        page_obj = paginator.page(1)

    context = {
        'page_title': 'Data SPPD',
        'sppd_list': page_obj.object_list,
        'page_obj': page_obj,
        'filter_years': years,
        'filter_months': months,
        'selected_year': tahun,
        'selected_month': bulan,
        'selected_tujuan': tujuan,
    }
    return render(request, 'sppd/sppd_list.html', context)


@login_required
def sppd_search(request):
    """Search/filter SPPD across roles by year, month, and tujuan."""
    role = get_user_role(request.user)

    qs = (
        SPPD.objects
        .select_related('created_by__user')
        .prefetch_related('pegawai_list__pegawai__user')
        .order_by('-created_at')
    )

    # If regular user, limit to SPPD where user is a participant
    if role == 'user':
        qs = qs.filter(pegawai_list__pegawai=request.user.pegawai).distinct()

    tahun = request.GET.get('tahun')
    bulan = request.GET.get('bulan')
    tujuan = request.GET.get('tujuan')

    if tahun:
        try:
            qs = qs.filter(tanggal_berangkat__year=int(tahun))
        except ValueError:
            pass

    if bulan:
        try:
            qs = qs.filter(tanggal_berangkat__month=int(bulan))
        except ValueError:
            pass

    if tujuan:
        qs = qs.filter(tujuan__icontains=tujuan)

    # available years for filter
    years_qs = SPPD.objects.dates('tanggal_berangkat', 'year', order='DESC')
    years = [d.year for d in years_qs]

    months = [
        (1, 'Januari'), (2, 'Februari'), (3, 'Maret'), (4, 'April'),
        (5, 'Mei'), (6, 'Juni'), (7, 'Juli'), (8, 'Agustus'),
        (9, 'September'), (10, 'Oktober'), (11, 'November'), (12, 'Desember'),
    ]

    # Pagination
    paginator = Paginator(qs, 15)
    page_number = request.GET.get('page', 1)
    try:
        page_obj = paginator.page(page_number)
    except:
        page_obj = paginator.page(1)

    context = {
        'page_title': 'Cari SPPD',
        'sppd_list': page_obj.object_list,
        'page_obj': page_obj,
        'filter_years': years,
        'filter_months': months,
        'selected_year': tahun,
        'selected_month': bulan,
        'selected_tujuan': tujuan,
    }
    return render(request, 'sppd/sppd_search.html', context)


@login_required
@user_passes_test(is_admin_user)
def sppd_create(request):
    if request.method == 'POST':
        form = SPPDForm(request.POST)
        menimbang_formset = get_menimbang_formset_with_defaults(data=request.POST)
        dasar_formset = DasarFormSet(request.POST, prefix='dasar')
        
        if form.is_valid() and menimbang_formset.is_valid() and dasar_formset.is_valid():
            sppd = form.save(commit=False)
            sppd.created_by = request.user.pegawai
            sppd.save()
            
            # Add pegawai
            for pegawai in form.cleaned_data['pegawai']:
                SPPDPegawai.objects.get_or_create(sppd=sppd, pegawai=pegawai)

            # Save menimbang forms
            untuk = form.cleaned_data.get('untuk', '')
            for index, menimbang_form in enumerate(menimbang_formset.forms, start=1):
                isi = menimbang_form.cleaned_data.get('isi', '').strip()
                if isi:
                    # Replace placeholder {untuk} dengan nilai maksud perjalanan
                    isi_final = isi.replace('{untuk}', untuk)
                    SPPDMenimbang.objects.create(sppd=sppd, urutan=index, isi=isi_final)

            # Save dasar forms
            for index, dasar_form in enumerate(dasar_formset.forms, start=1):
                isi = dasar_form.cleaned_data.get('isi', '').strip()
                if isi:
                    SPPDDasar.objects.create(sppd=sppd, urutan=index, isi=isi)

            messages.success(request, 'Data SPPD berhasil ditambahkan.')
            return redirect('sppd:sppd')
    else:
        form = SPPDForm()
        menimbang_formset = get_menimbang_formset_with_defaults()
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

    qs = (
        SPPD.objects
        .select_related('created_by__user')
        .prefetch_related('pegawai_list__pegawai__user')
        .order_by('-created_at')
    )

    tahun = request.GET.get('tahun')
    bulan = request.GET.get('bulan')
    tujuan = request.GET.get('tujuan')

    if tahun:
        try:
            qs = qs.filter(tanggal_berangkat__year=int(tahun))
        except ValueError:
            pass

    if bulan:
        try:
            qs = qs.filter(tanggal_berangkat__month=int(bulan))
        except ValueError:
            pass

    if tujuan:
        qs = qs.filter(tujuan__icontains=tujuan)

    # available years for filter dropdown
    years_qs = SPPD.objects.dates('tanggal_berangkat', 'year', order='DESC')
    years = [d.year for d in years_qs]

    months = [
        (1, 'Januari'), (2, 'Februari'), (3, 'Maret'), (4, 'April'),
        (5, 'Mei'), (6, 'Juni'), (7, 'Juli'), (8, 'Agustus'),
        (9, 'September'), (10, 'Oktober'), (11, 'November'), (12, 'Desember'),
    ]

    # Pagination
    paginator = Paginator(qs, 15)
    page_number = request.GET.get('page', 1)
    try:
        page_obj = paginator.page(page_number)
    except:
        page_obj = paginator.page(1)

    context = {
        'page_title': 'Dashboard Operator',
        'role_name': 'Operator',
        'role_description': 'Operator akan menginput dan memperbarui data operasional SPPD sesuai kewenangannya.',
        'sppd_list': page_obj.object_list,
        'page_obj': page_obj,
        'filter_years': years,
        'filter_months': months,
        'selected_year': tahun,
        'selected_month': bulan,
        'selected_tujuan': tujuan,
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

    tahun = request.GET.get('tahun')
    bulan = request.GET.get('bulan')
    tujuan = request.GET.get('tujuan')

    if tahun:
        try:
            perjalanan_list = perjalanan_list.filter(sppd__tanggal_berangkat__year=int(tahun))
        except ValueError:
            pass

    if bulan:
        try:
            perjalanan_list = perjalanan_list.filter(sppd__tanggal_berangkat__month=int(bulan))
        except ValueError:
            pass

    if tujuan:
        perjalanan_list = perjalanan_list.filter(sppd__tujuan__icontains=tujuan)

    # Pagination
    paginator = Paginator(perjalanan_list, 15)
    page_number = request.GET.get('page', 1)
    try:
        page_obj = paginator.page(page_number)
    except:
        page_obj = paginator.page(1)

    for perjalanan in page_obj.object_list:
        perjalanan.kelengkapan_progress = get_kelengkapan_progress(perjalanan)

    # available years for filter dropdown
    years_qs = SPPD.objects.dates('tanggal_berangkat', 'year', order='DESC')
    years = [d.year for d in years_qs]

    months = [
        (1, 'Januari'), (2, 'Februari'), (3, 'Maret'), (4, 'April'),
        (5, 'Mei'), (6, 'Juni'), (7, 'Juli'), (8, 'Agustus'),
        (9, 'September'), (10, 'Oktober'), (11, 'November'), (12, 'Desember'),
    ]

    context = {
        'page_title': 'Dashboard User',
        'role_name': 'User',
        'role_description': 'User akan melihat SPPD pribadi dan mengunggah dokumen pendukung sesuai perjalanan dinasnya.',
        'perjalanan_list': page_obj.object_list,
        'page_obj': page_obj,
        'filter_years': years,
        'filter_months': months,
        'selected_year': tahun,
        'selected_month': bulan,
        'selected_tujuan': tujuan,
    }
    return render(request, 'sppd/user_dashboard.html', context)
