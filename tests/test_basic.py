import unittest
import warnings

import sunit

from tests import SubunitPluginTester
class TestBasic(SubunitPluginTester):
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

    def makeSuite(self):
        #import pdb;pdb.set_trace()
        class failure(unittest.TestCase):
            def runTest(self):
                self.assertTrue(False)
        class success(unittest.TestCase):
            def runTest(self):
                assert True
        class error(unittest.TestCase):
            def runTest(self):
                l=NoSuchVariable
        return unittest.TestSuite([failure(),success(),error()])
        
    