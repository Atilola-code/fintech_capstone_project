from django.db import models
from user.models import User

# Create your models here.
class Wallet(models.Model):
    balance = models.DecimalField(max_digits=100, decimal_places=2)
    currency = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wallet')

