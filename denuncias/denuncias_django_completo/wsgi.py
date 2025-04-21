
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'denuncias_django_completo.settings')
application = get_wsgi_application()
