from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect         
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from django.urls import is_valid_path
from urllib.parse import urlparse
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from .models import Event, CustomUserCreationForm
from .utils.tokens import account_activation_token


def home_view(request):
    return render(request, 'home.html')

def event_list(request):
    """
    Lista de fiestas con filtros (q, city, date) y autocompletado de ciudades.
    """
    q = request.GET.get('q', '').strip()
    city = request.GET.get('city', '').strip()
    date = request.GET.get('date', '').strip() 

    qs = Event.objects.all()
    if q:
        qs = qs.filter(Q(name__icontains=q))
    if city:
        qs = qs.filter(city__icontains=city)
    if date:
        qs = qs.filter(date=date)

    paginator = Paginator(qs.order_by('-date'), 9)
    page_obj = paginator.get_page(request.GET.get('page'))

    cities = Event.objects.order_by().values_list('city', flat=True).distinct()

    return render(
        request,
        'events.html',
        {
            'events': page_obj, 
            'cities': cities,
            'q': q, 'city': city, 'date': date,
        }
    )

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')

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
    message = render_to_string("registration/email_confirmation.html", {
        'user': user_fullname,
        'domain': domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        "protocol": 'https' if request.is_secure() else 'http'
    })
    email = EmailMessage(email_subject, message, to=[to_email])
    if email.send():
        messages.success(request, f'Please confirm your email address to complete the registration. An activation link has been sent to {to_email}.')
    else:
        messages.error(request, f'Error sending email to {to_email}. Please check if you typed it correctly or try again later.')

def signup_view(request): 
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            User = get_user_model()
            email = form.cleaned_data.get('email')
            if User.objects.filter(email=email).exists():
                messages.error(request, 'A user with this email address already exists.')
                return render(request, 'registration/signup.html', {'form': form})
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            activateEmail(request, user, form.cleaned_data.get('email'), form.cleaned_data.get('full_name'))
            return redirect('login')
        else:
            messages.error(request, 'Unsuccessful registration. Invalid information.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

def login_view(request):
    next_url = request.GET.get('next', '/')
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
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form, 'next': next_url})

def logout_view(request):
    logout(request)
    return redirect('events')

def event_detail(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    return render(request, 'event_detail.html', {'event': event})
