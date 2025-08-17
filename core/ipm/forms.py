# forms.py
from django import forms
from django.core.exceptions import ValidationError
from ipaddress import ip_address
from .models import IPPoolModel, VlanModel

from django import forms
from django.core.validators import RegexValidator
from .models import VlanModel

from django import forms
from django.core.validators import RegexValidator
from .models import VlanModel

class VlanForm(forms.ModelForm):
    vpn_name = forms.CharField(
        max_length=100,
        required=False,  # Matches blank=True in model
        label="VPN Name",
        validators=[
            RegexValidator(
                regex=r'^[A-Za-z0-9]+$',
                message="VPN Name must contain only letters and numbers."
            )
        ],
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = VlanModel
        fields = [
            'name',
            'vlan_id',
            'description',
            'category',
            'vpn_name',
            'is_visible_to_users',
            'status',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'vlan_id': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'is_visible_to_users': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'status': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        vlan_id = cleaned_data.get('vlan_id')
        vpn_name = cleaned_data.get('vpn_name')

        if vlan_id and vpn_name:
            # Check for duplicates with same vlan_id and same vpn_name
            qs = VlanModel.objects.filter(vlan_id=vlan_id, vpn_name=vpn_name)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)  # Exclude current row if editing
            if qs.exists():
                raise forms.ValidationError(
                    "A VLAN with this VLAN Number and VPN Name already exists."
                )

        return cleaned_data



        
class IPPoolForm(forms.ModelForm):
    class Meta:
        model = IPPoolModel
        fields = '__all__'
    def __init__(self, *args, **kwargs):
        super(IPPoolForm, self).__init__(*args, **kwargs)
        # Filter VLANs to only those with status=True
        self.fields['vlan'].queryset = VlanModel.objects.filter(status=True)



    def clean(self):
        cleaned_data = super().clean()

        vlan = cleaned_data.get("vlan")
        start = cleaned_data.get("ip_range_start")
        end = cleaned_data.get("ip_range_end")
        gateway = cleaned_data.get("gateway")

        # --- 1) Parse IPs and validate format ---
        try:
            start_ip = ip_address(start)
        except Exception:
            self.add_error("ip_range_start", "Enter a valid IP address.")
            return cleaned_data

        try:
            end_ip = ip_address(end)
        except Exception:
            self.add_error("ip_range_end", "Enter a valid IP address.")
            return cleaned_data

        try:
            gw_ip = ip_address(gateway)
        except Exception:
            self.add_error("gateway", "Enter a valid IP address.")
            return cleaned_data

        # --- 2) Ensure all are same IP version ---
        if len({start_ip.version, end_ip.version, gw_ip.version}) != 1:
            raise ValidationError("Start, End, and Gateway must all be IPv4 or all IPv6.")

        # --- 3) Ensure range is valid and > 1 IP ---
        if int(end_ip) <= int(start_ip):
            self.add_error("ip_range_end", "End IP must be greater than Start IP.")
        else:
            ip_count = int(end_ip) - int(start_ip) + 1
            if ip_count <= 1:
                self.add_error("ip_range_end", "Range must contain more than 1 IP.")

        # --- 4) Ensure gateway inside range ---
        if not (int(start_ip) <= int(gw_ip) <= int(end_ip)):
            self.add_error("gateway", "Gateway must be between Start and End IP.")

        # --- 5) Ensure uniqueness within VLAN ---
        if vlan:
            qs = IPPoolModel.objects.filter(vlan=vlan).exclude(pk=self.instance.pk)

            if qs.filter(ip_range_start=start).exists():
                self.add_error("ip_range_start", "This Start IP is already used in this VLAN.")

            if qs.filter(ip_range_end=end).exists():
                self.add_error("ip_range_end", "This End IP is already used in this VLAN.")

            if qs.filter(ip_range_start=start, ip_range_end=end).exists():
                raise ValidationError("This exact IP range already exists in this VLAN.")

        return cleaned_data