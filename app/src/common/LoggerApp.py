"""
Sistema de logging mejorado para la aplicación
Proporciona funciones para registrar información, advertencias y errores
"""
import os
from datetime import datetime
from django.conf import settings
from .AppLoggin import check_file, LOG_FILE_PATH


def log_info(user, url, file_name, message, request=None):
    """
    Registra un evento informativo
    
    Args:
        user: Usuario que realiza la acción
        url: URL de la petición
        file_name: Nombre del archivo/vista que genera el log
        message: Mensaje descriptivo
        request: Objeto request de Django (opcional)
    """
    check_file()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user_email = user.email if hasattr(user, 'email') else str(user)
    ip = get_client_ip(request) if request else "N/A"
    
    log_entry = (
        f"[{timestamp}] [INFO] "
        f"User: {user_email} | "
        f"IP: {ip} | "
        f"URL: {url} | "
        f"File: {file_name} | "
        f"Message: {message}\n"
    )
    
    with open(LOG_FILE_PATH, "a", encoding="utf-8") as file:
        file.write(log_entry)


def log_warning(user, url, file_name, message, request=None):
    """
    Registra una advertencia
    
    Args:
        user: Usuario que realiza la acción
        url: URL de la petición
        file_name: Nombre del archivo/vista que genera el log
        message: Mensaje descriptivo
        request: Objeto request de Django (opcional)
    """
    check_file()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user_email = user.email if hasattr(user, 'email') else str(user)
    ip = get_client_ip(request) if request else "N/A"
    
    log_entry = (
        f"[{timestamp}] [WARNING] "
        f"User: {user_email} | "
        f"IP: {ip} | "
        f"URL: {url} | "
        f"File: {file_name} | "
        f"Message: {message}\n"
    )
    
    with open(LOG_FILE_PATH, "a", encoding="utf-8") as file:
        file.write(log_entry)


def log_error(user, url, file_name, message, request=None):
    """
    Registra un error
    
    Args:
        user: Usuario que realiza la acción
        url: URL de la petición
        file_name: Nombre del archivo/vista que genera el log
        message: Mensaje descriptivo
        request: Objeto request de Django (opcional)
    """
    check_file()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user_email = user.email if hasattr(user, 'email') else str(user)
    ip = get_client_ip(request) if request else "N/A"
    
    log_entry = (
        f"[{timestamp}] [ERROR] "
        f"User: {user_email} | "
        f"IP: {ip} | "
        f"URL: {url} | "
        f"File: {file_name} | "
        f"Message: {message}\n"
    )
    
    with open(LOG_FILE_PATH, "a", encoding="utf-8") as file:
        file.write(log_entry)


def get_client_ip(request):
    """
    Obtiene la IP del cliente desde el request
    
    Args:
        request: Objeto request de Django
        
    Returns:
        str: Dirección IP del cliente
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
