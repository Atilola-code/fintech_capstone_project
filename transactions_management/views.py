
# Create your views here.
from rest_framework import generics, permissions
from .models import Transaction
from .serializers import TransactionSerializer
from django.db.models import Q
from drf_spectacular.utils import extend_schema, OpenApiExample
from django_filters.rest_framework import DjangoFilterBackend
from user.permissions import CanTransact, IsAdmin
from rest_framework.pagination import PageNumberPagination

    
@extend_schema(
    tags=["Transactions"],
    summary="Create a new transaction",
    description=("Allows an authenticated user to perform a **credit**, **debit**,"
        "or **transfer** transaction.\n\n"
        "**Transfer:** Provide the receiver's account number.\n"
        "**Credit/Debit:** The sender is automatically detected from the logged-in user."
    ),
    request=TransactionSerializer,
    responses={201: TransactionSerializer, 400: dict},
    examples=[
        OpenApiExample(
            name="Transfer Transaction",
            description = "Send money to another user's wallet using their account number.",
            value={
                "receiver": 1234567890,
                "amount": 1000.00,
                "transaction_type": "transfer",
                "description": "string",
            },
        ),
        OpenApiExample(
            name="Credit Transaction",
            description="Add funds to your own wallet (like a top-up)",
            value={
                "amount": 2000.00,
                "transaction_type": "credit",
                "description": "Wallet top-up"
            },
        ),

        OpenApiExample(
            name="Debit Transaction",
            description="Deduct funds from your wallet (i.e purchase).",
            value={
                "amount": 500.00,
                "transaction_type": "debit",
                "description": "string"
            },
        ),
    ],
)
class CreateTransactionView(generics.CreateAPIView):
  
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated, CanTransact]

    def get_serializer_context(self):
        # pass request to serializer for wallet validation
        return {"request": self.request}


@extend_schema(
    tags=["Transactions"],
    summary="View all transactions related to the logged-in user",\
    description="Fetch a list of transaction related to your wallet (sent and received).",
    responses={200: TransactionSerializer(many=True)},
)
class TransactionHistoryView(generics.ListAPIView):

    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Transaction.objects.none()
        wallet = self.request.user.wallet
        return Transaction.objects.filter(Q(sender=wallet) | Q(receiver=wallet)).order_by("-transaction_time")


@extend_schema(
    tags=["Transactions"],
    summary="Retrieve a single transaction detail",
    description="View details of one transaction that involves your wallet by ID",
    responses={200: TransactionSerializer, 404: dict},
)
class TransactionDetailView(generics.RetrieveAPIView):

    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        wallet = self.request.user.wallet
        return Transaction.objects.filter(Q(sender=wallet) | Q(receiver=wallet))
    

class AdminTransactionPagination(PageNumberPagination):
    page_size = 10   
@extend_schema(
    tags=["Transactions"],
    summary="Admin-only: View all transactions in the system",
    description="List all transactions for administrative purposes. Requires admin privileges.",
    responses={200: TransactionSerializer(many=True)},
)

class AdminTransactionListView(generics.ListAPIView):
    queryset = Transaction.objects.all().order_by("-transaction_time")
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["transaction_type", "sender", "receiver"]
    search_fields = ["description"]
    ordering_fields = ["transaction_time", "amount"]
    pagination_class = AdminTransactionPagination

    def get_queryset(self):
        return Transaction.objects.all().order_by("-transaction_time")
