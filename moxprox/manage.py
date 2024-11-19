#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import signal

from websockify import WebSocketProxy
from multiprocessing import Process
from dashboard.back.domain import Domain

def custom_shutdown_handler(signum, frame):
    """
    Fonction appelée lorsque le serveur Django reçoit un signal d'arrêt (Ctrl+C ou autre).
    """
    print("\nSignal d'arrêt reçu. Exécution des tâches de nettoyage...")
    
    try:
        for key in Domain.websockify_pid.keys:
            Domain.websockify_pid["proxy"].terminate()

        print("Tâches de nettoyage terminées. Arrêt du serveur.")
    except Exception as e:
        print(f"Erreur lors de l'exécution des tâches de nettoyage : {e}")
    
    sys.exit(0)

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'moxprox.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    
    signal.signal(signal.SIGINT, custom_shutdown_handler )  # Ctrl+C
    signal.signal(signal.SIGTERM, custom_shutdown_handler)  # Arrêt système
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
