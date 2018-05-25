from django.db import models


class PermittedRobotUser(models.Model):
    code = models.CharField(max_length=16)
    user_id = models.CharField(max_length=64)

    def __str__(self):
        return self.code
