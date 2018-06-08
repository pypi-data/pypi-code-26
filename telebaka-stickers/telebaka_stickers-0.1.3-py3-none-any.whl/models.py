from django.db import models


class BotUser(models.Model):
    user_id = models.CharField(max_length=32)
    username = models.CharField(max_length=32, null=True)
    name = models.TextField()

    def __str__(self):
        return f'@{self.username}' if self.username else self.user_id


class BotUsage(models.Model):
    date = models.DateField()
    usages = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'{self.date} ({self.usages} usages)'
