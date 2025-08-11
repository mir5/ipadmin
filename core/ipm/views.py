# views.py
from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import IPPoolModel
from .forms import IPPoolForm

class NewIpPoolView(CreateView):
    model = IPPoolModel
    form_class = IPPoolForm
    template_name = 'ipm/new_ippool.html'  # Template for creating a new IP pool
    success_url = reverse_lazy('ip_pool_list')  # Redirect after successful creation


class RequestListView(ListView):
    model = IPPoolModel
    template_name = 'ipm/list_requests.html'  # Template for listing IP pools
    context_object_name = 'ip_pools'