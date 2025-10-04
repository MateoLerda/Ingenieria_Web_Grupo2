from haystack import indexes
from events.models import Event
import datetime

class EventIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    name = indexes.CharField(model_attr='name')
    date = indexes.DateField(model_attr='date')
    description = indexes.CharField(model_attr='description')
    city = indexes.CharField(model_attr='city')
    state_province = indexes.CharField(model_attr='state_province')
    country = indexes.CharField(model_attr='country')

    def get_model(self):
        return Event

    def index_queryset(self, using=None):
        """Index only future events, not past ones."""
        return self.get_model().objects.filter(date__gte=datetime.date.today())