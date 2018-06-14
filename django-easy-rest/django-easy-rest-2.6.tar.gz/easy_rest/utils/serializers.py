import json


class DynamicEncoder(json.JSONEncoder):

    def default(self, obj):
        if hasattr(obj, "serialize"):
            return obj.serialize()

        return (
            "Can't serialize object, in order to serialize it "
            "Declare a serialize method in your class"
        )
