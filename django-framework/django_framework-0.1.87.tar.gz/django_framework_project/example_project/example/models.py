



from django_framework.django_helpers.model_helpers.model_registry import register_model

from django.db import models
from django_framework.django_helpers.model_helpers import BaseModel

from django_framework.django_helpers.model_helpers.model_fields import UnixEpochDateTimeField
from django_framework.django_helpers.model_helpers.model_fields import UnixEpochTimeField


class ExampleTable(BaseModel):

    a_time = UnixEpochTimeField(null = True, blank = True)
    
    a_date_time = UnixEpochDateTimeField(null = True, blank = True)
    
    
    class Meta:
        app_label = "example_project" # this name needs to match the app model it is going in!
#         db_table = "chaiappliance_appliance_prototype"


        

register_model(ExampleTable)  # this line is pretty important! it registers this model so it can be called properly

