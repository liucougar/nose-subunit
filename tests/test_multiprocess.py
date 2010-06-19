import unittest
from tests import SubunitPluginTester
import sunit

from nose.plugins.multiprocess import MultiProcess
from os import path

class TestMultiProcess(SubunitPluginTester):
    #enable MultiProcess nose plugin
    plugins = [sunit.Subunit(),MultiProcess()]
    args = ['--processes=2'] #enable 2 processes
    #multiprocess can't load a inline testcase (created by makeSuite),
    #so suitepath has to be used
    suitepath = path.join(path.dirname(__file__),"multiprocess.py")
    def runTest(self):
        self.getFedSubunitServer()
        result = self.testResult
        self.assertEqual(result.testsRun, 2)
        self.assertEqual(len(result.failures), 0)
        self.assertEqual(len(result.errors), 0)
        self.assertTrue("multiprocess.test1" in self.output)
        self.assertTrue("multiprocess.test2" in self.output)