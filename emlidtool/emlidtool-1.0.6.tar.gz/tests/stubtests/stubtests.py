class StubPassingTest():
    def run(self):
        return True

class StubFailingTest():
    def run(self):
        return False

class StubFailingTestWithException():
    def run(self):
        raise Exception("Test failed")
