#this file has to be outside of tests dir so that it won't be picked up when multiprocess plugin is enabled to run nose-subunit tests
def setup_package():
    raise Exception
