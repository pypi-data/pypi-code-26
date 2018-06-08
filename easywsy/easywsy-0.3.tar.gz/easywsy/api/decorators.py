from ..check.mixin import ChecksMixin, _check_attr_method_map


class APIDecorators(ChecksMixin):

    def check(self, fields):
        """
        Decorator aimed to map attributes with check methods
        that will then validate the values of those attributes.

        @param fields: List of attribute names the defined method will check
        @type  fields: list
        @return: Newly defined method
        @rtype : function
        """

        def check_dec(func):
            for f in fields:
                _check_attr_method_map[f] = func

            def func_wrapper(*method_args):
                return func(*method_args)
            return func_wrapper
        return check_dec
