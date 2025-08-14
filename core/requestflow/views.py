from django.views.generic import CreateView, ListView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib import messages
from .models import IPRequest, AssignedIP
from .forms import IPRequestForm, AdminReviewForm
from django.db import transaction
import ipaddress




class AdminReviewView(UserPassesTestMixin, UpdateView):
    model = IPRequest
    fields = ['status', 'admin_comment', 'selected_ippool']
    template_name = 'requestflow/admin_review.html'  # Use your actual template name
    success_url = reverse_lazy('requestflow:admin_requests')  # Adjust to your desired redirect

    def test_func(self):
        # Only allow users with is_staff or is_superuser privileges
        return self.request.user.is_staff or self.request.user.is_superuser

    def form_valid(self, form):
        ip_request = form.instance

        if ip_request.status == 'rejected':
            messages.info(self.request, "Request has been rejected.")
            return super().form_valid(form)

        if ip_request.status == 'approved':
            try:
                with transaction.atomic():
                    ip_request.assign_ips()
                    messages.success(self.request, "Request approved and IPs assigned successfully.")
                    return super().form_valid(form)
            except ValueError as e:
                form.add_error(None, str(e))
                messages.error(self.request, f"Approval failed: {e}")
                ip_request.status = 'pending'  # Reset status if assignment fails
                return super().form_invalid(form)

        # If status is still pending or invalid
        messages.warning(self.request, "No action taken. Please select approve or reject.")
        return super().form_invalid(form)


class IPRequestCreateView(LoginRequiredMixin, CreateView):
    model = IPRequest
    form_class = IPRequestForm
    template_name = 'requestflow/new_request.html'
    success_url = reverse_lazy('requestflow:my_requests')

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, "✅ Request submitted successfully.")
        return super().form_valid(form)

class MyRequestListView(LoginRequiredMixin, ListView):
    model = IPRequest
    template_name = 'requestflow/my_requests.html'
    context_object_name = 'requests'

    def get_queryset(self):
        return IPRequest.objects.filter(user=self.request.user).order_by('-created_at')

class AdminRequestListView(UserPassesTestMixin, ListView):
    model = IPRequest
    template_name = 'requestflow/admin_requests.html'
    context_object_name = 'requests'
    paginate_by = 10  # Show 10 requests per page

    def test_func(self):
        return self.request.user.is_staff

    def get_queryset(self):
        status_filter = self.request.GET.get('status', 'pending')  # Default to 'pending'
        return IPRequest.objects.filter(status=status_filter).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_filter'] = self.request.GET.get('status', 'pending')
        context['status_choices'] = IPRequest.STATUS_CHOICES
        return context






   
class RequestDetailView(LoginRequiredMixin, DetailView):
    model = IPRequest
    template_name = 'requestflow/request_detail.html'
    context_object_name = 'request'


