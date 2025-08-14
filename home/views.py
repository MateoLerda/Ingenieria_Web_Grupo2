from django.shortcuts import render

def home(request):
    return render(request, 'home.html', {'mensaje': "Hola Mundo"})