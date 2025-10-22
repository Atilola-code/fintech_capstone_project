from django.urls import path
from .views import WalletManagement

urlpatterns = [
    path('retrieve/', WalletManagement.as_view(), name='wallet'),
    path('retrieve/detail/<int:id>/', WalletManagement.as_view(), name='wallet_detail'),

]