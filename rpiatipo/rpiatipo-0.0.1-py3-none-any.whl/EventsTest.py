from unittest import TestCase
from unittest.mock import patch, Mock
from rpiatipo.Events import Event, EventService

class EventsTest(TestCase):
    @patch('rpiatipo.Events.EventService')
    def setUp(self, MockEventService):
        self.event = Event(type="test", data={"data": 1})
        self.eventService = MockEventService()
        self.eventService.create.return_value = self.event
               
    def test_CreateEvent_EventService(self):
        response = self.eventService.create()
        self.assertIsInstance(response, Event)

    def test_GetIdEvent_Success_EventService(self):
        self.eventService.getId.side_effect = self.side_effect("1")
        response = self.eventService.getId()
        self.assertIsInstance(response, Event)

    def test_GetIdEvent_NotFound_EventService(self):
        self.eventService.getId.side_effect = self.side_effect("0")
        response = self.eventService.getId()
        self.assertNotIsInstance(response, Event)
    
    def side_effect(self, id):
            if (id=="1"):
                return [self.event]
            else:
                return None