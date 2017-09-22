import logging
import pdb
import time

# internal modules
from nfv_utils.utils import MyLogger, convert_size
from nfv_validators.nfvlockmanager import NfvLockManager

mylogger = MyLogger()
logger = mylogger.get_logger()
logger.info("I am first log")

def multi_produce():
    testfilepath = 'E:\\locktest\\README.md'
    logger.info("Create Lock Manager")
    lockmanager = NfvLockManager()
    # attach to a file to be lock manipulated

    logger.info("Create Locks")
    lockmanager.attach(testfilepath)
    producer = lockmanager.produce_lock()
    
    logger.info("Attach lock manager to a file")
    logger.info("Turn on all locks")
    for lock in producer:
        lock.on()
        logger.info("lock %s was turned on" % lock.get_property('id'))

    logger.info("Wait for 1 seconds")
    time.sleep(1)

    logger.info("Turn off all locks")
    for lock in lockmanager:
        lock.off()
        logger.info("lock %s was turned off" % lock.get_property('id'))

    logger.info("Detach file")
    lockmanager.detach()

    logger.info("Delete lock manager")
    lockmanager.wipe_lock()



def individual_produce():
    testfilepath = 'E:\\locktest\\README.md'
    logger.info("Create Lock Manager")
    lockmanager = NfvLockManager()
    # attach to a file to be lock manipulated

    logger.info("Create Locks")
    lockmanager.attach(testfilepath)
    lockmanager.produce_lock(start=0, length=10, stop=500, step=10, mode='exclusive')
    
    logger.info("Attach lock manager to a file")

    logger.info("Turn on all locks")
    for lock in lockmanager:
        lock.on()
        logger.info("lock %s was turned on" % lock.get_property('id'))

    logger.info("Wait for 1000 seconds")
    time.sleep(10)


if __name__ == "__main__":

    multi_produce()


