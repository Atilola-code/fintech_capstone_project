from django.urls import path
from .views import (
    CreateTransactionView,
    TransactionHistoryView,
    TransactionDetailView,
    AdminTransactionListView
)

urlpatterns = [
    path('create/', CreateTransactionView.as_view(), name="create_transaction"),
    path("history/", TransactionHistoryView.as_view(), name="transaction-history"),
    path("<int:pk>/", TransactionDetailView.as_view(), name="transaction-detail"),
    path("admin/all/", AdminTransactionListView.as_view(), name="admin-transactions"),
]