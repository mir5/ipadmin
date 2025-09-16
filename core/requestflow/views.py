from django.views.generic import CreateView, ListView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from .models import IPRequest, AssignedIP
from .forms import IPRequestForm, AdminReviewForm
from django.db import transaction
import ipaddress
from django.db.models import Count, Q
from django.http import JsonResponse, HttpResponseForbidden
from ipm.models import IPPoolModel




class AdminReviewView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = IPRequest
    form_class = AdminReviewForm
    template_name = 'requestflow/admin_review.html'
    success_url = reverse_lazy('requestflow:admin_requests')

    def test_func(self):
        # Only superusers can review requests
        return self.request.user.is_superuser

    def form_valid(self, form):
        ip_request = form.instance

        if ip_request.status == 'rejected':
            messages.info(self.request, "Request has been rejected.")
            return super().form_valid(form)

        if ip_request.status == 'approved':
            try:
                with transaction.atomic():
                    # Manual or automatic assignment
                    manual = form.cleaned_data.get('manual_assign')
                    if manual:
                        start_ip = form.cleaned_data.get('manual_start_ip')
                        end_ip = form.cleaned_data.get('manual_end_ip')
                        pool = form.cleaned_data.get('selected_ippool')

                        # Generate range and assign
                        s = ipaddress.IPv4Address(start_ip)
                        e = ipaddress.IPv4Address(end_ip)

                        # Additional safety checks (should be covered in form.clean())
                        p_start = ipaddress.IPv4Address(pool.ip_range_start)
                        p_end = ipaddress.IPv4Address(pool.ip_range_end)
                        if not (p_start <= s <= p_end and p_start <= e <= p_end and s <= e):
                            raise ValueError("Invalid manual IP range.")

                        # Check for conflicts within VLAN
                        existing_ips = set(
                            AssignedIP.objects.filter(ip_request__selected_ippool__vlan=pool.vlan)
                            .values_list('ip_address', flat=True)
                        )

                        # Ensure range size equals requested ip_count
                        required = int(ip_request.ip_count or 0)
                        selected_count = int(e) - int(s) + 1
                        if selected_count != required:
                            raise ValueError("Manual range size must equal requested IP count.")

                        current = int(s)
                        created = 0
                        while current <= int(e):
                            ip_str = str(ipaddress.IPv4Address(current))
                            if ip_str in existing_ips:
                                raise ValueError(f"IP {ip_str} is already assigned.")
                            AssignedIP.objects.create(
                                ip_request=ip_request,
                                user=ip_request.user,
                                ip_address=ip_str,
                                assigned_by_admin=True,
                            )
                            created += 1
                            current += 1
                    else:
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ip_request = self.object
        user = ip_request.user
        qs = IPRequest.objects.filter(user=user)
        context.update({
            'requester': user,
            'profile': getattr(user, 'user_profile', None),
            'request_stats': {
                'total': qs.count(),
                'approved': qs.filter(status='approved').count(),
                'rejected': qs.filter(status='rejected').count(),
                'pending': qs.filter(status='pending').count(),
            },
            'user_assigned_total': AssignedIP.objects.filter(user=user).count(),
        })
        return context


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
    paginate_by = 10

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



class AdminRequestListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = IPRequest
    template_name = 'requestflow/admin_requests.html'
    context_object_name = 'requests'
    paginate_by = 10  # Show 10 requests per page

    def test_func(self):
        return self.request.user.is_superuser

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






   
class RequestDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = IPRequest
    template_name = 'requestflow/request_detail.html'
    context_object_name = 'ip_request'

    def test_func(self):
        obj = self.get_object()
        # Only allow the creator of the request to view
        return self.request.user == obj.user

    def handle_no_permission(self):
        messages.error(self.request, "You are not allowed to view that request.")
        return redirect('requestflow:my_requests')

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

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


def pool_stats(request, pk):
    """Return JSON with stats for a selected IP pool for the given request.

    Response example:
    {
      "pool_id": 1,
      "total": 50,
      "used": 12,
      "free": 38,
      "required": 5,
      "enough": true
    }
    """
    if not request.user.is_authenticated or not request.user.is_superuser:
        return HttpResponseForbidden()

    ip_request = get_object_or_404(IPRequest, pk=pk)
    pool_id = request.GET.get('pool')
    try:
        pool = IPPoolModel.objects.get(pk=pool_id, is_active=True)
    except (IPPoolModel.DoesNotExist, ValueError, TypeError):
        return JsonResponse({"detail": "Pool not found"}, status=404)

    total = pool.total_ip_count
    used = pool.assigned_ip_count
    free = max(total - used, 0)
    required = ip_request.ip_count or 0

    # Determine first and last used IP within this pool (if any)
    used_first = None
    used_last = None
    if used:
        assigned_list = list(
            AssignedIP.objects.filter(ip_request__selected_ippool=pool)
            .values_list('ip_address', flat=True)
        )
        try:
            ip_objs = [ipaddress.IPv4Address(ip) for ip in assigned_list]
            used_first = str(min(ip_objs))
            used_last = str(max(ip_objs))
        except Exception:
            used_first, used_last = None, None

    return JsonResponse({
        "pool_id": pool.id,
        "total": total,
        "used": used,
        "free": free,
        "required": required,
        "enough": free >= required,
        "used_first": used_first,
        "used_last": used_last,
    })
