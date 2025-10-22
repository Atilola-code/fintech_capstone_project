from rest_framework import serializers
from .models import Wallet

class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ["id", "user","balance","currency","created_at","updated_at", "account_number"]

        read_only_fields = ["id", "user", "created_at", "updated_at", "balance", "account_number"]

    def validate_currency(self, value):
        
        allowed_currencies = ["NGN", "USD", "EUR"]
        if value not in allowed_currencies:
            raise serializers.ValidationError(f"Currency must be one of: {', '.join(allowed_currencies)}")
        return value
    
    
