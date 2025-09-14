from django import forms
from django.core.exceptions import ValidationError
from ipaddress import ip_address
from .models import IPRequest
from ipm.models import IPPoolModel,VlanModel

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

        return cleaned_data
