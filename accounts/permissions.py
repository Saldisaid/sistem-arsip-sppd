from django.urls import reverse


def get_user_role(user):
    if not user.is_authenticated:
        return None

    if user.is_superuser:
        return 'developer'

    if hasattr(user, 'pegawai'):
        return user.pegawai.role

    return None


def get_role_redirect_url(user):
    role = get_user_role(user)

    if role == 'developer':
        return reverse('admin:index')

    if role == 'admin':
        return reverse('accounts:dashboard')

    if role == 'operator':
        return reverse('sppd:operator_dashboard')

    if role == 'user':
        return reverse('sppd:user_dashboard')

    return None


def is_admin_user(user):
    if not user.is_authenticated:
        return False

    return get_user_role(user) == 'admin'


def user_can_access_sppd(user, sppd):
    role = get_user_role(user)
    if role == 'admin':
        return True

    if role == 'user' and hasattr(user, 'pegawai'):
        return sppd.pegawai_list.filter(pegawai=user.pegawai).exists()

    return False
