from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import UserManager
from django.utils import timezone
from django.conf import settings
import uuid, hashlib

# Create your user models here.

class User(AbstractUser):
    USER_ROLES = (
        ('customer', 'Customer'),
        ('merchant', 'Merchant'),
        ('admin', 'Admin'),
    )
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    username = None
    role = models.CharField(max_length=20, choices=USER_ROLES)
    KYC_status = models.BooleanField(default=False)
    phone = models.CharField(max_length=11, blank=True, null=True)  

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email
    

# Email otp model
class EmailOTP(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="email_otps")
    code_hash = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    idempotency_key = models.UUIDField(default=uuid.uuid4, editable=False)

    class Meta:
        indexes = [
            models.Index(fields=["user", "created_at"]),
        ]

    def verify(self, code: str) -> bool:
        # Return True if code matches and is not expired/used.
        if self.used or timezone.now() > self.expires_at:
            return False
        hashed = hashlib.sha256(code.encode()).hexdigest()
        return hashed == self.code_hash

    def mark_used(self):
        self.used = True
        self.save(update_fields=["used"])    
