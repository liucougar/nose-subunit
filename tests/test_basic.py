import unittest
import warnings

from tests import SubunitPluginTester, getTestPath

class TestBasic(SubunitPluginTester):
    suitepath = getTestPath('basic.py')
    def runTest(self):
        self.getFedSubunitServer()
        result = self.testResult
        self.assertEqual(result.testsRun, 3)
        self.assertEqual(len(result.errors), 1)
        self.assertEqual(len(result.failures), 1)
        self.assertFalse("multipart" in self.output)
        self.assertTrue("NoSuchVariable" in result.errors[0][1]["traceback"].iter_bytes()[0])
        self.assertTrue("self.assertTrue(False)" in result.failures[0][1]["traceback"].iter_bytes()[0])
        #make sure printSummary of the default TestResult is 
        #not being called
        self.assertFalse("----------" in self.output)
        
        #make sure progress is properly reported
	self.assertEqual((3, 1), result._progress[0])
    
