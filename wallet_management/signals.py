from django.db.models.signals import post_save
from django.dispatch import receiver
from user.models import User
from .models import Wallet
from django.utils.crypto import get_random_string



@receiver(post_save, sender=User)
def create_wallet_for_new_user(sender, instance, created, **kwargs):

    # Create a wallet automatically when a new user is registered.
    if created and not hasattr(instance, 'wallet'):
        Wallet.objects.create(
            user=instance,
            currency="NGN"  #Default currency
        )

        print(f" Wallet created for {instance.email}")
