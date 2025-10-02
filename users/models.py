from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import date

# Create your models here.
class CustomUserModel(AbstractUser):
    full_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    birth_date = models.DateField(null=True, blank=True)
    first_name = None
    last_name = None

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'full_name']

    class Meta:
        ordering = ['date_joined']

        
