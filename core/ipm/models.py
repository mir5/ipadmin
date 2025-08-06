from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError

import ipaddress

CATEGORY_CHOICES = [
    (1, 'Private'),
    (2, 'Public'),
    (3, 'Other'),
]




class VlanModel(models.Model):
    # Human-readable name for the VLAN
    name = models.CharField(max_length=100, verbose_name="VLAN Name")

    # VLAN ID used in the network
    vlan_id = models.PositiveIntegerField(
        unique=True,
        verbose_name="VLAN Number",
        validators=[
            MinValueValidator(1),
            MaxValueValidator(2048)
        ]
    )


    # Description of the VLAN's purpose
    description = models.TextField(blank=True, verbose_name="Description")

    # Category or usage type of the VLAN
    category = models.IntegerField(
    choices=CATEGORY_CHOICES,
    default=1,
    verbose_name="Category"
    )



    # VPN range or identifier used for segmentation
    vpn_name = models.CharField(max_length=100, blank=True, verbose_name="VPN Name")

    # Whether this VLAN should be visible to end users
    is_visible_to_users = models.BooleanField(default=False, verbose_name="Visible to Users")
    status=models.BooleanField(default=False,verbose_name="status of vlan")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "VLAN"
        verbose_name_plural = "VLANs"
        ordering = ['vlan_id']

    def __str__(self):
        return f"{self.name} (VLAN {self.vlan_id})"




class IPPoolModel(models.Model):
    # Link to the VLAN this IP pool belongs to
    vlan = models.ForeignKey(VlanModel, on_delete=models.CASCADE, related_name='ip_pools', verbose_name="VLAN")
    
    # IP range start and end
    ip_range_start = models.GenericIPAddressField(protocol='IPv4', verbose_name="Start IP")
    ip_range_end = models.GenericIPAddressField(protocol='IPv4', verbose_name="End IP")

    # Subnet mask
    subnet_mask = models.GenericIPAddressField(protocol='IPv4', verbose_name="Subnet Mask")

    # Default gateway
    gateway = models.GenericIPAddressField(protocol='IPv4', verbose_name="Gateway")

    # Optional DNS servers (comma-separated)
    dns_servers = models.CharField(max_length=255, blank=True, verbose_name="DNS Servers")

    # Description or notes
    description = models.TextField(blank=True, verbose_name="Description")

    # Active status
    is_active = models.BooleanField(default=True, verbose_name="Is Active")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "IP Pool"
        verbose_name_plural = "IP Pools"
        ordering = ['ip_range_start']

    def __str__(self):
        return f"{self.vlan.name} Pool: {self.ip_range_start} - {self.ip_range_end}"
    
    def clean(self):
        # Convert to ipaddress.IPv4Address for comparison
        try:
            start_ip = ipaddress.IPv4Address(self.ip_range_start)
            end_ip = ipaddress.IPv4Address(self.ip_range_end)
            gateway_ip=ipaddress.IPv4Address(self.gateway)
        except ipaddress.AddressValueError:
            raise ValidationError("Invalid IP address format.")

        if start_ip > end_ip:
            raise ValidationError("Start IP must be less than or equal to End IP.")
        if not (start_ip <= gateway_ip <= end_ip):
            raise ValidationError("Gateway IP must be within the IP range.")

