import requests

requests.post("http://127.0.0.1:8080/p", data={"a": 1, "b": 2}, files=[("abc.py", open("test_timer.py"))])