from .models import IPRequest


def pending_requests(request):
    """Provide pending IP requests (for superusers) to all templates."""
    if request.user.is_authenticated and request.user.is_superuser:
        pending_qs = IPRequest.objects.filter(status='pending').order_by('-created_at')[:10]
        count = IPRequest.objects.filter(status='pending').count()
    else:
        pending_qs = IPRequest.objects.none()
        count = 0

    return {
        'pending_requests': pending_qs,
        'pending_requests_count': count,
    }
