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
        #make sure progress is properly reported
        self.assertTrue("progress: +2" in self.output)

class TestStopOnError(SubunitPluginTester):
    args = ["-x"]
    suitepath = getTestPath("stoponerror.py")
    def runTest(self):
        #print self.output
        self.getFedSubunitServer()
        result = self.testResult
        self.assertEqual(result.testsRun, 1)
        self.assertEqual(len(result.errors), 1)
        #make sure progress is properly reported
	self.assertEqual((2, 1), result._progress[0])
