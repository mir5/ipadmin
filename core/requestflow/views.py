from django.views.generic import CreateView, ListView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib import messages
from .models import IPRequest, AssignedIP
from .forms import IPRequestForm, AdminReviewForm
from django.db import transaction
import ipaddress
from django.db.models import Count, Q




class AdminReviewView(UserPassesTestMixin, UpdateView):
    model = IPRequest
    form_class = AdminReviewForm
    template_name = 'requestflow/new_request.html'  # Reuse the new request template layout
    success_url = reverse_lazy('requestflow:admin_requests')

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
        qs = IPRequest.objects.filter(user=self.request.user).order_by('-created_at')
        status_filter = self.request.GET.get('status')
        query = self.request.GET.get('q')

        if status_filter in {code for code, _ in IPRequest.STATUS_CHOICES}:
            qs = qs.filter(status=status_filter)

        if query:
            qs = qs.filter(
                Q(vlan__name__icontains=query)
                | Q(reason__icontains=query)
                | Q(id__icontains=query)
            )
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        status_filter = self.request.GET.get('status', '')
        query = self.request.GET.get('q', '')

        # Counts per status for this user's requests
        base_qs = IPRequest.objects.filter(user=self.request.user)
        counts = base_qs.values('status').annotate(total=Count('id'))
        status_counts = {code: 0 for code, _ in IPRequest.STATUS_CHOICES}
        for row in counts:
            status_counts[row['status']] = row['total']

        context.update(
            status_filter=status_filter,
            q=query,
            status_buttons=[
                {
                    'code': code,
                    'label': label,
                    'count': status_counts.get(code, 0),
                }
                for code, label in IPRequest.STATUS_CHOICES
            ],
        )
        return context



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

        # Add counts per status for filter buttons
        counts = IPRequest.objects.values('status').annotate(total=Count('id'))
        status_counts = {code: 0 for code, _ in IPRequest.STATUS_CHOICES}
        for row in counts:
            status_counts[row['status']] = row['total']
        context['status_buttons'] = [
            {
                'code': code,
                'label': label,
                'count': status_counts.get(code, 0),
            }
            for code, label in IPRequest.STATUS_CHOICES
        ]
        return context






   
class RequestDetailView(LoginRequiredMixin, DetailView):
    model = IPRequest
    template_name = 'requestflow/request_detail.html'
    context_object_name = 'request'

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        # Only the request owner or staff can update comments
        if not (request.user.is_staff or request.user == self.object.user):
            messages.error(request, "You are not allowed to update comments for this request.")
            return redirect('requestflow:request_detail', pk=self.object.pk)

        updated = 0
        for ip in self.object.assigned_ips.all():
            field_name = f'desc_{ip.id}'
            if field_name in request.POST:
                new_desc = request.POST.get(field_name, '').strip()
                if new_desc != (ip.description or ''):
                    ip.description = new_desc
                    ip.save(update_fields=['description', 'updated_at'])
                    updated += 1

        if updated:
            messages.success(request, f"Saved comments for {updated} IP(s).")
        else:
            messages.info(request, "No changes to save.")

        return redirect('requestflow:request_detail', pk=self.object.pk)


    
