
def passtest():
    pass
passtest.description = "myfunc.pass"

def failtest():
    assert False
failtest.description = "myfunc.fail"

def testGenerator():
    yield passtest
    yield failtest
