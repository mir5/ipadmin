# forms.py
from django import forms
from .models import IPPoolModel

class IPPoolForm(forms.ModelForm):
    class Meta:
        model = IPPoolModel
        fields = '__all__'