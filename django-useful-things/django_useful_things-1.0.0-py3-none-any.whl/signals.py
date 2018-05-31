from django.db.models.signals import ModelSignal

pre_safe_delete = ModelSignal(providing_args=["instance", "using"], use_caching=True)
post_safe_delete = ModelSignal(providing_args=["instance", "using"], use_caching=True)
