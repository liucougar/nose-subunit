import unittest
from tests import SubunitPluginTester
import sunit

from nose.plugins.failuredetail import FailureDetail
from testtools.content import Content

class TestDetails(SubunitPluginTester):
    #enable FailureDetail nose plugin
    plugins = [sunit.Subunit(),FailureDetail()]
    args = ['-d'] #enable FailureDetail
    def runTest(self):
        self.getFedSubunitServer()
        result = self.testResult
        self.assertEqual(result.testsRun, 1)
        self.assertEqual(len(result.failures), 1)
        self.assertTrue("multipart" in self.output)
        self.assertTrue(result.failures[0][1].has_key("traceback"))
        self.assertTrue(issubclass(result.failures[0][1]["traceback"].__class__, Content))
        #import pdb;pdb.set_trace()
        #print self.output,
        
    def makeSuite(self):
        class failuredetail(unittest.TestCase):
            def runTest(self):
                self.assertTrue(False)
        return unittest.TestSuite([failuredetail()])