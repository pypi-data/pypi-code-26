from rest_framework import viewsets, permissions, routers
from django_user_images.models import Image
from .serializers import ImageSerializer


class ImageViewSet(viewsets.ModelViewSet):
    serializer_class = ImageSerializer
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Image.objects.all()

    def get_serializer_context(self):
        return {'owner': self.request.user}

    def filter_queryset(self, queryset):
        user = self.request.user
        return queryset.filter(owner=user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    class Meta:
        model = Image


router = routers.SimpleRouter()
router.register('images', ImageViewSet)

urlpatterns = router.urls
