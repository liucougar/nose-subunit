"""This plugin takes over all tests output to generate subunit-formated
output.
"""

from new import instancemethod
from datetime import datetime
from unittest import TestSuite

from testtools.content import Content, ContentType, TracebackContent
#can't name this file as subunit, otherwise the following line fails
from subunit import TestProtocolClient, iso8601, PROGRESS_CUR

from nose.suite import LazySuite
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
        if getattr(test, 'test', None) and isinstance(test.test, NoseFailure):
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
    
    def options(self, parser, env):
        """Register commandline options
        """
        Plugin.options(self, parser, env)
        parser.add_option(
            "--no-preload", action="store_false",
            default=not env.get("NOSE_NO_PRELOAD"), dest="preload",
            help="Don't preload any nose LazySuite so instead of a single "
            "subunit progress output, this will generate "
            "more than one. Useful if preloading all tests is not "
            "feasible [NOSE_NO_PRELOAD]")

    def configure(self, options, conf):
        if not self.can_configure:
            return
        Plugin.configure(self, options, conf)
        
        self.config = conf

        self.preload = options.preload
            
        #detailedErrors is defined in failuredetail plugin
        self.useDetails = getattr(options, 
          "detailedErrors", self.useDetails)
        #multiprocess_workers defined in multiprocess plugin
        self.multiprocess_workers = getattr(options, 
          "multiprocess_workers", self.multiprocess_workers)

    #copied from multiprocess plugin
    def prepareTestLoader(self, loader):
        """Remember loader class so MultiProcessTestRunner can instantiate
        the right loader.
        """
        self.loaderClass = loader.__class__

        #monkey patch SuiteFactory.__call__ function to count how many tests there are
        sC = loader.suiteClass
        plugin = self
        def __call__(tests=(), **kw):
            is_suite = isinstance(tests, TestSuite)
            if callable(tests) and not is_suite:
                tests = list(tests())
            elif is_suite:
                tests = [tests]
            suite = sC(tests, **kw)
            if not is_suite:
                if not getattr(tests, '__len__', None):
                    lt = tests.tests
                else:
                    lt = tests
                #preload all lazy load suite, so we can count totalTests properly
                if self.preload:
                    for t in lt:
                        plugin.preloadLazySuite(t)
                plugin.totalTests += sum(1 for i in lt if not isinstance(i, TestSuite))
                #plugin.totalTests += sum(i.countTestCases() for i in lt)
                #import pdb;pdb.set_trace()
                #print "totalTests", plugin.totalTests, '*'*60
            return suite
        #assigning to suiteClass.__call__ won't make it work: calling suiteClass() won't trigger the __call__ attribute
        loader.suiteClass = __call__
    def preloadLazySuite(self, t):
        if isinstance(t, LazySuite):
            tests = [i for i in t]
            t._tests = tests
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
            #with MultiProcessTestRunner.run, beforeTest is called too 
            #early, so it will never print any progress info
            #instead, we have to monkey patch nextBatch which is
            #called by MultiProcessTestRunner.run to collect all tests
            from nose.plugins.multiprocess import MultiProcessTestRunner
            class SubunitMultiProcessTestRunner(MultiProcessTestRunner):
                _top = 1
                def nextBatch(self, test):
                    top = self._top
                    if top:
                        self._top = 0
                    for batch in MultiProcessTestRunner.nextBatch(self, test):
                        yield batch
                    if top:
                        plugin.printProgress()

            runner = SubunitMultiProcessTestRunner(stream=runner.stream,
                                      verbosity=self.config.verbosity,
                                      config=self.config,
                                      loaderClass=self.loaderClass)

        runner.useDetails = self.useDetails
        plugin = self
        def _makeResult(self):
            result = SubunitTestResult(self.stream, self.descriptions,
                self.config, useDetails=self.useDetails)
            result.addTime()
            #save the result so it can be used in beforeTest below
            plugin.result = result
            #plugin.printProgress()
            #if plugin.totalTests:
            #    result.progress(plugin.totalTests, PROGRESS_CUR)
            #    result.addTime()
            return result
        runner._makeResult = instancemethod(_makeResult, 
          runner, runner.__class__)

        return runner
    totalTests = 0
    def printProgress(self):
        if self.totalTests:
            self.result.progress(self.totalTests, PROGRESS_CUR)
            self.totalTests = 0
    def beforeTest(self, *args):
        self.printProgress()

# vi: set filetype=python tabstop=4 softtabstop=4 shiftwidth=4 expandtab:
