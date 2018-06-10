from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordChangeView,
    PasswordChangeDoneView,
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)
from django.urls import path

from .views import AccountView

app_name = 'account'

urlpatterns = [
    path('', AccountView.as_view(), name='view'),
    path('<int:pk>', AccountView.as_view(), name='view-one'),
    path('profile/', AccountView.as_view(), name='profile'),

    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout', kwargs={'next_page': '/'}),
    path('password/change/', PasswordChangeView.as_view(), name='password-change',
         kwargs={'post_change_redirect': 'account:password-change-done'}),
    path('password/change/done/', PasswordChangeDoneView.as_view(), name='password-change-done'),
    path('password/reset/', PasswordResetView.as_view(), name='password-reset',
         kwargs={'post_reset_redirect': 'account:password-reset-done'}),
    path('password/reset/done/', PasswordResetDoneView.as_view(), name='password-reset-done'),
    path('password/reset/confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm',
         kwargs={'post_reset_redirect': 'account:password-reset-complete'}),
    path('password/reset/complete/', PasswordResetCompleteView.as_view(), name='password-reset-complete'),
]
