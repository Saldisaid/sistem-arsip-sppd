from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from django.urls import path, reverse_lazy

from . import views
from .forms import TailwindPasswordChangeForm


app_name = 'accounts'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('laporan/', views.laporan, name='laporan'),
    path('login/', views.RoleBasedLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path(
        'accounts/password_change/',
        auth_views.PasswordChangeView.as_view(
            form_class=TailwindPasswordChangeForm,
            template_name='registration/password_change_form.html',
            success_url=reverse_lazy('accounts:password_change_done'),
        ),
        name='password_change',
    ),
    path(
        'accounts/password_change/done/',
        auth_views.PasswordChangeDoneView.as_view(
            template_name='registration/password_change_done.html',
        ),
        name='password_change_done',
    ),
]
