from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, get_user_model

User = get_user_model()

class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Email address',
    }))

    def clean(self):
        email = self.cleaned_data.get('username')  # Still called 'username'
        password = self.cleaned_data.get('password')

        if email and password:
            self.user_cache = authenticate(
                self.request,
                email=email,  # Note: 'email' here must match backend signature
                password=password
            )
            if self.user_cache is None:
                raise forms.ValidationError("Invalid email or password")
            elif not self.user_cache.is_active:
                raise forms.ValidationError("This account is inactive")
        return self.cleaned_data