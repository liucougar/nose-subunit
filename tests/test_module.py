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
        self.assertEqual(result.testsRun, 1)
        self.assertEqual(len(result.errors), 1)
        self.assertEqual(len(result.failures), 0)
        self.assertFalse("multipart" in self.output)
        self.assertTrue("raise Exception" in self.output)
        #make sure printSummary of the default TestResult is 
        #not being called
        self.assertFalse("----------" in self.output)
        print self.output

from nose.plugins.multiprocess import MultiProcess

class TestModuleWithMultiProcess(TestModule):
    '''make sure this works with multiprocess plugin as well'''
    plugins = [sunit.Subunit(), MultiProcess()]
    args = ['--processes=1'] #enable 2 processes

class TestImportError(SubunitPluginTester):
    suitepath = getTestPath("importerror.py")
    def runTest(self):
        self.getFedSubunitServer()
        result = self.testResult
        self.assertEqual(result.testsRun, 1)
        self.assertEqual(len(result.errors), 1)
        #make sure we don't see nose.failure.Failure.runTest
        self.assertFalse("nose.failure.Failure.runTest" in self.output)
        #instead we should see the name of the module
        self.assertTrue("tests.importerror" in self.output)