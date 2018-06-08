from suds import sudsobject
from ..error.check_error import CheckError


_check_attr_method_map = {
}


class ChecksMixin(object):

    def _checkattrs(self, elem, no_check=[]):
        """
        Call check methods mapped to attrs `key` and raise if those fail.

        @param attrs: Dictionary of Attributes to Check
        @type  attrs: dict
        @param no_check: (Optional) Fields to avoid checking
        @type  no_check: list
        @return: None
        @rtype : NoneType
        @raise e: CheckError (Either Method was not found, or it failed)
        """
        for attr_name, attr_value in elem:
            if isinstance(attr_value, sudsobject.Object):
                self._checkattrs(attr_value, no_check=no_check)
            elif isinstance(attr_value, list):
                for s in attr_value:
                    self._checkattrs(s, no_check=no_check)
            else:
                if attr_name in no_check:
                    continue
                if attr_name not in _check_attr_method_map:
                    raise CheckError(attr=attr_name, not_found=True)
                method = _check_attr_method_map[attr_name]
                if not method(self, attr_value):
                    raise CheckError(attr=attr_name, method=method.func_name)
        return

    _check_attr_method_map = _check_attr_method_map
