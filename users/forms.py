from django import forms
from django.contrib.auth.forms import UserCreationForm
from users.models import CustomUserModel
import re

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUserModel
        fields = ['full_name', 'email', 'username', 'birth_date', 'password1', 'password2']
        error_messages = {
            'email': {
                'unique': 'A user with this email address already exists.',
                'invalid': 'Enter a valid email address.',
                'required': 'Email is required.',
            },
            'full_name': {
                'required': 'Full name is required.',
            },
        }

    def clean_full_name(self):
        full_name = self.cleaned_data.get('full_name') or ''
        if not re.match(r'^[A-Za-zÁÉÍÓÚáéíóúÑñüÜ\s]+$', full_name):
            raise forms.ValidationError('Full name can only contain alphabetic characters and spaces.')
        return full_name