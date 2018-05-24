from django.conf import settings

GRAFANA_API_KEY = getattr(settings,'GRAFANA_API_KEY')
GRAFANA_API_HEADERS = getattr(settings,'GRAFANA_API_HEADERS')
GRAFANA_API_BASE_URL = getattr(settings,'GRAFANA_API_BASE_URL')