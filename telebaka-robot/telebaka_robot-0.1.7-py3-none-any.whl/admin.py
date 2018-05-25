from django.contrib import admin

from telebaka_robot.models import PermittedRobotUser


@admin.register(PermittedRobotUser)
class PermittedRobotUserAdmin(admin.ModelAdmin):
    pass
