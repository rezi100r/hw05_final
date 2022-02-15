from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from django.urls import path

from . import views


app_name = 'users'

urlpatterns = [
    path(
        'logout/',
        auth_views.LogoutView.as_view(template_name='users/logged_out.html'),
        name='logout'
    ),
    path(
        'login/',
        auth_views.LoginView.as_view(template_name='users/login.html'),
        name='login'
    ),
    path('signup/', views.SignUp.as_view(), name='signup'),
    path(
        'password_change/done/',
        auth_views.PasswordChangeDoneView.as_view(
            template_name='users/password_change_done.html'
        ),
        name='password_change_done'
    ),
    path(
        'password_change/',
        auth_views.PasswordChangeView.as_view(
            template_name='users/password_change_form.html',
            success_url=reverse_lazy('users:password_change_done')
        ),
        name='password_change'
    ),
    path(
        'password_reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='users/password_reset_done.html'
        ),
        name='password_reset_done'
    ),
    path(
        'password_reset/',
        auth_views.PasswordResetView.as_view(
            template_name='users/password_reset_form.html',
            success_url=reverse_lazy('users:password_reset_done')
        ),
        name='password_reset_form'
    ),
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='users/password_reset_confirm.html',
            success_url=reverse_lazy('users:password_reset_complete'),
        ),
        name='password_reset_confirm'
    ),
    path(
        'reset/done/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='users/password_reset_complete.html'
        ),
        name='password_reset_complete'
    ),
]
