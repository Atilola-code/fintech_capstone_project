import random
from django.db import models
from user.models import User
from decimal import Decimal
from django.core.validators import MinValueValidator

    

# Create your models here.
class Wallet(models.Model):
    CURRENCY_CHOICES = [
        ("NGN", "Nigerian Naira"),
        ("USD", "US Dollar"),
        ("EUR", "Euro"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wallet')
    account_number = models.CharField(max_length=10, unique=True, editable=False, null=False, blank=False)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), validators=[MinValueValidator(Decimal('0.00'))])
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default="NGN")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.account_number:
            self.account_number = self.generate_account_number()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_account_number():
        while True:
            acct_number = str(random.randint(10**9, 10**10 - 1))
            if not Wallet.objects.filter(account_number=acct_number).exists():
                return acct_number
            
    def credit(self, amount):
        self.balance += Decimal(amount)
        self.save(update_fields=['balance'])

    def debit(self, amount):
        if self.balance < Decimal(amount):
            raise ValueError("Insufficient funds in wallet.")
        self.balance -= Decimal(amount)
        self.save(update_fields=['balance'])
            
    def __str__(self):
        return f"{self.user.email} - {self.account_number}"
    
    class Meta:
        verbose_name = "Wallet"
        verbose_name_plural = "Wallets"
        ordering = ['-created_at']
