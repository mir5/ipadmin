from django.urls import path,include
from . import views

app_name = "ipm"


urlpatterns = [
    # path('',include('django.contrib.auth.urls'))
   # path('login/',views.LoginView.as_view(),name="login"),
   # path('logout/',views.LogoutView.as_view(),name="logout"),
    # path('register/',views.RegisterView.as_view(),name="register"),
    path('ipool/new/', views.NewIpPoolView.as_view(), name='newippool'),
    path('ippool/list/', views.IppoolListView.as_view(), name='ippoollist'),

    path('vlan/new/', views.NewVlanView.as_view(), name='newvlan'),
    path('vlan/list/', views.ListVlanView.as_view(), name='listvlan'),
]
