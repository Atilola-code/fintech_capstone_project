from django.db import models
from user.models import User
from wallet_management.models import Wallet

# Create your models here.
 
class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('credit', 'Credit'),
        ('debit', 'Debit'),
        ('transfer', 'Transfer')

    )

    sender = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='sent_transactions', null=True, blank=True)
    receiver = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='received_transactions', null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    description = models.TextField(null=True, blank=True)
    transaction_time = models.DateTimeField(auto_now_add=True)


    def get_transaction_summary(self):
        if self.transaction_type == 'transfer':
        # Use first_name and last_name to identify users with fallback to email
            if self.sender and self.sender.user:  
                 sender_name = (f"{self.sender.user.first_name} {self.sender.user.last_name}".strip()
                    or self.sender.user.email)
            else:
                 sender_name = "Unknown Sender"

            if self.receiver and self.receiver.user:
                receiver_name = (f"{self.receiver.user.first_name} {self.receiver.user.last_name}".strip()
                    or self.receiver.user.email)
            else:
                receiver_name = "Unknown Receiver"
            return f"A sum of {self.amount} was transferred from: " f"{sender_name} to {receiver_name} at {self.transaction_time}"
        
        # For credit and debit, this will show type and amount
        return f"{self.transaction_type.title()} : {self.amount}"
    
    def __str__(self):
        return self.get_transaction_summary()

