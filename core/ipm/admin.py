

# Register your models here.
from django.contrib import admin
from .models import VlanModel, IPPoolModel

@admin.register(VlanModel)
class VlanModelAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'vlan_id',
        'category',
        'vpn_name',
        'is_visible_to_users',
        'status',
        'created_at',
    )
    list_filter = ('category', 'is_visible_to_users', 'status')
    search_fields = ('name', 'vlan_id', 'vpn_name', 'description')
    ordering = ('vlan_id',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(IPPoolModel)
class IPPoolModelAdmin(admin.ModelAdmin):
    list_display = (
        'vlan',
        'ip_range_start',
        'ip_range_end',
        'subnet_mask',
        'gateway',
        'is_active',
        'created_at',
    )
    list_filter = ('is_active', 'vlan')
    search_fields = ('ip_range_start', 'ip_range_end', 'gateway', 'dns_servers', 'description')
    ordering = ('ip_range_start',)
    readonly_fields = ('created_at', 'updated_at')