from urllib.parse import urlparse
from django.shortcuts import render
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.urls import is_valid_path
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.contrib import messages
from django.shortcuts import redirect
from utils.tokens import account_activation_token
from .forms import CustomUserCreationForm
from datetime import date
import re

# Create your views here.
def activate_account(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Thank you, your account has been activated successfully! Now you can log in.')
        return redirect('login')
    else:
        messages.error(request, 'Activation link is invalid!')
    return redirect('home')

def activateEmail(request, user, to_email, user_fullname):
    email_subject = "Activate your PartyFinder account!"
    current_site = get_current_site(request)
    domain = current_site.domain.rstrip('/')  
    message = render_to_string("users/email_confirmation.html", {
        'user': user_fullname,
        'domain': domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        "protocol": 'https' if request.is_secure() else 'http'
    })
    email = EmailMessage(email_subject, message, to=[to_email])
    if email.send():
        messages.info(request, f'Please confirm your email address to complete the registration. An activation link has been sent to {to_email}.')
    else:
        messages.warning(request, f'Error sending email to {to_email}. Please check if you typed it correctly or try again later.')

def signup_view(request): 
    if request.user.is_authenticated:
        return redirect('events')

    if request.method == 'GET':
        form = CustomUserCreationForm()
        return render(request, 'users/signup.html', {'form': form })
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            birth_date = form.cleaned_data.get('birth_date')
            today = date.today()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            if age < 18:
                messages.error(request, 'You must be at least 18 years old to register.')
                return render(request, 'users/signup.html', {'form': form })
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            activateEmail(request, user, form.cleaned_data.get('email'), form.cleaned_data.get('full_name'))
            return redirect('login')
        else:
            errors = form.errors
            if 'email' in errors:
                msg = errors['email'][0]
            else:
                first_key = next(iter(errors))
                msg = errors[first_key][0]
            messages.error(request, f"{msg}")
            return render(request, 'users/signup.html', {'form': form })
    

def login_view(request):
    next_url = request.GET.get('next', '/')
    if request.user.is_authenticated:
        return redirect(next_url)

    if request.method == 'GET':
        form = AuthenticationForm()
        return render(request, 'users/login.html', {'form': form, 'next': next_url})
    
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.POST.get('next', next_url)
            parsed_url = urlparse(next_url)
            if not parsed_url.netloc and is_valid_path(next_url):
                return redirect(next_url)
            return redirect('/events')
        else:
            messages.error(request, 'Invalid username or password.')
            return render(request, 'users/login.html', {'form': form, 'next': next_url})

def logout_view(request):
    logout(request)
    return redirect('events')
