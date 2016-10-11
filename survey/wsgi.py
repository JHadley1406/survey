"""
WSGI config for survey project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/howto/deployment/wsgi/
"""

import os, sys

sys.path.append('/home/public_html/survey/')
sys.path.append('/home/public_html/survey/survey')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "survey.settings")
from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
