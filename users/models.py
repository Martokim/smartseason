from django.db import models
from django.contrib.auth.models import AbstractUser , UserManager

# Create your models here.

class CustomUserManager(UserManager):
    def create_superuser(self, username, email=None, password=None, **extra_fields):
        # Force role to ADMIN for every superuser
        extra_fields.setdefault('role', 'ADMIN')
        return super().create_superuser(username, email, password, **extra_fields)

class User(AbstractUser):
    ROLE_CHOICES =(
        ('ADMIN', 'Admin'),
        ('AGENT', 'Field Agent'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES,default='AGENT')

    objects = CustomUserManager()
    
    @property
    def is_admin(self):
        return self.role == 'ADMIN'

    @property
    def is_agent(self):
        return self.role == 'AGENT'

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
