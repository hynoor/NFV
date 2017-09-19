import logging

# internal modules
from nfv_utils.utils import MyLogger, convertsize
from nfv_validators.nfvlockmanager import NfvLockManager


if __name__ == "__main__":

    mylogger = MyLogger( logger_name = 'ut1', log_level = 'INFO', record_path ='log/ut1')
    logger = mylogger.get_logger()
    logger.info("I am first log")

    size = '30G'
    print("converted %s to %d" % (size, convertsize(size)))

    testfilepath = 'testshare/testfile.txt'
    filemanager = NfvLockManager(testfilepath, 'shared')
    filemanager.lock()
    logger.debug(filemanager.get_lock())
