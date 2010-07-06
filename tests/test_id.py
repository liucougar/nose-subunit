import warnings
import os

from tests import SubunitPluginTester, getTestPath

from nose.plugins.testid import TestId
from nose import SkipTest

import sunit

idfile = "testid.noseids"

def tearDownModule():
    if os.path.isfile(idfile):
        os.remove(idfile)

class TestTestId(SubunitPluginTester):
    plugins = [sunit.Subunit(),TestId()]
    args = ['--with-id','--id-file=%s' % idfile]
    suitepath = getTestPath('basic.py')
    idfilepresent = False
    def runTest(self):
        self.getFedSubunitServer()
        result = self.testResult
        self.assertEqual(result.testsRun, 3)
        self.assertEqual(len(result.errors), 1)
        self.assertEqual(len(result.failures), 1)
        self.assertTrue(os.path.isfile('testid.noseids'))
        TestTestId.idfilepresent = True

#this test has to run after the previous test finishes,
#so the class name has to be a string considered greater than the previous
#class.
#TODO: is there a better way to do this?
class TestTestIdLoopFailed(TestTestId):
    args = ['--id-file=%s' % idfile, '--failed']
    def runTest(self):
        if not TestTestId.idfilepresent:
            raise SkipTest('TestTestId failed')
        try:
            self.getFedSubunitServer()
            result = self.testResult
            self.assertEqual(result.testsRun, 2)
            self.assertEqual(len(result.errors), 1)
            self.assertEqual(len(result.failures), 1)
        finally:
            if os.path.isfile(idfile):
                os.remove(idfile)