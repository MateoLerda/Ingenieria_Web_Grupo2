from django.contrib import admin

# CON ESTO EL ADMIN HACE FIESTAS RANDOM (CREO) HAY QUE PROBAR PERO NOSE
from .models import Party, PartyImage

class PartyImageInline(admin.TabularInline):
    model = PartyImage
    extra = 1

@admin.register(Party)
class PartyAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'date')
    list_filter = ('city', 'date')
    search_fields = ('name', 'city', 'description')
    inlines = [PartyImageInline]

@admin.register(PartyImage)
class PartyImageAdmin(admin.ModelAdmin):
    list_display = ('party', 'caption')
