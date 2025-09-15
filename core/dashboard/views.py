from django.shortcuts import render
from django.views.generic import TemplateView
from django.db import models
from django.contrib.auth.mixins import LoginRequiredMixin
from ipm.models import VlanModel, IPPoolModel
from requestflow.models import IPRequest
from django.contrib.auth import get_user_model
from requestflow.models import AssignedIP

# Create your views here.
class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Dashboard metrics
        vlan_count = VlanModel.objects.count()
        pool_count = IPPoolModel.objects.count()
        # Total IPs meaning differs for non-superusers
        if self.request.user.is_superuser:
            total_ips = sum(p.total_ip_count for p in IPPoolModel.objects.all())
            assigned_ips_total = AssignedIP.objects.count()
        else:
            # For non-superusers, base totals on their requested IP counts
            total_ips = IPRequest.objects.filter(user=self.request.user).aggregate(
                total=models.Sum('ip_count')
            )['total'] or 0
            assigned_ips_total = AssignedIP.objects.filter(user=self.request.user).count()
        overall_usage_pct = 0
        if total_ips:
            overall_usage_pct = round(assigned_ips_total * 100 / total_ips, 2)
        User = get_user_model()
        total_users = User.objects.count()
        admin_count = User.objects.filter(is_staff=True).count()
        normal_user_count = User.objects.filter(is_staff=False).count()

        # Requests visibility
        if self.request.user.is_superuser:
            total_requests = IPRequest.objects.count()
            pending_count = IPRequest.objects.filter(status='pending').count()
            approved_count = IPRequest.objects.filter(status='approved').count()
            latest_requests = IPRequest.objects.select_related('user', 'vlan').order_by('-created_at')[:10]
        else:
            total_requests = IPRequest.objects.filter(user=self.request.user).count()
            pending_count = IPRequest.objects.filter(user=self.request.user, status='pending').count()
            approved_count = IPRequest.objects.filter(user=self.request.user, status='approved').count()
            latest_requests = IPRequest.objects.select_related('user', 'vlan').filter(user=self.request.user).order_by('-created_at')[:10]

        context.update(
            vlan_count=vlan_count,
            pool_count=pool_count,
            total_ips=total_ips,
            assigned_ips_total=assigned_ips_total,
            overall_usage_pct=overall_usage_pct,
            total_requests=total_requests,
            pending_count=pending_count,
            approved_count=approved_count,
            total_users=total_users,
            admin_count=admin_count,
            normal_user_count=normal_user_count,
            ip_pools=IPPoolModel.objects.select_related('vlan').all(),
            latest_requests=latest_requests,
        )
        return context
