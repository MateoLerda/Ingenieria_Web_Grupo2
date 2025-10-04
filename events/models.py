from django.db import models
import os
from uuid import uuid4
from users.models import CustomUserModel
from django.core.validators import MaxValueValidator, MinValueValidator

def get_flyer_filename(instance, filename):
    base, ext = os.path.splitext(os.path.basename(filename))
    return f"event_flyers/{uuid4().hex}{ext.lower()}"

class Event(models.Model):
    name = models.CharField(max_length=120)
    city = models.CharField(max_length=80)
    state_province = models.CharField(max_length=80) # MANEJAMOS ESTADO O PROVINCIA SEGUN EL PAIS
    country = models.CharField(max_length=80)
    date = models.DateField()
    description = models.TextField()
    flyer = models.ImageField(upload_to=get_flyer_filename)
    created_by = models.ForeignKey(CustomUserModel, related_name='created_events', on_delete=models.CASCADE)
    available_tickets = models.PositiveIntegerField()  
    max_tickets_per_user = models.PositiveIntegerField(default=1)  

    REQUIRED_FIELDS = ['name', 'city', 'state_province', 'country', 'date', 'description', 'flyer', 'created_by']

    def __str__(self):
        return f'{self.name.upper()} - {self.country.upper()}'

def get_image_filename(instance, filename):
    filename = os.path.basename(filename)
    return f"event_images/{instance.event_id}/{filename}"

def get_video_filename(instance, filename):
    filename = os.path.basename(filename)
    return f"event_videos/{instance.event_id}/{filename}"

class EventImage(models.Model):
    event = models.ForeignKey(Event, related_name='images', on_delete=models.CASCADE)
    image_url = models.ImageField(upload_to=get_image_filename)

    def __str__(self):
        return f'Imagen de {self.event.name}'

class EventVideo(models.Model):
    event = models.ForeignKey(Event, related_name='videos', on_delete=models.CASCADE)
    video_url = models.FileField(upload_to=get_video_filename, blank=False)

    def __str__(self):
        return f'Video de {self.event.name}'
    
class EventSector(models.Model):
    sector_name = models.CharField(max_length=100)
    sector_inventory = models.PositiveIntegerField()  # pool de entradas disponibles por sector
    sector_price = models.DecimalField(max_digits=12, decimal_places=2) # cada sector va a tener un precio distinto
    event = models.ForeignKey(Event, related_name='sectors', on_delete=models.CASCADE)

class Purchase(models.Model):
    user = models.ForeignKey(CustomUserModel, related_name='purchases', on_delete=models.CASCADE)
    event_sector = models.ForeignKey(EventSector, related_name='purchases', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    purchase_date = models.DateTimeField(auto_now_add=True)