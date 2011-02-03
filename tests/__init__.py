import unittest
from os import path

from nose.plugins import PluginTester
from subunit import TestProtocolServer

import sunit

from StringIO import StringIO

def getTestPath(t):
    return path.join(__path__[0], t) #path.dirname(__file__)

class ServerTestResult(unittest.TestResult):
    def __init__(self):
        unittest.TestResult.__init__(self)
        self.skips = []
        self.times = []
        self._progress = []
    def addSkip(self, test, error=None, details=None):
        self.skips.append((test,details or self._exc_info_to_string(error, test)))
    def addError(self, test, error=None, details=None):
        self.errors.append((test, details or self._exc_info_to_string(error, test)))
    def addFailure(self, test, error=None, details=None):
        self.failures.append((test, details or self._exc_info_to_string(error, test)))
    def progress(self, offset, whence):
        self._progress.append((offset, whence))
    def time(self, a_datetime):
        self.times.append(a_datetime)
    #def _exc_info_to_details(error, test):

class SubunitPluginTester(PluginTester, unittest.TestCase):
    activate = '--with-subunit'
    plugins = [sunit.Subunit()]
    def getFedSubunitServer(self):
        #subunit.TestProtocolServer would pass the output from 
        #the makeSuite test. the result of the parsing is in 
        #self.testResult (
        self.serverIO = StringIO()
        self.testResult = ServerTestResult()
        self.server = TestProtocolServer(self.testResult,self.serverIO)
        #print self.output,
        lastline = ""
        print self.output
        for line in self.output:
            self.server.lineReceived(line)
            if line.startswith("test:") and line==lastline:
                raise Exception('subunit output should not contain two consecutive identical lines starting with "tests:"')
            lastline = line

        return self.server
    #args = ['-s']
    #env = {'EVEN_FANCIER': '1'}
