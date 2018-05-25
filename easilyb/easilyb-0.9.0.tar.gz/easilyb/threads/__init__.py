import threading


def threaded(func, args, daemon=False):
    t = threading.Thread(target=func, args=args)
    t.setDaemon(daemon)
    t.start()
    return t
