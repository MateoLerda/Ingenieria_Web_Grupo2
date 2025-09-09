from django.contrib.auth.forms import UserCreationForm  
from django import forms

class CustomUserCreationForm(UserCreationForm):
    full_name = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        fields =  ('full_name', 'email') + UserCreationForm.Meta.fields