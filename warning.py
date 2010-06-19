import warnings

from nose.plugins import Plugin
from nose.case import Test

class Warnings(Plugin):
    """Capture warnings from the code being tested
    """
    
    name = 'warning'
    score = 100
    
    def prepareTestCase(self, test):
        """Wrap actual test in warning capture context
        """
        if not isinstance(test, Test):
            return
        def run(result):
            with warnings.catch_warnings(record=True) as w:
                warnings.filterwarnings("default", category=Warning, module=r".*")
                test.test(result)
                print "warnings captured: ",w
        return run