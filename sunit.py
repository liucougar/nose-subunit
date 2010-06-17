"""This plugin takes over all tests output to generate subunit-formated
output.
"""

#can't name this as subunit, otherwise the following line fails
from subunit import TestProtocolClient

from nose.plugins import Plugin
from nose.util import isclass
from nose.result import _exception_detail

class SubunitTestResult(TestProtocolClient):
    def __init__(self, stream, descriptions, config=None,
                 errorClasses=None):        
        if errorClasses is None:
            errorClasses = {}
        self.errorClasses = errorClasses
        if config is None:
            config = Config()
        self.config = config
        TestProtocolClient.__init__(self, stream)
                
    def addError(self, test, err): #modified from nose/result.addError
        """Overrides normal addError to add support for
        errorClasses. If the exception is a registered class, the
        error will be added to the list for that class, not errors.
        """
        stream = self._stream #getattr(self, '_stream', None)
        ec, ev, tb = err
        try:
            exc_info = self._exc_info_to_string(err, test)
        except TypeError:
            # 2.3 compat
            exc_info = self._exc_info_to_string(err)

        for cls, (storage, label, isfail) in self.errorClasses.items():
            if isclass(ec) and issubclass(ec, cls):
                if isfail:
                    test.passed = False
                #storage.append((test, exc_info))
                # Might get patched into a streamless result
                if stream is not None:
                    if not isfail:
                        reason = _exception_detail(err[1])
                        self._addNonFailOutcome(label.lower(),test,reason=reason)
                return

        TestProtocolClient.addError(self, test, err);

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

    def setOutputStream(self, stream):
        # grab for own use
        self.stream = stream
        # return dummy to prevent all default output
        class dummy:
            def write(self, *arg):
                pass
            def writeln(self, *arg):
                pass
        return dummy()

    def prepareTestResult(self, result):
        return SubunitTestResult(self.stream,result.descriptions,
            result.config, result.errorClasses)
