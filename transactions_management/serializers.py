from rest_framework import serializers
from .models import Transaction
from wallet_management.models import Wallet


class TransactionSerializer(serializers.ModelSerializer):
    sender = serializers.SlugRelatedField(slug_field="account_number", read_only=True)
    receiver = serializers.SlugRelatedField(slug_field="account_number", queryset=Wallet.objects.all(), required=False)
    summary = serializers.SerializerMethodField()
    current_balance = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = ['id', 'sender', 'receiver', 'amount', 'transaction_type', 'description', 'transaction_time', 'summary', 'current_balance']
        read_only_fields = ['id', 'transaction_time', 'summary', 'sender', 'current_balance']

    def get_summary(self, obj):
        return f" A {obj.transaction_type.title()} of {obj.amount} has been made for {obj.description}"
    
    def get_current_balance(self, obj):
        #Return the balance of the logged-in user's wallet after the transaction has been processed.
        request = self.context.get('request')
        if request and hasattr(request.user, 'wallet'):
            return request.user.wallet.balance
        return None

    def validate(self, attrs):
        request = self.context['request']
        user_wallet = request.user.wallet

        amount = attrs.get("amount")
        transaction_type = attrs.get("transaction_type")
        receiver_wallet = attrs.get("receiver")

        # Ensure minimum transaction amount
        if amount < 100:
            raise serializers.ValidationError({"amount": "Amount must be 100 and above"})
            
        if transaction_type == 'transfer':
            if not receiver_wallet:
                raise serializers.ValidationError({"receiver": "Receiver account is required for transfers."})
          
            if receiver_wallet == user_wallet:
                raise serializers.ValidationError({"receiver": "You cannot transfer to your own wallet."})
                
            if user_wallet.balance < amount:
                raise serializers.ValidationError({"balance": "Insufficient funds for this transfer. Try a lower amount."})
            
        # Debit Validation        
        if transaction_type == "debit" and user_wallet.balance < amount:
            raise serializers.ValidationError({"balance": "Insufficient funds for debit transaction."})
        return attrs
            
    def create(self, validated_data):
        request = self.context['request']
        user_wallet= request.user.wallet
        
        receiver_wallet = validated_data.get('receiver')
        amount = validated_data['amount']
        transaction_type = validated_data['transaction_type']

        sender_wallet = user_wallet if transaction_type in ['debit', 'transfer'] else None

      # Perform balance updates 
        if transaction_type == 'transfer':
            # Deduct from sender
            user_wallet.balance -= amount
            # Credit receiver
            receiver_wallet.balance += amount
            user_wallet.save()
            receiver_wallet.save()

        elif transaction_type == 'credit':
            user_wallet.balance += amount
            user_wallet.save()

        elif transaction_type == 'debit':
            if user_wallet.balance < amount:
                raise serializers.ValidationError({"balance": "insufficient funds for debit transaction."})
            user_wallet.balance -= amount
            user_wallet.save()

        # Save transaction record
        return Transaction.objects.create(
            sender = sender_wallet,
            receiver = receiver_wallet if transaction_type in ['credit', 'transfer'] else None,
            amount = amount,
            transaction_type = transaction_type,
            description = validated_data.get("description", "")
        )