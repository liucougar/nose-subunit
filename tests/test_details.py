import unittest
from tests import SubunitPluginTester
import sunit

from nose.plugins.failuredetail import FailureDetail
from nose.plugins.skip import Skip
from nose import SkipTest
from testtools.content import Content

class TestDetails(SubunitPluginTester):
    #enable FailureDetail nose plugin
    plugins = [sunit.Subunit(),FailureDetail(),Skip()]
    args = ['-d'] #enable FailureDetail, Skip is enabled by default
    def runTest(self):
        self.getFedSubunitServer()
        result = self.testResult
        self.assertEqual(result.testsRun, 2)
        self.assertEqual(len(result.failures), 1)
        self.assertEqual(len(result.errors), 0)
        self.assertEqual(len(result.skips), 1)
        self.assertTrue("multipart" in self.output)
        self.assertTrue(result.failures[0][1].has_key("traceback"))
        self.assertTrue(issubclass(result.failures[0][1]["traceback"].__class__, Content))
        #import pdb;pdb.set_trace()
        #print self.output,
        
    def makeSuite(self):
        class failuredetail(unittest.TestCase):
            def runTest(self):
                self.assertTrue(False)
        class skip(unittest.TestCase):
            def runTest(self):
                raise SkipTest()
        return unittest.TestSuite([failuredetail(), skip()])