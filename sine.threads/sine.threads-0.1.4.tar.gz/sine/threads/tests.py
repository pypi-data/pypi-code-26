import unittest
from core import *

def f1():
    pass

def f2(stop_event):
    pass

def f3(**kwargs):
    pass

run_last = 0.05
wait_exit = 1

class WhiteBox(unittest.TestCase):
    def test_parameter(self):
        def test(Thread, func, noerror):
            try:
                Thread(target=func)
            except ValueError as e:
                noerror = not noerror
            self.assertTrue(noerror)
        test(StoppableThread, f1, False)
        test(StoppableThread, f2, True)
        test(StoppableThread, f3, True)
        test(ReStartableThread, f1, False)
        test(ReStartableThread, f2, True)
        test(ReStartableThread, f3, True)

    def test_stop(self):
        def test(Thread):
            stopped = [False]
            def f(stop_event):
                while 1:
                    if stop_event.is_set():
                        break
                stopped[0] = True
            t = Thread(target=f)
            t.start()
            t.join(run_last)
            t.stop()
            t.join(wait_exit)
            self.assertTrue(stopped[0])
        test(StoppableThread)
        test(ReStartableThread)

    def test_restart(self):
        s = [0]
        def f(stop_event):
            s[0] += 1
            while 1:
                if stop_event.is_set():
                    break
            s[0] += 10

        t = ReStartableThread(target=f)
        t.start()
        t.join(run_last)
        self.assertEqual(s[0], 1)
        t.stop()
        t.join(wait_exit)
        self.assertEqual(s[0], 11)
        t.start()
        t.join(run_last)
        self.assertEqual(s[0], 12)
        t.stop()
        t.join(wait_exit)
        self.assertEqual(s[0], 22)


if __name__ == '__main__':
    unittest.main()
