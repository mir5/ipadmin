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
    template_name = 'ipm/list_ippool.html'  # Template for listing IP pools
    context_object_name = 'ip_pools'





class NewVlanView(CreateView):
    model = VlanModel
    form_class = VlanForm
    template_name = 'ipm/new_vlan.html'  # Template for creating a new IP pool
    success_url = reverse_lazy('vlan_list')  # Redirect after successful creation


class ListVlanView(ListView):
    model = VlanModel
    template_name = 'ipm/list_vlan.html'  # Template for listing IP pools
    context_object_name = 'vlans'