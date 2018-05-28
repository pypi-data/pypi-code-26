from django.conf.urls import url
from .views import TicketCreateAPIView, TicketMetaRetrieveView

urlpatterns = [
    url(r"^tickets/$", view=TicketCreateAPIView.as_view(), name="ticket-create"),
    url(r"^tickets/(?P<pk>\d+)/meta/$", view=TicketMetaRetrieveView.as_view(), name="ticket-meta-download"),

]
