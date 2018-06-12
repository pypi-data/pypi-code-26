from .models import SystemUserLog
from .json_utils import JsonUtils


class SystemUserLogMethodMixin:

    def __log(self, operation, model_class, json_data, model_create_user, model_update_user, model_id=None):
        """
        创建用户修改数据日志
        :param operation: 操作类型
        :param model_class: 实体类型【全路径】
        :param json_data: 实体json字符串
        :param model_create_user: 实体创建人
        :param model_update_user: 实体更新人
        :param model_id: 实体主键标识
        :return:
        """
        SystemUserLog.objects.create_log(
            operation=operation,
            model_class=model_class,
            json_data=json_data,
            model_create_user=model_create_user,
            model_update_user=model_update_user,
            model_id=model_id
        )

    def log_on_create(self, model_class, json_data, model_create_user, model_update_user, model_id=None):
        self.__log(
            operation=SystemUserLog.OPERATION_ADD,
            model_class=model_class,
            json_data=json_data,
            model_create_user=model_create_user,
            model_update_user=model_update_user,
            model_id=model_id
        )

    def log_on_update(self, model_class, json_data, model_create_user, model_update_user, model_id=None):
        self.__log(
            operation=SystemUserLog.OPERATION_UPDATE,
            model_class=model_class,
            json_data=json_data,
            model_create_user=model_create_user,
            model_update_user=model_update_user,
            model_id=model_id
        )

    def log_on_delete(self, model_class, json_data, model_create_user, model_update_user, model_id):
        self.__log(
            operation=SystemUserLog.OPERATION_DELETE,
            model_class=model_class,
            json_data=json_data,
            model_create_user=model_create_user,
            model_update_user=model_update_user,
            model_id=model_id
        )


class SystemUserLogMixin(SystemUserLogMethodMixin):
    """
    记录数据修改日志公共view

    继承该view即可对数据修改进行日志记录
    """

    # def __model_2_dict(self, model):
    #     """
    #     model to dict
    #     :return:
    #     """
    #     return dict([(attr, getattr(model, attr)) for attr in [field.name for field in model._meta.fields]])

    def log_create(self, model):
        """
        insert model logging
        :param model:
        :return:
        """
        json_data = JsonUtils.obj_2_json_str(model)
        super(SystemUserLogMixin, self).log_on_create(model_class=model.__class__,
                                                      json_data=json_data,
                                                      model_create_user=model.create_user,
                                                      model_update_user=model.create_user,
                                                      model_id=model.id)

    def log_update(self, model):
        """
        update model logging
        :param model:
        :param update_user:
        :return:
        """
        record_create_user = self.get_create_model_user(model.__class__, model.id)

        json_data = JsonUtils.obj_2_json_str(model)
        super(SystemUserLogMixin, self).log_on_update(model_class=model.__class__,
                                                      json_data=json_data,
                                                      model_create_user=record_create_user,
                                                      model_update_user=model.update_user,
                                                      model_id=model.id)

    def log_delete(self, model):
        """
        delete model logging
        :param model:
        :param update_user:
        :return:
        """
        record_create_user = self.get_create_model_user(model.__class__, model.id)

        json_data = JsonUtils.obj_2_json_str(model)
        super(SystemUserLogMixin, self).log_on_delete(model_class=model.__class__,
                                                      json_data=json_data,
                                                      model_create_user=record_create_user,
                                                      model_update_user=model.update_user,
                                                      model_id=model.id)

    def get_create_model_user(self, model_class, model_id):
        """
        查询创建实体的用户
        :param model_id:
        :param model_class:
        :return:
        """
        db_record = SystemUserLog.objects.get_model_create_user(model_class, model_id)
        if db_record:
            record_create_user = db_record.model_create_user
        else:
            record_create_user = None
        return record_create_user

    # def get_create_model_user(self, user_id):
    #     """
    #     获取model创建用户。子类需要重写该方法
    #     :param user_id:
    #     :return:
    #     """
    #     raise NotImplementedError
