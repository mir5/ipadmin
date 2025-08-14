# views.py
from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import IPPoolModel, VlanModel
from .forms import IPPoolForm, VlanForm

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




class NewVlanView(CreateView):
    model = VlanModel
    form_class = VlanForm
    template_name = 'ipm/new_vlan.html'  # Template for creating a new IP pool
    success_url = reverse_lazy('vlan_list')  # Redirect after successful creation


class ListVlanView(ListView):
    model = VlanModel
    paginate_by = 10  # Number of VLANs per page
    template_name = 'ipm/list_vlan.html'  # Template for listing IP pools
    context_object_name = 'vlans'


    
class EditVlanView(UpdateView):
    model = VlanModel
    fields = ['name', 'vlan_id', 'category', 'vpn_name','description', 'is_visible_to_users', 'status']
    template_name = 'ipm/edit_vlan.html'
    success_url = reverse_lazy('ipm:listvlan')  # Redirect after successful edit


class DeleteVlanView(DeleteView):
    model = VlanModel
    template_name = 'ipm/delete_vlan.html'
    success_url = reverse_lazy('ipm:listvlan')  # Redirect after deletion
    
