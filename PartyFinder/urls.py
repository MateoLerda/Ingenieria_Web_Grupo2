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
from mainapp import views as main_views
from django.conf import settings
from django.conf.urls.static import static
from mainapp import views as v

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', main_views.home, name='home'),
    path('dashboard/', main_views.dashboard, name='dashboard'),
    path('accounts/signup/', main_views.signup_view, name='signup'),
    path('accounts/login/', main_views.login_view, name='login'),
    path('accounts/logout/', main_views.logout_view, name='logout'),
    path('events/<int:event_id>/', main_views.event_detail, name='event_detail'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
