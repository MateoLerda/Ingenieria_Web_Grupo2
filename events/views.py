from datetime import date
from pyexpat.errors import messages
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
    only_available = request.GET.get('only_available', '') 

    qs = Event.objects.all()
    if q:
        qs = qs.filter(Q(name__icontains=q))
    if city:
        qs = qs.filter(city__icontains=city)
    if date:
        qs = qs.filter(date=date)
    if only_available:  
        qs = qs.filter(available_tickets__gt=0)

    paginator = Paginator(qs.order_by('-date'), 9)
    page_obj = paginator.get_page(request.GET.get('page'))

    cities = Event.objects.order_by().values_list('city', flat=True).distinct()

    return render(
        request,
        'events/events.html',
        {
            'events': page_obj, 
            'cities': cities,
            'q': q,
            'city': city,
            'date': date,
            'only_available': only_available
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
    
@login_required
def buy_tickets(request, event_id):
    event = get_object_or_404(Event, pk=event_id)

    if request.method == "POST":
        quantity = int(request.POST.get("quantity", 1))

        # Validaciones
        if quantity < 1 or quantity > event.max_tickets_per_user:
            messages.error(request, f"Solo puedes comprar entre 1 y {event.max_tickets_per_user} entradas.")
            return redirect("event_detail", event_id=event.id)

        if quantity > event.available_tickets:
            messages.error(request, "No hay suficientes entradas disponibles.")
            return redirect("event_detail", event_id=event.id)

        # Descontar entradas
        event.available_tickets -= quantity
        event.save()

        # Redirigir a página de éxito
        return redirect("purchase_success")

    return redirect("event_detail", event_id=event.id)

def purchase_success(request):
    return render(request, "events/purchase_success.html")

@login_required
def update_tickets(request, event_id):
    event = get_object_or_404(Event, pk=event_id)

    # Seguridad: solo el creador puede editar
    if event.created_by != request.user:
        return redirect("event_detail", event_id=event.id)

    if request.method == "POST":
        try:
            new_available = int(request.POST.get("available_tickets"))
            if new_available < 0:
                raise ValueError("Cantidad inválida")
            event.available_tickets = new_available
            event.save()
            return redirect("event_detail", event_id=event.id)
        except (ValueError, TypeError):
            # Si ponen algo inválido, vuelve al detalle
            return redirect("event_detail", event_id=event.id)

    return render(request, "events/update_tickets.html", {"event": event})