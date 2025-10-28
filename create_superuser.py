#!/usr/bin/env python
"""
Script para crear un superuser en los contenedores con todos los datos necesarios.
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PartyFinder.settings')
django.setup()

from django.contrib.auth import get_user_model
from datetime import date

User = get_user_model()


def create_superuser():
    """
    Crea un superuser con datos completos si no existe.
    """
    # Obtener datos de variables de entorno con valores por defecto
    username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
    email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'status418@gmail.com')
    password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'Status418')
    full_name = os.environ.get('DJANGO_SUPERUSER_FULL_NAME', 'Admin User')
    birth_date_str = os.environ.get('DJANGO_SUPERUSER_BIRTH_DATE', '2003-07-03')
    
    # Convertir la fecha de string a date object
    try:
        birth_date = date.fromisoformat(birth_date_str)
    except ValueError:
        print(f"⚠️  Fecha de nacimiento inválida '{birth_date_str}', usando 2003-07-03")
        birth_date = date(2003, 7, 3)
    
    # Verificar si el usuario ya existe
    if User.objects.filter(username=username).exists():
        print(f"El superuser '{username}' ya existe")
        return
    
    # Crear el superuser
    try:
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            full_name=full_name,
            birth_date=birth_date
        )
        print(f"✅ Superuser creado exitosamente:")
        print(f"   Username: {username}")
        print(f"   Email: {email}")
        print(f"   Full Name: {full_name}")
        print(f"   Birth Date: {birth_date}")
        print(f"   Password: {'*' * len(password)}")
        
    except Exception as e:
        print(f"❌ Error al crear el superuser: {e}")
        import traceback
        traceback.print_exc()
        exit(1)


if __name__ == '__main__':
    print("🔧 Creando superuser...")
    create_superuser()
