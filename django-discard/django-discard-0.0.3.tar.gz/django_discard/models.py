from django.db import models
from django.utils import timezone


class SoftDeletionQuerySet(models.QuerySet):
    def discard(self):
        return super(SoftDeletionQuerySet, self).update(discarded_at=timezone.now())

    def undiscard(self):
        return super(SoftDeletionQuerySet, self).update(discarded_at=None)

    def kept(self):
        return self.filter(discarded_at=None)

    def discarded(self):
        return self.exclude(discarded_at=None)

class SoftDeletionManager(models.Manager):
    def __init__(self, *args, **kwargs):
        super(SoftDeletionManager, self).__init__(*args, **kwargs)

    def get_queryset(self):
        return SoftDeletionQuerySet(self.model)

class DiscardableModel(models.Model):
    discarded_at = models.DateTimeField(blank=True, null=True)
    objects = SoftDeletionManager()

    class Meta:
        abstract = True

    def discard(self):
        self.discarded_at = timezone.now()
        self.save()

    def undiscard(self):
        self.discarded_at = None
        self.save()

    def is_discarded(self):
        return self.discarded_at != None

    def is_kept(self):
        return self.discarded_at == None