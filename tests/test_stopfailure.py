import unittest
from tests import SubunitPluginTester, getTestPath

import sunit

class TestStopOnFailure(SubunitPluginTester):
    args = ["-x"]
    suitepath = getTestPath("stoponfailure.py")
    def runTest(self):
        #print self.output
        self.getFedSubunitServer()
        result = self.testResult
        self.assertEqual(result.testsRun, 1)
        self.assertEqual(len(result.failures), 1)

class TestStopOnError(SubunitPluginTester):
    args = ["-x"]
    suitepath = getTestPath("stoponerror.py")
    def runTest(self):
        #print self.output
        self.getFedSubunitServer()
        result = self.testResult
        self.assertEqual(result.testsRun, 1)
        self.assertEqual(len(result.errors), 1)