from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Wallet
from .serializers import WalletSerializer
from drf_spectacular.utils import extend_schema,OpenApiExample
from user.permissions import CanCreateWallet


@extend_schema(
    tags=["Wallet Management"],
    summary="Retrieve user wallet or specific wallet by ID and prevent deletion of user wallet",
    request=WalletSerializer,
    responses={
        200: WalletSerializer,
        400: dict,
        404: dict,
        405: dict
    },
    examples=[
        OpenApiExample(
            name="Get wallet info",
            description="Example response for fetching wallet details",
            value={
                "message": "Wallet information retrieved successfully.",
                "data": {
                    "id": 1,
                    "user": 3,
                    "balance": 1000.50,
                    "currency": "string",
                    "created_at": "2025-10-06T12:00:00Z"
                }
            }
        ),
    ]
)
class WalletManagement(APIView):
    permission_classes = [permissions.IsAuthenticated, CanCreateWallet]

    def get(self, request, id=None):
        # Retrieve wallet by ID or the logged-in user's wallet
        try:
            if id:
                # Admin can get any wallet by ID
                if request.user.is_staff:
                    wallet = wallet.objects.get(id=id)
                else:
                    wallet = Wallet.objects.get(id=id, user=request.user)
            else:
                # Otherwise, get their own wallet
                wallet = request.user.wallet
        except Wallet.DoesNotExist:
            return Response(
                {"message": "Wallet not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = WalletSerializer(wallet)
        return Response(
            {"message": "Wallet information retrieved successfully.", "data": serializer.data},
            status=status.HTTP_200_OK
            )

    
    def delete(self, request):
            """Block wallet deletion"""
            return Response(
                {"message": "Wallet deletion is not allowed."},
                status=status.HTTP_405_METHOD_NOT_ALLOWED
            )
