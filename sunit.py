"""This plugin takes over all tests output to generate subunit-formated
output.
"""

from new import instancemethod
from testtools.content import Content, ContentType, TracebackContent
#can't name this file as subunit, otherwise the following line fails
from subunit import TestProtocolClient

from nose.plugins import Plugin
from nose.util import isclass
from nose.result import _exception_detail

class TextContent(Content):
    def __init__(self, value, acontenttype=None):
        if acontenttype is None:
            acontenttype = ContentType("text","plain")
        Content.__init__(self, acontenttype, lambda:value.encode("utf8"))

class SubunitTestResult(TestProtocolClient):
    def __init__(self, stream, descriptions, config=None,
                 errorClasses=None, useDetails=False):        
        if errorClasses is None:
            errorClasses = {}
        self.errorClasses = errorClasses
        if config is None:
            config = Config()
        self.config = config
        self.useDetails = useDetails
        self.stream = stream #this is to make multiprocess plugin happy
        TestProtocolClient.__init__(self, stream)
    
    def _getArgs(self, test, err):
        if self.useDetails:
            details = {"traceback":TracebackContent(err,test)}
            error=None
        else:
            error=err
            details = None
        
        return error, details

    def addError(self, test, err): #modified from nose/result.addError
        """Overrides normal addError to add support for
        errorClasses. If the exception is a registered class, the
        error will be added to the list for that class, not errors.
        """
        stream = self._stream #getattr(self, '_stream', None)
        ec, ev, tb = err

        for cls, (storage, label, isfail) in self.errorClasses.items():
            if isclass(ec) and issubclass(ec, cls):
                if isfail:
                    test.passed = False

                # Might get patched into a streamless result
                if stream is not None:
                    if not isfail:
                        reason = _exception_detail(err[1])
                        if reason:
                            if self.useDetails:
                                details = {"reason":TextContent(reason)}
                                reason = None
                            else:
                                details = None

                        self._addNonFailOutcome(label.lower(),test,reason=reason,details=details)
                return
        error, details = self._getArgs(test, err)
        TestProtocolClient.addError(self,test, error, details=details)

    def addFailure(self, test, err):
        error, details = self._getArgs(test, err)
        TestProtocolClient.addFailure(self,test, error, details=details)

    def _addNonFailOutcome(self, outcome, test, reason=None, details=None):
        """Report a non-failure error (such as skip)"""
        if reason is None:
            self._addOutcome(outcome, test, error=None, details=details)
        else:
            self._stream.write(outcome+": %s [\n" % test.id())
            self._stream.write("%s\n" % reason)
            self._stream.write("]\n")

    #the nose testrunner would call these two functions
    def printErrors(self, *args):
        pass
    def printSummary(self, *args):
        pass
    
class Subunit(Plugin):
    """Output test results in subunit format
    """
    
    name = 'subunit'
    #run before multiprocess plugin, otherwise prepareTestRunner 
    #won't be able to properly monkey patch runner
    score = 1100

    def configure(self, options, conf):
        if not self.can_configure:
            return
        Plugin.configure(self, options, conf)
        #detailedErrors is defined in failuredetail plugin
        try:
            self.useDetails = options.detailedErrors
        except:
            self.useDetails = False

    def prepareTestRunner(self, runner):
        #replace _makeResult in the default nose TestRunner to return
        #our implementation SubunitTestResult
        if not hasattr(runner, "_makeResult"):
            raise Exception("runner does not have _makeResult method, don't know how to attach to it.")
        
        runner.useDetails = self.useDetails
        def _makeResult(self):
            result = SubunitTestResult(self.stream,self.descriptions,
                self.config, useDetails=self.useDetails)
            return result
        runner._makeResult = instancemethod(_makeResult, runner, runner.__class__)
        return runner
