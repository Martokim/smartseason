from django.db import models
from django.contrib.auth.models import AbstractUser 

# Create your models here.

class User(AbstractUser):
    ROLE_CHOICES =(
        ('ADMIN', 'Admin'),
        ('AGENT', 'Field Agent'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES,default='AGENT')
    @property
    def is_admin(self):
        return self.role == 'ADMIN'

    @property
    def is_agent(self):
        return self.role == 'AGENT'

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
