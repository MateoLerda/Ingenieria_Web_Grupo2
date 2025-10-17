from datetime import date
from django.contrib import messages
from django.shortcuts import render
from events.forms import EventForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect         
from django.core.paginator import Paginator
from django.db.models import Q, Case, When
from django.shortcuts import render, get_object_or_404
from .models import Event, EventImage, EventSector, Purchase
from django.db import transaction
from django.db.models import F, Sum
from haystack.query import SearchQuerySet
from haystack.inputs import AutoQuery
from django.core.management import call_command
from django.http import JsonResponse
from decimal import Decimal

def home_view(request):
    return render(request, 'events/home.html')

def event_list(request):
    """
    Lista de fiestas con filtros (q, city, date) y autocompletado de ciudades.
    Usa Whoosh/Haystack cuando el usuario aplica filtros (q, city o date);
    para el listado sin filtros usa el ORM.
    """
    q = request.GET.get('q', '').strip()
    city = request.GET.get('city', '').strip()
    date_val = request.GET.get('date', '').strip()
    only_available = request.GET.get('only_available', '')

    has_search_filters = bool(q or city or date_val)

    if has_search_filters:
        sqs = SearchQuerySet().models(Event)
        if q:
            sqs = sqs.filter(content=AutoQuery(q))
        if city:
            sqs = sqs.filter(city=city)
        if date_val:
            try:
                parsed_date = date.fromisoformat(date_val)
            except ValueError:
                parsed_date = None
            if parsed_date:
                sqs = sqs.filter(date=parsed_date)

        ids = [int(r.pk) for r in sqs]
        if ids:
            preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(ids)])
            qs = Event.objects.filter(pk__in=ids).order_by(preserved)
        else:
            qs = Event.objects.none()

        if only_available:
            qs = qs.filter(available_tickets__gt=0)
    else:
        qs = Event.objects.filter(date__gte=date.today()).order_by('-date')
        if only_available:
            qs = qs.filter(available_tickets__gt=0)

    paginator = Paginator(qs, 9)
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
            'date': date_val,
            'only_available': only_available,
        },
    )

@login_required
def dashboard(request):
    return render(request, 'events/dashboard.html')

def event_detail(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    sectors = event.sectors.all().order_by('sector_name')
    return render(request, 'events/event_detail.html', {'event': event, 'sectors': sectors})

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
                # Available tickets will be defined in Step 2 (sectors)
                event.available_tickets = 0
                event.created_by = request.user
                event.save()
                # Redirect to Step 2 (sectors) with the new event_id
                return redirect('add_event_sectors', event_id=event.id)
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
    


# Override manage_tickets with bulk edit version
@login_required
def manage_tickets(request, event_id):
    """Editar inventario y precio por sector en un solo formulario.
    Actualiza todo de forma atómica y recalcula el total disponible del evento.
    """
    event = get_object_or_404(Event, pk=event_id)
    if event.created_by != request.user:
        return redirect("event_detail", event_id=event.id)

    sectors = event.sectors.all().order_by('sector_name')
    if request.method == 'POST':
        from decimal import Decimal
        try:
            with transaction.atomic():
                locked = EventSector.objects.select_for_update().filter(event=event).order_by('pk')
                total = 0
                for s in locked:
                    inv_key = f'inv_{s.id}'
                    price_key = f'price_{s.id}'
                    try:
                        new_inv = int(request.POST.get(inv_key, s.sector_inventory))
                    except (TypeError, ValueError):
                        new_inv = s.sector_inventory
                    try:
                        new_price = Decimal(request.POST.get(price_key, s.sector_price) or s.sector_price)
                    except Exception:
                        new_price = s.sector_price

                    if new_inv < 0:
                        new_inv = 0
                    if new_price < 0:
                        new_price = Decimal('0')

                    if new_inv != s.sector_inventory or new_price != s.sector_price:
                        EventSector.objects.filter(pk=s.pk).update(
                            sector_inventory=new_inv,
                            sector_price=new_price,
                        )
                    total += new_inv

                Event.objects.filter(pk=event.pk).update(available_tickets=total)
            messages.success(request, 'Cambios guardados correctamente.')
        except Exception:
            messages.error(request, 'No se pudieron guardar los cambios. Intentá nuevamente.')
        return redirect('manage_tickets', event_id=event.id)

    return render(request, 'events/manage_tickets.html', { 'event': event, 'sectors': sectors })

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


# New implementation appended to enforce sector-based purchases and limits
@login_required
def buy_tickets(request, event_id):
    event = get_object_or_404(Event, pk=event_id)

    if request.method == "POST":
        try:
            quantity = int(request.POST.get("quantity", 1))
        except (TypeError, ValueError):
            quantity = 1
        sector_id = request.POST.get("sector_id")

        if not sector_id:
            messages.error(request, "Debes seleccionar un sector.")
            return redirect("event_detail", event_id=event.id)

        # Validaciones básicas
        if quantity < 1 or quantity > event.max_tickets_per_user:
            messages.error(request, f"Solo puedes comprar entre 1 y {event.max_tickets_per_user} entradas por compra.")
            return redirect("event_detail", event_id=event.id)

        with transaction.atomic():
            # Bloqueo de fila de sector para evitar carrera
            sector = get_object_or_404(EventSector.objects.select_for_update(), pk=sector_id, event=event)

            # Límite acumulado por usuario para el evento (en todos los sectores)
            already_bought = (
                Purchase.objects.filter(user=request.user, event_sector__event=event)
                .aggregate(total=Sum("quantity"))
                .get("total")
                or 0
            )
            if already_bought + quantity > event.max_tickets_per_user:
                remaining = max(event.max_tickets_per_user - already_bought, 0)
                if remaining == 0:
                    messages.error(request, "Ya alcanzaste el límite de entradas para este evento.")
                else:
                    messages.error(request, f"Solo puedes comprar {remaining} entrada(s) adicionales para este evento.")
                return redirect("event_detail", event_id=event.id)

            if sector.sector_inventory < quantity:
                messages.error(request, "No hay suficientes entradas disponibles en el sector seleccionado.")
                return redirect("event_detail", event_id=event.id)

            # Descontar inventario de forma atómica
            EventSector.objects.filter(pk=sector.pk).update(sector_inventory=F("sector_inventory") - quantity)
            Event.objects.filter(pk=event.pk).update(available_tickets=F("available_tickets") - quantity)

            # Registrar compra
            total_price = sector.sector_price * quantity
            Purchase.objects.create(
                user=request.user,
                event_sector=sector,
                quantity=quantity,
                total_price=total_price,
            )

        return redirect("purchase_success")

    return redirect("event_detail", event_id=event.id)


@login_required
def add_event_sectors(request, event_id):
    """Step 2: define default sectors and inventory/prices.
    Creates sectors +18, +21, +30 and updates available_tickets as the sum.
    """
    event = get_object_or_404(Event, pk=event_id)
    if event.created_by != request.user:
        return redirect('events')

    if request.method == 'GET':
        return render(request, 'events/create_event_sectors.html', { 'event': event })

    if request.method == 'POST':
        try:
            inv_18 = int(request.POST.get('inv_18', 0))
            inv_21 = int(request.POST.get('inv_21', 0))
            inv_30 = int(request.POST.get('inv_30', 0))
            price_18 = Decimal(request.POST.get('price_18', '0') or '0')
            price_21 = Decimal(request.POST.get('price_21', '0') or '0')
            price_30 = Decimal(request.POST.get('price_30', '0') or '0')
        except (TypeError, ValueError):
            messages.error(request, 'Valores inválidos para sectores.')
            return render(request, 'events/create_event_sectors.html', { 'event': event })

        sectors_data = [
            ('+18', inv_18, price_18),
            ('+21', inv_21, price_21),
            ('+30', inv_30, price_30),
        ]
        total = 0
        with transaction.atomic():
            # Eliminar sectores previos si se reconfigura
            event.sectors.all().delete()
            for name, inv, price in sectors_data:
                inv = max(int(inv or 0), 0)
                price = price if price >= 0 else Decimal('0')
                total += inv
                EventSector.objects.create(
                    event=event,
                    sector_name=name,
                    sector_inventory=inv,
                    sector_price=price,
                )
            Event.objects.filter(pk=event.pk).update(available_tickets=total)

        # Step 3: media
        return redirect('add_event_media', event_id=event.id)


@login_required
def manage_tickets(request, event_id):
    """Atomic add/remove inventory per sector to avoid race conditions."""
    event = get_object_or_404(Event, pk=event_id)
    if event.created_by != request.user:
        return redirect("event_detail", event_id=event.id)

    sectors = event.sectors.all().order_by('sector_name')
    if request.method == 'POST':
        sector_id = request.POST.get('sector_id')
        action = request.POST.get('action')  # 'add' or 'remove'
        try:
            amount = int(request.POST.get('amount', 0))
        except (TypeError, ValueError):
            amount = 0

        if not sector_id or amount <= 0 or action not in ('add', 'remove'):
            messages.error(request, 'Datos inválidos.')
            return redirect('manage_tickets', event_id=event.id)

        with transaction.atomic():
            sector = get_object_or_404(EventSector.objects.select_for_update(), pk=sector_id, event=event)
            if action == 'remove':
                # No permitir negativos
                if sector.sector_inventory < amount:
                    amount = sector.sector_inventory
                delta = -amount
            else:
                delta = amount

            EventSector.objects.filter(pk=sector.pk).update(sector_inventory=F('sector_inventory') + delta)
            Event.objects.filter(pk=event.pk).update(available_tickets=F('available_tickets') + delta)

        messages.success(request, 'Inventario actualizado correctamente.')
        return redirect('manage_tickets', event_id=event.id)

    return render(request, 'events/manage_tickets.html', { 'event': event, 'sectors': sectors })



def rebuild_index(request):
    from django.core.management import call_command
    try:
        call_command("rebuild_index", noinput=False)
        result = "Index rebuilt"
    except Exception as err:
        result = f"Error: {err}"

    return JsonResponse({"result": result})


def purchase_success(request):
    return render(request, "events/purchase_success.html")

