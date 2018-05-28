def get_null_value(value):
    """Gets None from null token"""
    if value.lower().strip(' ') == "null":
        return None
    else:
        return value
