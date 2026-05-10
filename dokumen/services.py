def get_kelengkapan_progress(sppd_pegawai):
    rincian = getattr(sppd_pegawai, 'rincian_biaya', None)
    if not rincian:
        return {
            'wajib': 0,
            'terupload': 0,
            'lengkap': False,
            'label': 'Belum ada rincian wajib',
        }

    wajib_items = rincian.item_list.filter(wajib_upload=True)
    wajib = sum(item.jumlah_dokumen for item in wajib_items)
    terupload = sum(
        min(item.dokumen_list.count(), item.jumlah_dokumen)
        for item in wajib_items
    )
    lengkap = wajib > 0 and terupload >= wajib

    return {
        'wajib': wajib,
        'terupload': terupload,
        'lengkap': lengkap,
        'label': f'{terupload}/{wajib} dokumen wajib',
    }


def update_status_kelengkapan(sppd_pegawai):
    progress = get_kelengkapan_progress(sppd_pegawai)
    sppd_pegawai.status_kelengkapan = 'lengkap' if progress['lengkap'] else 'belum'
    sppd_pegawai.save(update_fields=['status_kelengkapan'])
