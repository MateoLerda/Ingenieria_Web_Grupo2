from datetime import date
from django.shortcuts import render
from events.forms import EventForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect         
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from .models import Event, EventImage
import json
from django.http import JsonResponse

def home_view(request):
    return render(request, 'events/home.html')

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
        'events/events.html',
        {
            'events': page_obj, 
            'cities': cities,
            'q': q, 'city': city, 'date': date,
        }
    )

@login_required
def dashboard(request):
    return render(request, 'events/dashboard.html')

def event_detail(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    return render(request, 'events/event_detail.html', {'event': event})

@login_required
def create_event(request):
    if request.user.groups.filter(name="Event_Organizer").exists():
        today = date.today().isoformat()  
        if request.method == 'GET':
            form = EventForm()
            return render(request, 'events/create_event.html', {'form': form, 'today': today})
        elif request.method == 'POST':
            form = EventForm(request.POST, request.FILES)
            if form.is_valid():
                event = form.save(commit=False)
                event.created_by = request.user
                event.save()
                # Redirect to Step 2 with the new event_id
                return redirect('add_event_media', event_id=event.id)
            else:
                return render(request, 'events/create_event.html', {'form': form, 'today': today})
    else:
        return redirect('events')
    
@login_required
def add_event_media(request, event_id):
    if request.user.groups.filter(name="Event_Organizer").exists():
        event = get_object_or_404(Event, pk=event_id)
        if request.method == 'GET':
            return render(request, 'events/create_event_media.html', {
                'event': event,
                'flyer': getattr(event, 'flyer', None),
            })
        elif request.method == 'POST':
            media_files = request.FILES.getlist('media')
            images = [f for f in media_files if f.content_type and f.content_type.startswith('image/')]
            for img in images:
                event_image = EventImage()
                event_image.event = event
                event_image.image_url = img
                event_image.save()
            return render(request, 'events/event_detail.html', {'event': event})
    else:
        return redirect('events')
