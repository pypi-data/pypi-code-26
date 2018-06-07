from unittest import TestCase

from slerp.entity import Entity
from slerp.logger import logging
from slerp.app import db
log = logging.getLogger(__name__)


class Notification(db.Model, Entity):
	__tablename__ = 'notification'
	id = db.Column('notification_id', db.BigInteger, db.Sequence('notification_notification_id_seq'), primary_key=True)
	title = db.Column(db.String(100))
	message = db.Column(db.Text)
	
	def __init__(self, obj=None):
		Entity.__init__(self, obj)
		

class TestEntity(TestCase):
	def setUp(self):
		pass
	
	def test_to_dict(self):
		notification = Notification()
		notification.title = 'kiditz'
		notification.message = 'Jakarta'
		notification.id = 1
		print(notification.to_dict())
		
	def test_from_dict(self):
		notification = Notification({'title': 'Kiditz', 'message': 'Test'})
		print(notification.to_dict())