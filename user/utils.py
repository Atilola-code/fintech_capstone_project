import random
import hashlib
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from django.core.mail import send_mail
from .models import EmailOTP

# 6-digit numeric code
def generate_numeric_code(length=6):
    start = 10**(length-1)
    end = 10**length - 1
    return str (random.randint(start, end))

def create_and_send_email_otp(user, subject= "Your verification code", ttl_minutes=15):
    code = generate_numeric_code(6)
    hashed = hashlib.sha256(code.encode()).hexdigest()
    expires_at = timezone.now() + timedelta(minutes=ttl_minutes)
    otp = EmailOTP.objects.create(user=user, code_hash=hashed, expires_at=expires_at)

    # Send email notification
    message = f"Your verification code is: {code}. It expires in {ttl_minutes} minutes."
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)
    return otp, code