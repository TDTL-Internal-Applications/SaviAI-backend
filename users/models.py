from django.db import models

from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('ceo',  'CEO'),
        ('chro','CHRO'),
        ('cfo', 'CFO'),
        ('cso', 'CSO'),
        ('cdo', 'CDO'),
        ('cmo', 'CMO'),  
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.username} - {self.role}"
