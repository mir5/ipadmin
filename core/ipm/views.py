# views.py
from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import IPPoolModel, VlanModel
from .forms import IPPoolForm, VlanForm
from django.shortcuts import get_object_or_404
from requestflow.models import AssignedIP

class NewIpPoolView(CreateView):
    model = IPPoolModel
    form_class = IPPoolForm
   
    template_name = 'ipm/new_ippool.html'  # Template for creating a new IP pool
    success_url = reverse_lazy('ip_pool_list')  # Redirect after successful creation


class IppoolListView(ListView):
    model = IPPoolModel
    paginate_by = 10  # Number of IP pools per page
    template_name = 'ipm/list_ippool.html'  # Template for listing IP pools
    context_object_name = 'ip_pools'


class EditIPPoolView(UpdateView):
    model = IPPoolModel
    fields = [
        'vlan', 'ip_range_start', 'ip_range_end', 'subnet_mask',
        'gateway', 'dns_servers', 'description', 'is_active'
    ]
    template_name = 'ipm/edit_ippool.html'
    success_url = reverse_lazy('ipm:listippool')  # Adjust to your actual list view name


class DeleteIPPoolView(DeleteView):
    model = IPPoolModel
    template_name = 'ipm/delete_ippool.html'
    success_url = reverse_lazy('ipm:listippool')

    def delete(self, request, *args, **kwargs):
        messages.success(request, "✅ IP Pool deleted successfully.")
        return super().delete(request, *args, **kwargs)


class DetailIPpoolView(DetailView):
    model = IPPoolModel
    template_name = 'ipm/ippool_detail.html'
    context_object_name = 'pool'

    def get_object(self):
        pool_id = self.kwargs.get('pk')
        return get_object_or_404(IPPoolModel, pk=pool_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['assigned_ips'] = AssignedIP.objects.filter(
            ip_request__selected_ippool=self.object
        )
        return context


class NewVlanView(CreateView):
    model = VlanModel
    form_class = VlanForm
    template_name = 'ipm/new_vlan.html'  # Template for creating a new IP pool
    success_url = reverse_lazy('vlan_list')  # Redirect after successful creation


class ListVlanView(ListView):
    model = VlanModel
    paginate_by = 10
    template_name = 'ipm/list_vlan.html'
    context_object_name = 'vlans'

    def get_queryset(self):
        queryset = VlanModel.objects.all().order_by('-id')  # Or any field you prefer

        vlan_name = self.request.GET.get('vlan_name')
        vpn_name = self.request.GET.get('vpn_name')
        status = self.request.GET.get('status')

        if vlan_name:
            queryset = queryset.filter(name__icontains=vlan_name)

        if vpn_name:
            queryset = queryset.filter(vpn_name__icontains=vpn_name)

        if status:
            if status.lower() == 'active':
                queryset = queryset.filter(status=True)
            elif status.lower() == 'inactive':
                queryset = queryset.filter(status=False)   
          

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['vlan_name'] = self.request.GET.get('vlan_name', '')
        context['vpn_name'] = self.request.GET.get('vpn_name', '')
        #context['status'] = self.request.GET.get('status', '')
        return context

    
class EditVlanView(UpdateView):
    model = VlanModel
    fields = ['name', 'vlan_id', 'category', 'vpn_name','description', 'is_visible_to_users', 'status']
    template_name = 'ipm/edit_vlan.html'
    success_url = reverse_lazy('ipm:listvlan')  # Redirect after successful edit


class DeleteVlanView(DeleteView):
    model = VlanModel
    template_name = 'ipm/delete_vlan.html'
    success_url = reverse_lazy('ipm:listvlan')  # Redirect after deletion
    
