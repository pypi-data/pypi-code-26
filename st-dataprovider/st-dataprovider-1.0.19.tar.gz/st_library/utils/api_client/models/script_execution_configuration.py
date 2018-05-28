from st_library.utils.api_client import ApiClient
from st_library.utils.generics.base_object import BaseModel
from st_library.utils.helpers.store import Store


class ScriptExecutionConfiguration(BaseModel):
    def get_initial_data(self):
        return ApiClient.get(ApiClient.res.sec_get_detail(Store.config_id))

    def get_parameter_value(self, parameter_id):
        for parameter in self['parameters']:
            if parameter['id'] == parameter_id:
                return parameter['value']

        raise ValueError('Parameter {} does not exist'.format(parameter_id))
