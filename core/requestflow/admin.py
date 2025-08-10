from django.contrib import admin
from .models import IPRequest, AssignedIP


@admin.register(IPRequest)
class IPRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'vlan', 'ip_count', 'status', 'created_at')
    list_filter = ('status', 'vlan')
    search_fields = ('user__email', 'reason')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)


@admin.register(AssignedIP)
class AssignedIPAdmin(admin.ModelAdmin):
    list_display = ('id', 'ip_request', 'user', 'ip_address', 'created_at')
    list_filter = ('ip_request__status', 'user')
    search_fields = ('ip_address', 'user__email')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')