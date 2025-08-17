from django.urls import path,include
from . import views
from .views import EditVlanView, DeleteVlanView
from .views import EditIPPoolView, DeleteIPPoolView,DetailIPpoolView


app_name = "ipm"


urlpatterns = [
    # path('',include('django.contrib.auth.urls'))
   # path('login/',views.LoginView.as_view(),name="login"),
   # path('logout/',views.LogoutView.as_view(),name="logout"),
    # path('register/',views.RegisterView.as_view(),name="register"),
    path('ipool/new/', views.NewIpPoolView.as_view(), name='newippool'),
    path('ippool/list/', views.IppoolListView.as_view(), name='ippoollist'),
    path('ippool/<int:pk>/edit/', EditIPPoolView.as_view(), name='edit_ippool'),
    path('ippool/<int:pk>/delete/', DeleteIPPoolView.as_view(), name='delete_ippool'),
    path('ippool/<int:pk>/detail',DetailIPpoolView.as_view(),name="detail_of_pool"),




    path('vlan/new/', views.NewVlanView.as_view(), name='newvlan'),
    path('vlan/list/', views.ListVlanView.as_view(), name='listvlan'),
    path('vlan/<int:pk>/edit/', EditVlanView.as_view(), name='edit_vlan'),
    path('vlan/<int:pk>/delete/', DeleteVlanView.as_view(), name='delete_vlan'),

]
