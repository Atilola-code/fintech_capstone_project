from django.urls import path
from .views import WalletManagement

urlpatterns = [
    path('endpoint/', WalletManagement.as_view(), name='wallet_list_create'),
    path('endpoint/<int:id>/', WalletManagement.as_view(), name='wallet_detail_update_delete'),

]