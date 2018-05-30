"""
Models that will define the table that stores the data of
the applications that are authorized to make requests.
"""
from django.db import models

# Create your models here.
class Applications(models.Model):
    """
    :field name: the name of the application that will make requests
    :field can_request: if the application has permissions to make requests
    """
    name = models.CharField(max_length=50, unique=True)
    can_request = models.BooleanField(default=True)

    def __str__(self):
        return self.name
