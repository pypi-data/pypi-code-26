from django.db import models


class Original(models.Model):
    href = models.URLField()
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    ready = models.BooleanField(default=False)

    def __str__(self):
        return self.href


class Rendition(models.Model):
    original = models.ForeignKey(Original)
    name = models.CharField(max_length=255)
    href = models.URLField()
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name
