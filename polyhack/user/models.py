from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, email, name, password=None, user_type='student'):
        if not email:
            raise ValueError("The Email field must be set")
        if not user_type:
            raise ValueError("User type must be specified")
        
        email = self.normalize_email(email)
        user = self.model(
            email=email, 
            name=name, 
            user_type=user_type
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password):
        user = self.create_user(
            email=email,
            name=name,
            password=password,
            user_type='admin'  # Superusers are admin type
        )
        user.is_admin = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser):
    USER_TYPE_CHOICES = [
        ('teacher', 'Teacher'),
        ('student', 'Student'),
        ('admin', 'Admin'),
    ]
    
    name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    user_type = models.CharField(
        max_length=50, 
        choices=USER_TYPE_CHOICES,
        default='student'
    )
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return f"{self.name} ({self.email})"

    @property
    def is_staff(self):
        return self.is_admin

    @property
    def is_teacher(self):
        return self.user_type == 'teacher'

    @property
    def is_student(self):
        return self.user_type == 'student'
