from django.urls import path
from .views import (
    IPRequestCreateView, MyRequestListView, AdminRequestListView,
    AdminReviewView, RequestDetailView
)

app_name = 'requestflow'

urlpatterns = [
    path('new/', IPRequestCreateView.as_view(), name='new_request'),
    path('my/', MyRequestListView.as_view(), name='my_requests'),
    path('admin/', AdminRequestListView.as_view(), name='admin_requests'),
    path('admin/<int:pk>/review/', AdminReviewView.as_view(), name='admin_review'),
    path('request/<int:pk>/', RequestDetailView.as_view(), name='request_detail'),
]