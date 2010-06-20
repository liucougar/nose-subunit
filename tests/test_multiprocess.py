import unittest
from tests import SubunitPluginTester, getTestPath
import sunit

from nose.plugins.multiprocess import MultiProcess

class TestMultiProcess(SubunitPluginTester):
    #enable MultiProcess nose plugin
    plugins = [sunit.Subunit(),MultiProcess()]
    args = ['--processes=2'] #enable 2 processes
    #multiprocess can't load a inline testcase (created by makeSuite),
    #so suitepath has to be used
    suitepath = getTestPath("multiprocess.py")
    def runTest(self):
        self.getFedSubunitServer()
        result = self.testResult
        self.assertEqual(result.testsRun, 2)
        self.assertEqual(len(result.failures), 0)
        self.assertEqual(len(result.errors), 0)
        self.assertTrue("multiprocess.test1" in self.output)
        self.assertTrue("multiprocess.test2" in self.output)
        #make sure the multiprocess does use 2 processes to execute
        #the tests (time taken to execute two sleep(1) should be 
        #greate than 1 less than 2 seconds
        delta = result.times[-1]-result.times[0]
        self.assertEqual(delta.seconds,1)
        #make sure printSummary of the default TestResult is 
        #not being called
        self.assertFalse("----------" in self.output)