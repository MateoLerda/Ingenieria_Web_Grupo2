
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect          # ← agrega redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm  # ← agrega esto

def home(request):
    return render(request, 'home.html')

@login_required(login_url='/accounts/login/')
def dashboard(request):
    return render(request, 'dashboard.html')

def signup(request): 
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})