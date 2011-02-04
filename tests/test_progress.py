import unittest
from tests import SubunitPluginTester, getTestPath
import sunit

from nose.plugins.multiprocess import MultiProcess

class TestParent(SubunitPluginTester):
    suitepath = getTestPath("../data/progress")
    firstProgress = 3
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
	self.assertEqual((self.firstProgress, 1), result._progress[0])

class TestParentNoPreload(TestParent):
    args = ['--no-preload']

class TestParentMultiProcess(TestParent):
    #enable MultiProcess nose plugin
    plugins = [sunit.Subunit(),MultiProcess()]
    args = ['--processes=2'] #enable 2 processes
    suitepath = getTestPath("../data/progress")

class TestParentMultiProcessNoPreload(TestParentMultiProcess):
    args = TestParentMultiProcess.args + ['--no-preload']

class TestDIR(TestParent):
    suitepath = getTestPath("../data/progress/tests")

class TestDIRNoPreload(TestDIR):
    args = ['--no-preload']
    firstProgress = 2
    def runTest(self):
    	TestDIR.runTest(self)
	self.assertEqual((1, 1), self.testResult._progress[1])

class TestDIRMultiProcess(TestParentMultiProcess):
    suitepath = getTestPath("../data/progress/tests")

class TestDIRMultiProcessNoPreload(TestDIRMultiProcess):
    args = TestDIRMultiProcess.args + ['--no-preload']
