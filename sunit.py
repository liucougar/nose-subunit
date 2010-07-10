"""This plugin takes over all tests output to generate subunit-formated
output.
"""

from new import instancemethod
from datetime import datetime

from testtools.content import Content, ContentType, TracebackContent
#can't name this file as subunit, otherwise the following line fails
from subunit import TestProtocolClient, iso8601

from nose.plugins import Plugin
from nose.util import isclass
from nose.result import _exception_detail
from nose.failure import Failure as NoseFailure

class TextContent(Content):
    def __init__(self, value, acontenttype=None):
        if acontenttype is None:
            acontenttype = ContentType("text","plain")
        Content.__init__(self, acontenttype, lambda:value.encode("utf8"))

def fixTestCase(test):
    if not hasattr(test, 'id'):
        def idfunc(*args): # pylint: disable-msg=W0613
            if hasattr(test, 'context'):
                cont = test.context
                if hasattr(cont, '__module__'):
                    return cont.__module__+"."+cont.__name__
                elif hasattr(cont, '__name__'):
                    return cont.__name__
                else:
                    return str(test.context)
            return str(test)
        test.id = idfunc

class SubunitTestResult(TestProtocolClient):
    def __init__(self, stream, descriptions, config=None,
                 errorClasses=None, 
                 #kwargs capture all other arguments, including unused 
                 #ones: verbosity
                 **kwargs): 
        if errorClasses is None:
            errorClasses = {}
        self.errorClasses = errorClasses
        #if config is None:
        #    config = Config()
        self.config = config
        self.descriptions = descriptions
        self.stream = stream #this is to make multiprocess plugin happy
        self.useDetails = kwargs.get("useDetails", False)
        self._wassuccess = True
        TestProtocolClient.__init__(self, stream)
    
    def _getArgs(self, test, err):
        if self.useDetails:
            details = {"traceback":TracebackContent(err, test)}
            error = None
        else:
            error = err
            details = None

        return error, details

    #properly assign an id() function to nose.failure.Failure (caused
    #by import error (or other errors which prevents loading of a file)
    #so in such a case, subunit won't print nose.failure.Failure.runTest
    #as the test case name
    def beforeTest(self, test): # pylint: disable-msg=R0201
        if isinstance(test.test, NoseFailure):
            def newid(*args): # pylint: disable-msg=W0613
                #test.address() returns a 3 item tuple, the first one
                #is the abspath to the py file, the second one is
                #the python module name
                #the default output would use test.__str__ as the id
                #of a nose.failure.Failure, but I think the module
                #name is more useful
                return test.address()[1]
            test.id = newid #test.__str__

    #in the case of import module failure, startTest is not called by
    #nose runner, we have to detect that case and call it manually in
    #addError to have wellformed subunit output
    def startTest(self, test):
        test._subunit_started = True
        TestProtocolClient.startTest(self, test)
        
    #modified from nose/result.addError
    def addError(self, test, error): # pylint: disable-msg=W0221
        """Overrides normal addError to add support for
        errorClasses. If the exception is a registered class, the
        error will be added to the list for that class, not errors.
        """
        
        fixTestCase(test)
        #manually call startTest if it's not already called
        if not getattr(test, '_subunit_started', False):
            self.startTest(test)

        ecls, evt, tbk = error # pylint: disable-msg=W0612

        # pylint: disable-msg=W0612
        for cls, (storage, label, isfail) in self.errorClasses.items():
            if isclass(ecls) and issubclass(ecls, cls):
                if not isfail:
                    reason = _exception_detail(evt)
                    if reason and self.useDetails:
                        details = {"reason":TextContent(reason)}
                        reason = None
                    else:
                        details = None

                    self._addNonFailOutcome(label.lower(), test, 
                        reason=reason, details=details)
                    return
        self._wassuccess = False
        error, details = self._getArgs(test, error)
        test.passed = False
        TestProtocolClient.addError(self, test, error, details=details)

    def addFailure(self, test, error): # pylint: disable-msg=W0221
        self._wassuccess = False
        #TestProtocolClient does not call TestResult.addFailure
        test.passed = False
        fixTestCase(test)
        error, details = self._getArgs(test, error)
        TestProtocolClient.addFailure(self, test, error, details=details)

    def wasSuccessful(self):
        return self._wassuccess

    def _addNonFailOutcome(self, outcome, test, reason=None, details=None):
        """Report a non-failure error (such as skip)"""
        if reason is None:
            self._addOutcome(outcome, test, error=None, details=details)
        else:
            self._stream.write(outcome+": %s [\n" % test.id())
            self._stream.write("%s\n" % reason)
            self._stream.write("]\n")
    
    def addTime(self):
        self.time(datetime.now(iso8601.UTC))
    #the nose testrunner would call these two functions
    def printErrors(self, *args):
        pass
    def printSummary(self, *args): # pylint: disable-msg=W0613
        self.addTime()

def _getOption(options, name, default):
    try:
        return getattr(options, name)
    except AttributeError:
        return default

class Subunit(Plugin):
    """Output test results in subunit format
    """
    
    name = 'subunit'
    #run before multiprocess plugin, otherwise prepareTestRunner 
    #won't be able to properly monkey patch runner
    score = 1100

    useDetails = False
    multiprocess_workers = 0
    config = None
    loaderClass = None
    
    def configure(self, options, conf):
        if not self.can_configure:
            return
        Plugin.configure(self, options, conf)
        
        self.config = conf
        
        #detailedErrors is defined in failuredetail plugin
        self.useDetails = _getOption(options, 
          "detailedErrors", self.useDetails)
        #multiprocess_workers defined in multiprocess plugin
        self.multiprocess_workers = _getOption(options, 
          "multiprocess_workers", self.multiprocess_workers)

    #copied from multiprocess plugin
    def prepareTestLoader(self, loader):
        """Remember loader class so MultiProcessTestRunner can instantiate
        the right loader.
        """
        self.loaderClass = loader.__class__ 

    #so we stick with prepareTestResult for now
    def prepareTestRunner(self, runner):
        #replace _makeResult in the default nose TestRunner to return
        #our implementation SubunitTestResult

        if not hasattr(runner, "_makeResult"):
            raise Exception('''runner does not have _makeResult method,\
don't know how to attach to it.''')
        
        #this plugin runs before  multiprocess plugin, and this function
        #return a runner, so it will prevent multiprocess.prepareTestRunner
        #from executing. so if multiprocess is enabled, we need to create 
        #MultiProcessTestRunner
        if self.multiprocess_workers:
            from nose.plugins.multiprocess import MultiProcessTestRunner
            runner = MultiProcessTestRunner(stream=runner.stream,
                                      verbosity=self.config.verbosity,
                                      config=self.config,
                                      loaderClass=self.loaderClass)

        runner.useDetails = self.useDetails
        def _makeResult(self):
            result = SubunitTestResult(self.stream, self.descriptions,
                self.config, useDetails=self.useDetails)
            result.addTime()
            return result
        runner._makeResult = instancemethod(_makeResult, 
          runner, runner.__class__)
        return runner
