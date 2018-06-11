from django.db import models
from django.utils.timezone import now
from yagura.sites.models import Site


WEBSITE_STATE_CHOICES = (
    ('OK', 'OK'),
    ('NG', 'NG'),
)


class Target(models.Model):
    """Monitoring target

    * For separation this app from sites-app
    """
    site = models.ForeignKey(
        Site, on_delete=models.CASCADE, related_name='targets')

    def __str__(self):
        return f"Target for {self.site.url}"


class TargetState(models.Model):
    """Website monitoring statement transition
    """
    target = models.ForeignKey(
        Target, on_delete=models.CASCADE, related_name='states')
    state = models.CharField(
        'State label', max_length=10, choices=WEBSITE_STATE_CHOICES)
    begin_at = models.DateTimeField(default=now)
    end_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True, auto_now=True)

    class Meta:
        unique_together = (
            ('target', 'begin_at', ),
        )
        ordering = ['begin_at']

    def __str__(self):
        return f"State for {self.target.site.url}" \
            " ({self.begin_at}-{self.end_at})"
