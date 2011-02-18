import unittest
from tests import SubunitPluginTester, getTestPath
import sunit

class TestGenerator(SubunitPluginTester):
    suitepath = getTestPath("generator.py")
    def runTest(self):
        self.getFedSubunitServer()
        result = self.testResult
        self.assertEqual(result.testsRun, 2)
        self.assertEqual(len(result.failures), 1)
        self.assertEqual(len(result.errors), 0)
        self.assertTrue("myfunc.pass" in self.output)
        self.assertTrue("myfunc.fail" in self.output)
        #make sure printSummary of the default TestResult is 
        #not being called
        self.assertFalse("----------" in self.output)
	#make sure progress is properly reported
	self.assertEqual((2, 1), result._progress[0])
