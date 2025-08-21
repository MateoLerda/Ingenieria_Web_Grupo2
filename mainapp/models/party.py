from django.db import models

class Party(models.Model):
    name = models.CharField(max_length=120)
    city = models.CharField(max_length=80)
    date = models.DateField()
    description = models.TextField(blank=True)
    cover = models.ImageField(upload_to='parties/covers/', blank=True, null=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f'{self.name} - {self.city}'


class PartyImage(models.Model):
    party = models.ForeignKey(Party, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='parties/gallery/')
    caption = models.CharField(max_length=120, blank=True)

    def __str__(self):
        return f'Imagen de {self.party.name}'

