from django.urls import path,include
from . import views
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy

app_name = "accounts"

urlpatterns = [
    # path('',include('django.contrib.auth.urls'))
    path('login/',views.LoginView.as_view(),name="login"),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('password_change/', auth_views.PasswordChangeView.as_view(
        template_name='accounts/password_change.html',
        success_url=reverse_lazy('accounts:password_change_done'),
    ), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='accounts/password_change_done.html'
    ), name='password_change_done'),
    # path('register/',views.RegisterView.as_view(),name="register"),
]
