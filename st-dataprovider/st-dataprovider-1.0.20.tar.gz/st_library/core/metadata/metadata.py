from collections import defaultdict

from st_library import exceptions
from st_library.utils.api_client import ApiClient
from st_library.utils.api_client.models import ScriptExecutionConfiguration
from st_library.utils.helpers.store import Store


class Metadata(object):
    """
    A Category for work with metadata.

    """

    def __init__(self):
        self._script_execution_configurations = defaultdict(ScriptExecutionConfiguration)

    def get_parameter_value(self, parameter_id):
        """
        Get parameter value from the Script Execution Configuration

        Parameters
        ----------
        parameter_id : str

        Returns
        -------
        object
            The parameter value

        """
        return self._script_execution_configurations[Store.config_id].get_parameter_value(parameter_id)

    def set_performance_output_parameter_value(self, parameter_id, parameter_value):
        """
        Set output parameter to the Performance

        Parameters
        ----------
        parameter_id : str
        parameter_value : object

        Raises
        ------
        st_library.exceptions.PerformanceRequired
            If Performance is not defined for current Environment

        """
        if not Store.performance_id:
            raise exceptions.PerformanceRequired('Performance is not defined for current Environment')

        performance_id = Store.performance_id
        ApiClient.post(ApiClient.res.performance_output_parameter_post(parameter_id, performance_id),
                       json={'value': parameter_value})

    @property
    def script_execution_configurations(self):
        return self._script_execution_configurations


_METADATA = Metadata()
