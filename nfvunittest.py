import logging
import pdb
import time

# internal modules
from nfv_utils.utils import MyLogger, convertsize
from nfv_validators.nfvlockmanager import NfvLockManager


if __name__ == "__main__":

    mylogger = MyLogger( logger_name = 'ut1', log_level = 'INFO')
    logger = mylogger.get_logger()
    logger.info("I am first log")

    testfilepath = 'Z:\\nfv\\testfile.txt'
    filemanager = NfvLockManager(testfilepath, 'shared')
    filemanager.lock(offset=0, length=10, locking_mode='exclusive')
    filemanager.lock(offset=5, length=15, locking_mode='exclusive')
    filemanager.unlock()
    filemanager.unlock()
    for l in filemanager.get_lock():
        logger.info(l)

    time.sleep(1000)
