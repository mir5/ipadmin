# ipm/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import IPRequest


# @receiver(post_save, sender=IPRequest)
# def auto_assign_ips(sender, instance, created, **kwargs):
#     # Only run if the request is updated (not newly created)
#     if not created and instance.status == 'approved':
#         # Check if IPs are already assigned to avoid duplication
#         if instance.assigned_ips.exists():
#             return
#         try:
#             instance.assign_ips()
#         except Exception as e:
#             # Optional: log or handle errors
#             print(f"IP assignment failed for Request #{instance.id}: {e}")