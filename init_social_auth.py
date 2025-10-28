#!/usr/bin/env python
"""
Script de inicialización para django-allauth.
Crea Sites y SocialApps necesarios para evitar errores en login/signup en los contenedores.
Setea credenciales dummy si no se proporcionan las reales para los providers de OAuth.
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PartyFinder.settings')
django.setup()

from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp


def init_sites():
    """
    Crea o actualiza el Site principal.
    """    
    from django.conf import settings
    site_id = getattr(settings, 'SITE_ID', 1)
    
    site, created = Site.objects.get_or_create(
        id=site_id,
        defaults={
            'domain': os.environ.get('SITE_DOMAIN', 'localhost:8000'),
            'name': os.environ.get('SITE_NAME', 'PartyFinder')
        }
    )
    
    if not created:
        site.domain = os.environ.get('SITE_DOMAIN', site.domain)
        site.name = os.environ.get('SITE_NAME', site.name)
        site.save()
        print(f"Site actualizado: {site.name} ({site.domain})")
    else:
        print(f"Site creado: {site.name} ({site.domain})")
    
    return site


def init_social_apps(site):
    """
    Crea o actualiza los SocialApps (Google, Twitter).
    Si no hay credenciales, crea providers dummy deshabilitados.
    """
    # Configuración para Google
    google_client_id = os.environ.get('GOOGLE_CLIENT_ID', '')
    google_secret = os.environ.get('GOOGLE_CLIENT_SECRET', '')
    
    if google_client_id and google_secret:
        # Crear Google provider real
        google_app, created = SocialApp.objects.get_or_create(
            provider='google',
            defaults={
                'name': 'Google OAuth',
                'client_id': google_client_id,
                'secret': google_secret,
            }
        )
        
        if not created:
            # Actualizar si ya existe
            google_app.client_id = google_client_id
            google_app.secret = google_secret
            google_app.save()
            print(f"✅ Google OAuth actualizado")
        else:
            print(f"✅ Google OAuth creado")
        
        # Asociar con el site
        if site not in google_app.sites.all():
            google_app.sites.add(site)
            print(f"   ↳ Asociado con site: {site.name}")
    else:
        # Crear Google provider dummy deshabilitado
        google_app, created = SocialApp.objects.get_or_create(
            provider='google',
            defaults={
                'name': 'Google OAuth (Placeholder)',
                'client_id': 'placeholder_google_client_id',
                'secret': 'placeholder_google_secret',
            }
        )
        
        if created:
            print("Google OAuth creado como placeholder (sin credenciales)")
            google_app.sites.add(site)
        else:
            print("Google OAuth ya existe")
    
    # Configuración para Twitter
    twitter_client_id = os.environ.get('TWITTER_CLIENT_ID', '')
    twitter_secret = os.environ.get('TWITTER_CLIENT_SECRET', '')
    
    if twitter_client_id and twitter_secret:
        # Crear Twitter provider real
        twitter_app, created = SocialApp.objects.get_or_create(
            provider='twitter',
            defaults={
                'name': 'Twitter OAuth',
                'client_id': twitter_client_id,
                'secret': twitter_secret,
            }
        )
        
        if not created:
            # Actualizar si ya existe
            twitter_app.client_id = twitter_client_id
            twitter_app.secret = twitter_secret
            twitter_app.save()
            print("Twitter OAuth actualizado")
        else:
            print("Twitter OAuth creado")
        
        # Asociar con el site
        if site not in twitter_app.sites.all():
            twitter_app.sites.add(site)
            print("Asociado con site: {site.name}")
    else:
        # Crear Twitter provider dummy deshabilitado
        twitter_app, created = SocialApp.objects.get_or_create(
            provider='twitter',
            defaults={
                'name': 'Twitter OAuth (Placeholder)',
                'client_id': 'placeholder_twitter_client_id',
                'secret': 'placeholder_twitter_secret',
            }
        )
        
        if created:
            print(f"Twitter OAuth creado como placeholder (sin credenciales)")
            # Asociar con el site
            twitter_app.sites.add(site)
        else:
            print(f"Twitter OAuth ya existe")


def main():
    """
    Función principal del script.
    """
    try:
        # Inicializar sites
        site = init_sites()
        
        # Inicializar social apps
        init_social_apps(site)
        
        print("✅ Inicialización completada exitosamente")
        
    except Exception as e:
        print(f"❌ Error durante la inicialización: {e}")
        import traceback
        traceback.print_exc()
        exit(1)


if __name__ == '__main__':
    main()
