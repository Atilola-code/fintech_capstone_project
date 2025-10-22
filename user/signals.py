from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.core.mail import send_mail
from .models import User
from django.utils import timezone
import time
from wallet_management.models import Wallet


@receiver(post_save, sender=User)
def send_welcome_email_with_wallet(sender, instance, created, **kwargs):
    # Send a welcome email to users with their wallet details immediately after they register.

        if not created: # Only send email when user is newly created
            return
        print("Signal triggered: Sending welcome email with account details...")

        wallet = None
        for _ in range(10):  # retry for ~2 seconds
            try:
                wallet = Wallet.objects.get(user=instance)
                break
            except Wallet.DoesNotExist:
                time.sleep(0.2)

        if not wallet:
            print("Wallet not found yet. Skipping email.")
            return
              
        recipient = instance.email
        first_name = instance.first_name
        last_name = instance.last_name
        full_name = f"{first_name} {last_name}"

        subject = "🎉 Welcome to SwiftBank Digital Banking 🎉"
        from_email =settings.EMAIL_HOST_USER
        to = [recipient]

        account_number = wallet.account_number
        balance = wallet.balance
        date_joined = timezone.localtime(instance.date_joined).strftime("%B %d, %Y")

        html_content = render_to_string("welcome.html",{
            "username": f"{full_name}",
            "description": "Your SwiftBank account has been successfully created. Here are your wallet details: 🚀",
            "account_number": account_number,
            "balance": balance,
            "date_joined": date_joined
            },
        )
        text_content = f"""Hello {first_name},\n\nWelcome to our Digital Banking Platform! 🎉\nYour account has been successfully created on {date_joined}.\nBelow are your wallet details:

        🏦 Account Number: {account_number}
        💰 Current Balance: ₦{balance}

        You can now start sending and receiving payments securely.
        SwiftBank — Fast. Safe. Reliable. 🚀  """

        # Create email
        msg = EmailMultiAlternatives(subject, text_content, from_email, to)
        msg.attach_alternative(html_content, "text/html")
        msg.send()

        print(f" Onboarding email sent successfully to {recipient}")


@receiver(post_save, sender=User)
def send_kyc_verification_email(sender, instance, **kwargs):
     if instance.KYC_status:  # When it is verified (True)
          subject ="KYC Verification Approved"
          message = (f"Hi, {instance.first_name}, your KYC verification has been successfully approved.")
          send_mail(subject, message, "support@swiftbank.com", [instance.email])
          
