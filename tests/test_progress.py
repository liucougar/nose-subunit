import unittest
from tests import SubunitPluginTester, getTestPath
import sunit

from nose.plugins.multiprocess import MultiProcess

class TestProgressTestDIRParent(SubunitPluginTester):
    #enable MultiProcess nose plugin
    plugins = [sunit.Subunit(),MultiProcess()]
    #args = ['--processes=2'] #enable 2 processes
    #multiprocess can't load an inline testcase (created by makeSuite),
    #so suitepath has to be used
    suitepath = getTestPath("../data/progress")
    def runTest(self):
        self.getFedSubunitServer()
        result = self.testResult
        self.assertEqual(result.testsRun, 3)
        self.assertEqual(len(result.failures), 0)
        self.assertEqual(len(result.errors), 0)
        #make sure printSummary of the default TestResult is 
        #not being called
        self.assertFalse("----------" in self.output)
	#make sure progress is properly reported
	self.assertEqual((3, 1), result._progress[0])

class TestProgressTestDIR(TestProgressTestDIRParent):
    suitepath = getTestPath("../data/progress/tests")
