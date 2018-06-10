from .models import Account


class AccountConverter(object):
    regex = '[0-9]+'

    def to_python(self, value):
        try:
            return Account.objects.get(**{'pk': value})
        except Account.DoesNotExist:
            """Doe's not silence MultipleObjectsReturned exception, that should be handled somewhere else"""
            return None

    def to_url(self, value):
        return f'{getattr(value, "pk")}'
