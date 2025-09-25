from datetime import date
from django import forms
import re
from events.models import Event, EventImage, EventVideo

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['name', 'country', 'state_province', 'city', 'date', 'description', 'flyer']
        error_messages = {
            'name': {
                'required': 'Event name is required.',
            },
            'description': {
                'required': 'Event description is required.',
            },
            'country': {
                'required': 'Country is required.',
            },
            'state_province': {
                'required': 'State/Province is required.',
            },
            'city': {
                'required': 'City is required.',
            },
            'date': {
                'required': 'Event date is required.',
            },
            'flyer': {
                'required': 'Event flyer is required.',
            },
        }

    def clean_event_date(self): 
        event_date = self.cleaned_data.get('date')
        if event_date and event_date < date.today():
            raise forms.ValidationError('Event date cannot be in the past.')
        return event_date
