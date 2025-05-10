from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import CustomUser

User = get_user_model()

@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    """
    Signal to handle user profile updates
    """
    if created:
        # Log first time login
        instance.last_login = timezone.now()
        instance.save()

@receiver(post_save, sender=User)
def create_user_settings(sender, instance, created, **kwargs):
    """
    Signal to create user settings on user creation
    """
    if created:
        # Add any additional user settings initialization here
        pass

@receiver(post_save, sender=CustomUser)
def user_post_save(sender, instance, created, **kwargs):
    """Handle post-save actions for CustomUser"""
    if created:
        # Add any initialization code here
        pass