# import threading
# from weakref import WeakSet
# import win32gui

# instances = WeakSet()

# class base(object):
#     def __new__(cls, *args, **kwargs):
#         instance = object.__new__(cls, *args, **kwargs)
#         instances.add(instance)
#         # if not thread.is_alive:
#         #     thread.start()
#         return instance

# def pump_messages():
#     while instances:
#         win32gui.PumpWaitingMessages()

# thread = threading.Thread(target=pump_messages, daemon=True)