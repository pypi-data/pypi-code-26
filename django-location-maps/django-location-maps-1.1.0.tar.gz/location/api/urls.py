from rest_framework import routers

from ..views import CityViewSet, StateViewSet, CountryViewSet

router = routers.DefaultRouter()
router.register(r'cities', CityViewSet)
router.register(r'states', StateViewSet)
router.register(r'countries', CountryViewSet)