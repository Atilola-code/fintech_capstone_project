from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Wallet
from .serializers import WalletSerializer
from rest_framework.permissions import AllowAny

# Create your views here.

class WalletManagement(APIView):
    permission_classes = [AllowAny]
    def get(self, request, id=None):
        if id:
            try:
                wallet_data = Wallet.objects.get(id=id)
            except Wallet.DoesNotExist:
                return Response({"message": "Wallet not found."}, status=status.HTTP_404_NOT_FOUND)
            serializer = WalletSerializer(wallet_data)
            return Response({"message": "Wallet information retrieved successfully.", "data": serializer.data}, status=status.HTTP_200_OK)
        
        # If no ID is provided, return all wallets
        wallets =  Wallet.objects.all()
        serializer = WalletSerializer(wallets, many=True)
        return Response({"message": "Wallet information retrieved successfully.", "data": serializer.data}, status=status.HTTP_200_OK)
    
    def post(self, request, id=None):
        wallet_data = request.data
        serializer = WalletSerializer(data=wallet_data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Wallet information created successfully."}, status=status.HTTP_201_CREATED)
        else:
            return Response({"message": "Invalid data provided.", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, id=None):
        try:
            wallet_data = Wallet.objects.get(id=id)
        except Wallet.DoesNotExist:
            return Response({"message": "Wallet not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = WalletSerializer(wallet_data, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Wallet information updated successfully."}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Invalid data provided.", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    def patch(self, request, id=None):
        try:
            wallet_data = Wallet.objects.get(id=id)
        except Wallet.DoesNotExist:
            return Response({"message": "Wallet not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = WalletSerializer(wallet_data, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Wallet information updated successfully."}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Invalid data provided.", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, id=None):
        try:
            wallet_data = Wallet.objects.get(id=id)
        except Wallet.DoesNotExist:
            return Response({"message": "Wallet does not exist."}, status=status.HTTP_404_NOT_FOUND)
        wallet_data.delete()
        return Response({"message": "Wallet information deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

