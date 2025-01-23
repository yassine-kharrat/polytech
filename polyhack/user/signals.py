from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User
from teachers.models import Teacher
from students.models import Student

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:  # only when user is created, not updated
        if instance.user_type == 'teacher':
            Teacher.objects.create(
                user=instance,
                name=instance.name
            )
        elif instance.user_type == 'student':
            Student.objects.create(
                user=instance,
                name=instance.name
            ) 