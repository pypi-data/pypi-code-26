from datetime import datetime

from django.conf import settings
from django.db import models


def get_model_class(model):
    """Return the qualified path to a model class"""
    return '{}.{}'.format(model.__module__, model.__qualname__)


class SystemUserLogManager(models.Manager):
    def create_log(self, operation, model_class, model_id, json_data, model_create_user,model_update_user):
        self.create(
            operation=operation,
            model_class=get_model_class(model_class),
            model_id=model_id,
            data=json_data,
            model_create_user=model_create_user,
            model_update_user=model_update_user,
        )

    def get_by_model_create_user(self, model_class, model_create_user):
        """
        根据实体的创建人查询所有修改日志
        :param model_class:
        :param model_create_user:
        :return:
        """
        return self.filter(model_create_user=model_create_user, model_class=get_model_class(model_class))

    def get_by_model_update_user(self, model_class, model_update_user):
        """
        根据实体的更新人查询所有修改日志
        :param model_class:
        :param model_update_user:
        :return:
        """
        return self.filter(model_update_user=model_update_user, model_class=get_model_class(model_class))

    def get_model_create_user(self, model_class, model_id):
        """
        获取创建记录的用户
        :param model_class:
        :return:
        """
        try:
            return self.get(model_class=get_model_class(model_class), operation='add', model_id=model_id)
        except:
            return None


class SystemUserLog(models.Model):
    """
    用户修改数据日志
    """
    OPERATION_ADD = 'add'
    OPERATION_DELETE = 'delete'
    OPERATION_UPDATE = 'update'
    OPERATION_CHOICES = (
        (OPERATION_ADD, '新增'),
        (OPERATION_DELETE, '删除'),
        (OPERATION_UPDATE, '修改'),
    )

    operation = models.CharField('操作类型', choices=OPERATION_CHOICES, max_length=10)
    model_class = models.CharField('实体类', max_length=64)
    model_id = models.CharField('实体主键标识', max_length=64, null=True, blank=True)
    data = models.TextField('数据内容', default='')
    model_create_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        related_name='log_model_create_user',
        on_delete=models.CASCADE,
        verbose_name='数据创建人'
    )
    model_update_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        related_name='log_model_update_user',
        on_delete=models.CASCADE,
        verbose_name='数据修改人'
    )

    create_time = models.DateTimeField('创建时间', default=datetime.now)

    objects = SystemUserLogManager()

    class Meta:
        ordering = ('create_time',)
        db_table = 'system_user_log'
        verbose_name = "用户修改数据日志"
        verbose_name_plural = verbose_name

