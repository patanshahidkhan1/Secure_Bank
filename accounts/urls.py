from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_page, name='home_page'),
    path('auth/', views.auth_page, name='auth_page'),
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('balance/', views.balance_view, name='balance_view'),
    path('deposit/', views.deposit_money, name='deposit_money'),
    path('withdraw/', views.withdraw_money, name='withdraw_money'),
    path('logout/', views.user_logout, name='user_logout'),
]