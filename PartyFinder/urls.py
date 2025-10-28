"""
URL configuration for PartyFinder project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from events import views as event_views
from users import views as user_views
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView


urlpatterns = [
    path('', event_views.home_view, name='home'),
    path('admin/', admin.site.urls),
    path('about/', TemplateView.as_view(template_name='events/about.html'), name='about'),
    path('events/', event_views.event_list, name='events'),
    path('events/create/', event_views.create_event, name='create_event'),
    path('events/create/<event_id>/sectors/', event_views.add_event_sectors, name='add_event_sectors'),
    path('events/create/<event_id>/cancel/', event_views.cancel_event_creation, name='cancel_event_creation'),
    path('events/create/<event_id>/media/', event_views.add_event_media, name='add_event_media'),
    path('accounts/signup/', user_views.signup_view, name='signup'),
    path('accounts/login/', user_views.login_view, name='login'),
    path('accounts/logout/', user_views.logout_view, name='logout'),
    path('accounts/', include('allauth.urls')), 
    path('events/<int:event_id>/', event_views.event_detail, name='event_detail'),
    #path('activate/<uidb64>/<token>/', user_views.activate_account, name='activate'),
    path("events/<int:event_id>/buy/", event_views.buy_tickets, name="buy_tickets"),
    path("events/<int:event_id>/update_tickets/", event_views.update_tickets, name="update_tickets"),
    path("events/<int:event_id>/manage_tickets/", event_views.manage_tickets, name="manage_tickets"),
    path("purchase_success/", event_views.purchase_success, name="purchase_success"),
    path('search/', include('haystack.urls')),
    path('rebuild_index/', event_views.rebuild_index, name='rebuild_index'),
     path("robots.txt", TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
