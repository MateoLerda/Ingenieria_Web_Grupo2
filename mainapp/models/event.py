from django.db import models

class Event(models.Model):
    name = models.CharField(max_length=120)
    city = models.CharField(max_length=80)
    country = models.CharField(max_length=80)
    date = models.DateField()
    description = models.TextField()

    def __str__(self):
        return f'{self.name} - {self.city}, {self.country}'


def get_image_filename(instance, filename):
        id = instance.event.id
        return "event_images/%s" % (id)

class EventImage(models.Model):
    event = models.ForeignKey(Event, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to=get_image_filename)

    def __str__(self):
        return f'Imagen de {self.event.name}'

