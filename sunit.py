"""This plugin takes over all tests output to generate subunit-formated
output.
"""

#can't name this file as subunit, otherwise the following line fails
from testtools.content import Content, ContentType, TracebackContent
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

class Subunit(Plugin):
    """Output test results in subunit format
    """
    
    name = 'subunit'
    score = 2 # run late

    def configure(self, options, conf):
        if not self.can_configure:
            return
        Plugin.configure(self, options, conf)
        #detailedErrors is defined in failuredetail plugin
        try:
            self.useDetails = options.detailedErrors
        except:
            self.useDetails = False

    def prepareTestResult(self, result):
        #import pdb;pdb.set_trace()
        if isinstance(result,SubunitTestResult):
            return
        newresult = SubunitTestResult(result.stream,result.descriptions,
            result.config, result.errorClasses, useDetails=self.useDetails)
        for f in TestProtocolClient.__dict__.keys():
            if callable(getattr(TestProtocolClient,f)) and f[0]!="_":
                setattr(result,f,getattr(newresult,f))
        def dummy(*args, **kwargs):
            #import pdb;pdb.set_trace()
            pass
        for f in ["printErrors", "printSummary"]:
            setattr(result,f,dummy)
        return newresult
        #return newresult
