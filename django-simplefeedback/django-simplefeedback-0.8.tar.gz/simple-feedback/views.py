from rest_framework.generics import CreateAPIView, RetrieveAPIView
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAdminUser

from django.http import HttpResponse
import re
import json
from .serializers import TicketSerializer
from .models import Ticket

class TicketCreateAPIView(CreateAPIView):
    serializer_class = TicketSerializer

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.validated_data['user'] = self.request.user
        super(TicketCreateAPIView, self).perform_create(serializer)


class TicketMetaRetrieveView(RetrieveAPIView):
    serializer_class = TicketSerializer
    permission_classes = (IsAdminUser,)

    def get(self, request, *args, **kwargs):
        ticket = get_object_or_404(Ticket, id=kwargs.get('pk'))
        response = HttpResponse(json.dumps(ticket.meta, indent=4), content_type='application/json')
        response['Content-Disposition'] = 'attachment; filename={}.json'.format(re.sub(r'\s+', '_', ticket.subject))
        return response