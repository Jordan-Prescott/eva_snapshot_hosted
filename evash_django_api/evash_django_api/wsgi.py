"""
WSGI config for evash_django_api project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os, sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

sys.path.append(os.path.join(BASE_DIR, 'evash_django_api', 'evash_django_api'))
sys.path.append(os.path.join(BASE_DIR, 'venv', 'lib', 'python3.10', 'site-packages'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'evash_django_api.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
