from django.contrib.auth import views as auth_views
from accounts.forms import EmailAuthenticationForm  # or your AuthenticationForm
from django.views.generic import TemplateView
from django.contrib.auth import logout
from django.shortcuts import redirect

class LoginView(auth_views.LoginView):
    print("LoginView initialized with template:")
    template_name = "accounts/login.html"
    form_class = EmailAuthenticationForm
    redirect_authenticated_user = True
    LOGIN_REDIRECT_URL = '/admin'
   