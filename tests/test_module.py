import unittest
import warnings

import sunit

from tests import SubunitPluginTester, getTestPath


class TestModule(SubunitPluginTester):
    '''test failures in setup_package could is properly captured'''
    suitepath = getTestPath("module")
    def runTest(self):
        self.getFedSubunitServer()
        result = self.testResult
        self.assertEqual(result.testsRun, 0)
        self.assertEqual(len(result.errors), 0)
        self.assertEqual(len(result.failures), 0)
        self.assertFalse("multipart" in self.output)
        self.assertTrue("raise Exception" in self.output)
        #make sure printSummary of the default TestResult is 
        #not being called
        self.assertFalse("----------" in self.output)

from nose.plugins.multiprocess import MultiProcess

class TestModuleWithMultiProcess(TestModule):
    '''make sure this works with multiprocess plugin as well'''
    plugins = [sunit.Subunit(), MultiProcess()]
    args = ['--processes=1'] #enable 2 processes