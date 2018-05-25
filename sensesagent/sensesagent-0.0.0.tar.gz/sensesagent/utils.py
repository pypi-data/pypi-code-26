class DictionaryUtility:
    """
    Utility methods for dealing with dictionaries.
    """
    @staticmethod
    def to_object(item):
        """
        Convert a dictionary to an object (recursive).
        """
        def convert(item): 
            if isinstance(item, dict):
                return type('jo', (), {k: convert(v) for k, v in item.items()})
            if isinstance(item, list):
                def yield_convert(item):
                    for index, value in enumerate(item):
                        yield convert(value)
                return list(yield_convert(item))
            else:
                return item

        return convert(item)


