import unittest
from tests import SubunitPluginTester

import sunit

from nose.plugins.skip import Skip
from nose import SkipTest

class TestSkip(SubunitPluginTester):
    #enable skip nose plugin, skip is auto-enabled, so no
    #need to add other args
    plugins = [sunit.Subunit(), Skip()]
    def runTest(self):
        self.getFedSubunitServer()
        result = self.testResult
        self.assertEqual(result.testsRun, 1)
        self.assertEqual(len(result.skips), 1)
        self.assertFalse("multipart" in self.output)
    def makeSuite(self):
        class skip(unittest.TestCase):
            def runTest(self):
                raise SkipTest("skip test")
        return unittest.TestSuite([skip()])