from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from django.contrib.auth import logout, get_user_model
from django.shortcuts import redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, FormView, UpdateView, View
from django.urls import reverse_lazy
from django.contrib import messages
from .forms import EmailAuthenticationForm, NewUserForm, EditUserForm, SelfProfileForm, StyledSetPasswordForm
from accounts.models import Profile

class LoginView(auth_views.LoginView):
    print("LoginView initialized with template:")
    template_name = "accounts/login.html"
    form_class = EmailAuthenticationForm
    redirect_authenticated_user = True
    LOGIN_REDIRECT_URL = '/admin'


class UserListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = get_user_model()
    template_name = 'accounts/user_list.html'
    context_object_name = 'users'
    paginate_by = 10

    def test_func(self):
        return self.request.user.is_superuser

    def get_queryset(self):
        User = get_user_model()
        qs = User.objects.all().order_by('-created_date')
        q = self.request.GET.get('q', '').strip()
        status = self.request.GET.get('status', '').strip()  # 'enabled' | 'disabled' | ''

        if q:
            from django.db.models import Q
            qs = qs.filter(
                Q(email__icontains=q)
                | Q(user_profile__first_name__icontains=q)
                | Q(user_profile__last_name__icontains=q)
                | Q(user_profile__department__icontains=q)
                | Q(user_profile__phone_number__icontains=q)
            )

        if status == 'enabled':
            qs = qs.filter(is_active=True)
        elif status == 'disabled':
            qs = qs.filter(is_active=False)

        return qs.select_related('user_profile')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['q'] = self.request.GET.get('q', '').strip()
        context['status_filter'] = self.request.GET.get('status', '').strip()
        return context


class UserCreateView(LoginRequiredMixin, UserPassesTestMixin, FormView):
    template_name = 'accounts/new_user.html'
    success_url = reverse_lazy('accounts:user_list')
    form_class = NewUserForm

    def test_func(self):
        return self.request.user.is_superuser

    def form_valid(self, form):
        User = get_user_model()
        email = form.cleaned_data['email']
        password = form.cleaned_data['password1']
        is_staff = form.cleaned_data.get('is_staff', False)

        user = User.objects.create_user(email=email, password=password, is_staff=is_staff)

        # Ensure profile exists and update
        profile = getattr(user, 'user_profile', None)
        if profile is None:
            profile = Profile.objects.create(user=user)
        profile.first_name = form.cleaned_data.get('first_name', '')
        profile.last_name = form.cleaned_data.get('last_name', '')
        profile.department = form.cleaned_data.get('department', '') or None
        if form.cleaned_data.get('phone_number'):
            profile.phone_number = form.cleaned_data['phone_number']
        profile.save()

        messages.success(self.request, f"User {email} created successfully")
        return super().form_valid(form)


class UserEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Profile
    form_class = EditUserForm
    template_name = 'accounts/edit_user.html'
    success_url = reverse_lazy('accounts:user_list')

    def get_object(self, queryset=None):
        # pk in URL refers to user id; fetch profile by user id
        user_id = self.kwargs.get('pk')
        return Profile.objects.get(user__id=user_id)

    def test_func(self):
        return self.request.user.is_superuser
    
    def form_valid(self, form):
        response = super().form_valid(form)
        profile = self.object
        user = profile.user
        is_active = form.cleaned_data.get('is_active', user.is_active)
        if user.is_active != is_active:
            # prevent deactivating self via edit
            if user == self.request.user:
                messages.error(self.request, "You cannot change your own active status.")
                return redirect('accounts:user_list')
            user.is_active = is_active
            user.save(update_fields=['is_active'])
            messages.success(self.request, f"User {user.email} is now {'enabled' if user.is_active else 'disabled'}.")
        else:
            messages.success(self.request, "User profile updated successfully.")
        return response


class ToggleUserActiveView(LoginRequiredMixin, UserPassesTestMixin, View):
    def post(self, request, pk):
        User = get_user_model()
        user = User.objects.get(pk=pk)
        if user == request.user:
            messages.error(request, "You cannot change your own active status.")
            return redirect('accounts:user_list')
        user.is_active = not user.is_active
        user.save(update_fields=['is_active'])
        messages.success(request, f"User {user.email} is now {'enabled' if user.is_active else 'disabled'}.")
        return redirect('accounts:user_list')

    def test_func(self):
        return self.request.user.is_superuser
   
class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = SelfProfileForm
    template_name = 'accounts/profile.html'
    success_url = reverse_lazy('dashboard:index')

    def get_object(self, queryset=None):
        return Profile.objects.get(user=self.request.user)


class AdminSetPasswordView(LoginRequiredMixin, UserPassesTestMixin, FormView):
    template_name = 'accounts/set_password.html'
    form_class = StyledSetPasswordForm
    success_url = reverse_lazy('accounts:user_list')

    def test_func(self):
        return self.request.user.is_superuser

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        User = get_user_model()
        self.target_user = User.objects.get(pk=self.kwargs['pk'])
        kwargs['user'] = self.target_user
        return kwargs

    def form_valid(self, form):
        form.save()
        messages.success(self.request, f"Password updated for {self.target_user.email}.")
        return super().form_valid(form)
