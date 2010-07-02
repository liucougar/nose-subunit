import unittest

class failure(unittest.TestCase):
    def runTest(self):
        self.assertTrue(False)
class success(unittest.TestCase):
    def runTest(self):
        assert True
class error(unittest.TestCase):
    def runTest(self):
        l=NoSuchVariable