from io import BytesIO
from pathlib import Path

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.files.base import ContentFile
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect, render
from PIL import Image, UnidentifiedImageError

from accounts.permissions import get_role_redirect_url, get_user_role, is_admin_user
from rincian.models import RincianBiayaItem
from sppd.models import SPPDPegawai
from .forms import DokumenUploadForm, KwitansiSaktiForm, SPBYForm
from .models import Dokumen, KwitansiSakti, SPBY, generate_dokumen_filename
from .services import get_kelengkapan_progress, update_status_kelengkapan


MODULES = {
    'dokumen': {
        'title': 'Verifikasi Dokumen',
        'description': 'Pantau kelengkapan tiket, boarding pass, hotel, laporan, dan dokumen pendukung lainnya.',
    },
    'kwitansi': {
        'title': 'Kwitansi & SPBY',
        'description': 'Kelola unggahan kwitansi SAKTI dan SPBY beserta arsip bukti perjalanan dinas.',
    },
}

BIAYA_TO_DOKUMEN = {
    'penginapan': 'hotel',
    'transport': 'lainnya',
    'uang_harian': 'lainnya',
    'representasi': 'lainnya',
}


def get_jenis_dokumen_for_rincian(rincian_item):
    if not rincian_item:
        return None

    pilihan_dokumen = {key for key, _label in Dokumen.JENIS_DOKUMEN}
    if rincian_item.jenis_biaya in pilihan_dokumen:
        return rincian_item.jenis_biaya

    return BIAYA_TO_DOKUMEN.get(rincian_item.jenis_biaya, 'lainnya')


def convert_image_upload_to_pdf(uploaded_file):
    content_type = getattr(uploaded_file, 'content_type', '') or ''
    suffix = Path(uploaded_file.name).suffix.lower()
    is_image = content_type.startswith('image/') or suffix in {
        '.jpg',
        '.jpeg',
        '.png',
        '.webp',
        '.bmp',
        '.tif',
        '.tiff',
    }

    if not is_image:
        return uploaded_file, uploaded_file.name, False

    try:
        uploaded_file.seek(0)
        image = Image.open(uploaded_file)
        image.load()
    except (UnidentifiedImageError, OSError):
        uploaded_file.seek(0)
        return uploaded_file, uploaded_file.name, False

    if image.mode in ('RGBA', 'LA'):
        background = Image.new('RGB', image.size, 'white')
        alpha_channel = image.getchannel('A')
        background.paste(image.convert('RGBA'), mask=alpha_channel)
        image = background
    else:
        image = image.convert('RGB')

    pdf_buffer = BytesIO()
    image.save(pdf_buffer, format='PDF', resolution=100.0)
    pdf_name = f'{Path(uploaded_file.name).stem}.pdf'
    return ContentFile(pdf_buffer.getvalue(), name=pdf_name), pdf_name, True


@login_required
def module_page(request, module):
    if module == 'dokumen':
        if get_user_role(request.user) != 'admin':
            return redirect(get_role_redirect_url(request.user) or 'accounts:login')

        verifikasi_list = (
            SPPDPegawai.objects
            .select_related('sppd', 'pegawai__user')
            .prefetch_related('rincian_biaya__item_list__dokumen_list')
            .order_by('-sppd__created_at', 'pegawai__user__first_name')
        )
        for item in verifikasi_list:
            item.kelengkapan_progress = get_kelengkapan_progress(item)

        context = {
            'page_title': MODULES[module]['title'],
            'module_description': MODULES[module]['description'],
            'verifikasi_list': verifikasi_list,
        }
        return render(request, 'dokumen/verifikasi_list.html', context)

    if module == 'kwitansi':
        if get_user_role(request.user) != 'operator':
            return redirect(get_role_redirect_url(request.user) or 'accounts:login')

        form = KwitansiSaktiForm(prefix='kwitansi')
        spby_form = SPBYForm(prefix='spby')

        if request.method == 'POST':
            form_type = request.POST.get('form_type')
            if form_type == 'spby':
                spby_form = SPBYForm(request.POST, request.FILES, prefix='spby')
                if spby_form.is_valid():
                    spby = spby_form.save(commit=False)
                    spby.uploaded_by = request.user.pegawai
                    spby.save()
                    messages.success(request, 'SPBY berhasil disimpan.')
                    return redirect('dokumen:kwitansi')
            else:
                form = KwitansiSaktiForm(request.POST, request.FILES, prefix='kwitansi')
            if form.is_valid():
                kwitansi = form.save(commit=False)
                kwitansi.uploaded_by = request.user.pegawai
                kwitansi.save()
                messages.success(request, 'Kwitansi SAKTI berhasil disimpan.')
                return redirect('dokumen:kwitansi')

        kwitansi_list = (
            KwitansiSakti.objects
            .select_related('sppd', 'uploaded_by__user')
            .order_by('-uploaded_at')
        )
        spby_list = (
            SPBY.objects
            .select_related('sppd', 'uploaded_by__user')
            .order_by('-uploaded_at')
        )
        context = {
            'page_title': MODULES[module]['title'],
            'module_description': MODULES[module]['description'],
            'form': form,
            'spby_form': spby_form,
            'kwitansi_list': kwitansi_list,
            'spby_list': spby_list,
        }
        return render(request, 'dokumen/kwitansi_list.html', context)

    module_data = MODULES[module]
    context = {
        'page_title': module_data['title'],
        'module': module,
        'module_description': module_data['description'],
    }
    return render(request, 'dokumen/module_page.html', context)


@login_required
def user_sppd_detail(request, sppd_pegawai_id):
    role = get_user_role(request.user)
    if role not in ('admin', 'user'):
        return redirect(get_role_redirect_url(request.user) or 'accounts:login')

    sppd_pegawai_qs = SPPDPegawai.objects.select_related('sppd', 'pegawai__user')
    if role == 'user':
        sppd_pegawai_qs = sppd_pegawai_qs.filter(pegawai=request.user.pegawai)
    sppd_pegawai = get_object_or_404(sppd_pegawai_qs, id=sppd_pegawai_id)

    rincian = getattr(sppd_pegawai, 'rincian_biaya', None)
    item_list = []
    if rincian:
        item_list = (
            rincian.item_list
            .prefetch_related('dokumen_list')
            .order_by('jenis_biaya', 'created_at')
        )

    dokumen_umum = (
        sppd_pegawai.dokumen_list
        .filter(rincian_item__isnull=True)
        .order_by('-uploaded_at')
    )

    context = {
        'page_title': 'Kelengkapan Dokumen',
        'sppd_pegawai': sppd_pegawai,
        'item_list': item_list,
        'dokumen_umum': dokumen_umum,
        'can_upload': role == 'user',
        'kelengkapan_progress': get_kelengkapan_progress(sppd_pegawai),
    }
    return render(request, 'dokumen/user_sppd_detail.html', context)


@login_required
def download_dokumen(request, dokumen_id):
    dokumen = get_object_or_404(
        Dokumen.objects.select_related('sppd_pegawai__sppd', 'sppd_pegawai__pegawai__user'),
        id=dokumen_id,
    )
    role = get_user_role(request.user)

    if role == 'user' and dokumen.sppd_pegawai.pegawai != request.user.pegawai:
        return redirect(get_role_redirect_url(request.user) or 'accounts:login')

    if role not in ('admin', 'user'):
        return redirect(get_role_redirect_url(request.user) or 'accounts:login')

    filename = dokumen.nama_file or Path(dokumen.file.name).name
    return FileResponse(dokumen.file.open('rb'), as_attachment=True, filename=filename)


@login_required
def delete_dokumen(request, dokumen_id):
    dokumen = get_object_or_404(
        Dokumen.objects.select_related('sppd_pegawai__sppd', 'sppd_pegawai__pegawai__user', 'uploaded_by__user'),
        id=dokumen_id,
    )
    role = get_user_role(request.user)

    if role != 'user' or dokumen.uploaded_by != request.user.pegawai:
        return redirect(get_role_redirect_url(request.user) or 'accounts:login')

    if request.method == 'POST':
        sppd_pegawai = dokumen.sppd_pegawai
        dokumen.file.delete(save=False)
        dokumen.delete()
        update_status_kelengkapan(sppd_pegawai)
        messages.success(request, 'Dokumen berhasil dihapus.')
        return redirect('dokumen:user_sppd_detail', sppd_pegawai_id=sppd_pegawai.id)

    return redirect('dokumen:user_sppd_detail', sppd_pegawai_id=dokumen.sppd_pegawai.id)


@login_required
def user_upload_dokumen(request, sppd_pegawai_id, rincian_item_id=None):
    if get_user_role(request.user) != 'user':
        return redirect(get_role_redirect_url(request.user) or 'accounts:login')

    sppd_pegawai = get_object_or_404(
        SPPDPegawai.objects.select_related('sppd', 'pegawai__user'),
        id=sppd_pegawai_id,
        pegawai=request.user.pegawai,
    )
    rincian_item = None
    fixed_jenis_dokumen = None
    fixed_jenis_label = None
    if rincian_item_id:
        rincian_item = get_object_or_404(
            RincianBiayaItem.objects.select_related('rincian__sppd_pegawai'),
            id=rincian_item_id,
            rincian__sppd_pegawai=sppd_pegawai,
        )
        fixed_jenis_dokumen = get_jenis_dokumen_for_rincian(rincian_item)
        fixed_jenis_label = dict(Dokumen.JENIS_DOKUMEN).get(fixed_jenis_dokumen, 'Lainnya')

    if request.method == 'POST':
        form = DokumenUploadForm(
            request.POST,
            request.FILES,
            fixed_jenis_dokumen=fixed_jenis_dokumen,
        )
        if form.is_valid():
            dokumen = form.save(commit=False)
            dokumen.sppd_pegawai = sppd_pegawai
            dokumen.rincian_item = rincian_item
            if fixed_jenis_dokumen:
                dokumen.jenis_dokumen = fixed_jenis_dokumen
            dokumen.uploaded_by = request.user.pegawai
            converted_file, file_name, converted_to_pdf = convert_image_upload_to_pdf(dokumen.file)
            dokumen.file = converted_file
            dokumen.nama_file = generate_dokumen_filename(dokumen, file_name)
            dokumen.save()
            update_status_kelengkapan(sppd_pegawai)
            if converted_to_pdf:
                messages.success(request, 'Dokumen berhasil diunggah dan gambar otomatis dikonversi ke PDF.')
            else:
                messages.success(request, 'Dokumen berhasil diunggah.')
            return redirect('dokumen:user_sppd_detail', sppd_pegawai_id=sppd_pegawai.id)
    else:
        form = DokumenUploadForm(fixed_jenis_dokumen=fixed_jenis_dokumen)

    context = {
        'page_title': 'Upload Dokumen',
        'sppd_pegawai': sppd_pegawai,
        'rincian_item': rincian_item,
        'fixed_jenis_label': fixed_jenis_label,
        'form': form,
    }
    return render(request, 'dokumen/user_upload_dokumen.html', context)
