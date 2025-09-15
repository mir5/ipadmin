from django.urls import path,include
from . import views
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from accounts.forms import StyledPasswordChangeForm

app_name = "accounts"

urlpatterns = [
    # path('',include('django.contrib.auth.urls'))
    path('login/',views.LoginView.as_view(),name="login"),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('users/new/', views.UserCreateView.as_view(), name='user_create'),
    path('users/<int:pk>/edit/', views.UserEditView.as_view(), name='user_edit'),
    path('users/<int:pk>/password/', views.AdminSetPasswordView.as_view(), name='user_set_password'),
    path('users/<int:pk>/toggle-active/', views.ToggleUserActiveView.as_view(), name='user_toggle_active'),
    path('profile/', views.ProfileUpdateView.as_view(), name='profile'),
    path('password_change/', auth_views.PasswordChangeView.as_view(
        template_name='accounts/password_change.html',
        form_class=StyledPasswordChangeForm,
        success_url=reverse_lazy('accounts:password_change_done'),
    ), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='accounts/password_change_done.html'
    ), name='password_change_done'),
    # path('register/',views.RegisterView.as_view(),name="register"),
]
