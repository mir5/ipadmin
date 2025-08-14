from django.db import models

# Create your models here.
from django.db import models
from accounts.models import User
from ipm.models import VlanModel,IPPoolModel
from django.core.exceptions import ValidationError
import ipaddress
from django.db import transaction






class IPRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'In progress'),
        ('approved', ' Approved '),
        ('rejected', 'Rejected'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    vlan = models.ForeignKey(VlanModel, on_delete=models.CASCADE)
    

    ip_count = models.PositiveIntegerField()
    reason = models.TextField()
    duration_days = models.PositiveIntegerField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    admin_comment = models.TextField(blank=True, null=True)
    selected_ippool = models.ForeignKey(
        'ipm.IPPoolModel', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='requests', verbose_name="Selected IP Pool"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Request #{self.id} by {self.user.email}"
 
    def assign_ips(self):
        if self.status != 'approved':
            raise ValueError("Request must be approved before assigning IPs.")
        if not self.selected_ippool:
            raise ValueError("No IP pool selected for this request.")

        vlan = self.selected_ippool.vlan


        existing_ips = set(
              AssignedIP.objects.filter(ip_request__selected_ippool__vlan=vlan)
             .values_list('ip_address', flat=True)
            )



        # Generate IP range from pool
        start_ip = ipaddress.ip_address(self.selected_ippool.ip_range_start)
        end_ip = ipaddress.ip_address(self.selected_ippool.ip_range_end)

        available_ips = []
        current_ip = start_ip

        while current_ip <= end_ip and len(available_ips) < self.ip_count:
            if str(current_ip) not in existing_ips:
                available_ips.append(str(current_ip))
            current_ip += 1

        if len(available_ips) < self.ip_count:
            raise ValueError("Not enough available IPs in this VLAN's pool.")

        # Assign IPs atomically
        with transaction.atomic():
            for ip in available_ips:
               AssignedIP.objects.create(
               ip_request=self,
               user=self.user,
               ip_address=ip,
               
            )


class AssignedIP(models.Model):
    ip_request = models.ForeignKey(IPRequest, on_delete=models.CASCADE, related_name='assigned_ips')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ip_address = models.GenericIPAddressField()
   
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    assigned_by_admin = models.BooleanField(default=False, verbose_name="Assigned by Admin")
    is_monitored = models.BooleanField(default=False, verbose_name="Monitoring Enabled")



    def __str__(self):
        return f"{self.ip_address} → {self.user.email} (Request #{self.ip_request.id})"
    def clean(self):
        super().clean()

        # Ensure IP is unique across all AssignedIP entries
        if AssignedIP.objects.exclude(pk=self.pk).filter(ip_address=self.ip_address).exists():
            raise ValidationError(f"IP address {self.ip_address} is already assigned.")

        # Ensure IP is within the selected IP pool range
        if not self.ip_request or not self.ip_request.selected_ippool:
            raise ValidationError("IPRequest or its selected IP pool is missing.")

        pool = self.ip_request.selected_ippool
        try:
            ip = ipaddress.IPv4Address(self.ip_address)
            start_ip = ipaddress.IPv4Address(pool.ip_range_start)
            end_ip = ipaddress.IPv4Address(pool.ip_range_end)
        except ipaddress.AddressValueError:
            raise ValidationError("Invalid IP address format.")

        if not (start_ip <= ip <= end_ip):
            raise ValidationError(f"IP address {self.ip_address} is outside the pool range {start_ip} - {end_ip}.")
        assigned_count = AssignedIP.objects.filter(ip_request=self.ip_request).exclude(pk=self.pk).count()
        if assigned_count + 1 > self.ip_request.ip_count:
            raise ValidationError(f"Cannot assign more than {self.ip_request.ip_count} IPs for this request.")

