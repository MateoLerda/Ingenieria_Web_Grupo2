from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect         
from django.contrib.auth.forms import UserCreationForm  
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.urls import is_valid_path
from urllib.parse import urlparse
from django.http import HttpResponseRedirect


def home(request):
    return render(request, 'home.html')

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')

def signup_view(request): 
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  
    else:
        form = UserCreationForm()
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
            return redirect('/')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form, 'next': next_url})

def logout_view(request):
    logout(request)
    return redirect('home')

from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from .models import Party

def party_list(request):
    q = request.GET.get('q', '').strip()
    city = request.GET.get('city', '').strip()
    date = request.GET.get('date', '').strip()  # YYYY-MM-DD

    qs = Party.objects.all()
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(description__icontains=q))
    if city:
        qs = qs.filter(city__icontains=city)
    if date:
        qs = qs.filter(date=date)

    paginator = Paginator(qs, 6)
    parties = paginator.get_page(request.GET.get('page'))

    cities = Party.objects.order_by().values_list('city', flat=True).distinct()
    return render(request, 'parties/list.html', {
        'parties': parties, 'cities': cities, 'q': q, 'city': city, 'date': date
    })

def party_detail(request, pk):
    party = get_object_or_404(Party, pk=pk)
    return render(request, 'parties/detail.html', {'party': party})

