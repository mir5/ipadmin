from django import forms
from django.core.exceptions import ValidationError
from ipaddress import ip_address
from .models import IPRequest
from ipm.models import IPPoolModel,VlanModel
from requestflow.models import AssignedIP
import ipaddress as _ip

class IPRequestForm(forms.ModelForm):
    class Meta:
        model = IPRequest
        fields = ['vlan', 'ip_count', 'reason', 'duration_days']
        widgets = {
            'vlan': forms.Select(attrs={'class': 'form-select'}),
            'ip_count': forms.NumberInput(attrs={'class': 'form-control'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'duration_days': forms.NumberInput(attrs={'class': 'form-control'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Show only VLANs visible to users (and active)
        self.fields['vlan'].queryset = VlanModel.objects.filter(
            is_visible_to_users=True,
            status=True,
        )


       

    def clean(self):
        cleaned_data = super().clean()
        ip_count = cleaned_data.get('ip_count')
        duration = cleaned_data.get('duration_days')

        if ip_count and ip_count <= 0:
            self.add_error('ip_count', "IP count must be greater than zero.")

        if duration and duration <= 0:
            self.add_error('duration_days', "Duration must be greater than zero.")

        return cleaned_data

class AdminReviewForm(forms.ModelForm):
    manual_assign = forms.BooleanField(required=False, label='Manual IP assignment')
    manual_start_ip = forms.GenericIPAddressField(protocol='IPv4', required=False, label='Start IP',
                                                 widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 192.168.1.10'}))
    manual_end_ip = forms.GenericIPAddressField(protocol='IPv4', required=False, label='End IP',
                                               widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 192.168.1.20'}))
    class Meta:
        model = IPRequest
        fields = ['status', 'admin_comment', 'selected_ippool']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'admin_comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'selected_ippool': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Get the current IPRequest instance
        ip_request = self.instance

        if ip_request and ip_request.vlan:
            self.fields['selected_ippool'].queryset = IPPoolModel.objects.filter(
                is_active=True,
                vlan=ip_request.vlan
            )
        else:
            # Fallback: show no pools if VLAN is missing
            self.fields['selected_ippool'].queryset = IPPoolModel.objects.none()

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        pool = cleaned_data.get('selected_ippool')

        if status == 'approved' and not pool:
            raise ValidationError("You must select an IP pool when approving a request.")

        manual = cleaned_data.get('manual_assign')
        start_ip = cleaned_data.get('manual_start_ip')
        end_ip = cleaned_data.get('manual_end_ip')

        # If approving and manual assignment selected, validate the range
        if status == 'approved' and manual:
            if not pool:
                raise ValidationError("Select an IP pool before manual assignment.")

            if not start_ip:
                self.add_error('manual_start_ip', 'Start IP is required for manual assignment.')
            if not end_ip:
                self.add_error('manual_end_ip', 'End IP is required for manual assignment.')

            if start_ip and end_ip:
                try:
                    s = _ip.IPv4Address(start_ip)
                    e = _ip.IPv4Address(end_ip)
                except Exception:
                    raise ValidationError('Invalid IP address format provided.')

                if s > e:
                    self.add_error('manual_end_ip', 'End IP must be greater than or equal to Start IP.')

                try:
                    p_start = _ip.IPv4Address(pool.ip_range_start)
                    p_end = _ip.IPv4Address(pool.ip_range_end)
                except Exception:
                    raise ValidationError('IP pool range is invalid.')

                if start_ip and not (p_start <= s <= p_end):
                    self.add_error('manual_start_ip', f'Start IP must be within pool range {p_start} - {p_end}.')
                if end_ip and not (p_start <= e <= p_end):
                    self.add_error('manual_end_ip', f'End IP must be within pool range {p_start} - {p_end}.')

                # Ensure the manual range size equals requested ip_count
                if s <= e:
                    required = int(self.instance.ip_count or 0)
                    selected_count = int(e) - int(s) + 1
                    if selected_count != required:
                        raise ValidationError(
                            f'The selected IP range size must equal the requested count ({required}). '
                            f'Current size is {selected_count}.'
                        )

                    # Check for conflicts with already assigned IPs in the same VLAN
                    vlan = pool.vlan
                    # Build list of IP strings in range; limit to reasonable size (required count)
                    ip_list = [str(_ip.IPv4Address(int(s) + i)) for i in range(required)]
                    conflicts = set(
                        AssignedIP.objects.filter(
                            ip_request__selected_ippool__vlan=vlan,
                            ip_address__in=ip_list
                        ).values_list('ip_address', flat=True)
                    )
                    if conflicts:
                        conflict_example = next(iter(conflicts))
                        raise ValidationError(
                            f"One or more IPs in the selected range are already assigned. Example: {conflict_example}"
                        )

        # If approving and NOT manual, ensure pool has enough free IPs
        if status == 'approved' and pool and not manual and self.instance:
            required = int(self.instance.ip_count or 0)
            total = pool.total_ip_count
            used = pool.assigned_ip_count
            free = max(total - used, 0)
            if required > free:
                raise ValidationError(
                    f"Selected IP pool does not have enough free IPs. "
                    f"Required: {required}, Free: {free}."
                )

        return cleaned_data
