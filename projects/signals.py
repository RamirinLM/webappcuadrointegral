from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.core.mail import send_mail
from .models import UserProfile, Notification

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()

@receiver(post_save, sender=Notification)
def send_notification_email(sender, instance, created, **kwargs):
    if created and not instance.sent:
        # Send email to project creator or stakeholders
        recipients = [instance.project.created_by.email]
        send_mail(
            f'Alerta de Proyecto: {instance.alert_type}',
            instance.message,
            'your-email@gmail.com',
            recipients,
            fail_silently=True,
        )
        instance.sent = True
        instance.save()