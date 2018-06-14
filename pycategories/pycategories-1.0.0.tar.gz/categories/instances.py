import inspect


def make_getter(instances, name):
    def getter(type):
        for cls in inspect.getmro(type):
            if cls in instances:
                return instances[cls]
        raise TypeError("No instance for ({} {})".format(name, type))

    return getter


def make_adder(instances):
    def adder(type, instance):
        instances[type] = instance

    return adder


def make_undefiner(instances):
    def undefiner(type):
        for cls in inspect.getmro(type):
            if cls in instances:
                del instances[cls]

    return undefiner
