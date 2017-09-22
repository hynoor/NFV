import logging
import pdb
import time

# internal modules
from nfv_utils.utils import MyLogger, convert_size
from nfv_validators.nfvlockmanager import NfvLockManager, NfvLock

mylogger = MyLogger()
logger = mylogger.get_logger()
logger.info("I am first log")

def multi_produce():
    testfilepath = 'testshare/testfile.txt'
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
        logger.info("switched on lock %s" % lock.get_property('id'))

    logger.info("Wait for 1 seconds")
    time.sleep(1)

    logger.info("Turn off all locks")
    for lock in lockmanager:
        lock.off()
        logger.info("switched off %d" % lock.get_property('id'))

    logger.info("Detach file")
    lockmanager.detach()

    logger.info("Delete lock manager")
    lockmanager.wipe_lock()



def individual_produce():
    """ demonstrates how to create lock and switch on lock
    life cycle of a lock:
    (create lock)-->lock.attach-->lock.on-->lock.off-->lock.detach-->(del lock)
    """
    testfilepath = 'testshare/testfile.txt'
    testfilepath2 = 'testshare/testfile.txt'
    logger.info("Create 2 invidual NfvLock objects")

    lock1 = NfvLock(offset=0, length=100)
    lock2 = NfvLock(offset=200, length=205)
    with open(testfilepath, 'rb+') as testfh:
        lock1.attach(testfh)
        lock2.attach(testfh)
        
        lock1.on()
        lock2.on()

        logger.info("switched on lock %s " % lock1.get_property('id'))
        logger.info("switched on lock %s " % lock2.get_property('id'))
        logger.info("Wait for 3 seconds")
        time.sleep(3)
        lock1.off()
        lock2.off()
        logger.info("detach filehandle ...")
        lock1.detach()
        lock2.detach()
        logger.info("close filehandle ...")

    with open(testfilepath2, 'rb+') as testfh:
        lock1.attach(testfh)
        lock2.attach(testfh)
        
        lock1.on()
        lock2.on()

        logger.info("switched on lock %s " % lock1.get_property('id'))
        logger.info("switched on lock %s " % lock2.get_property('id'))
        logger.info("Wait for 3 seconds")
        time.sleep(3)
        lock1.off()
        lock2.off()
        logger.info("detach filehandle ...")
        lock1.detach()
        lock2.detach()
        logger.info("close filehandle ...")

    del lock1, lock2
   
if __name__ == "__main__":

    multi_produce()
    individual_produce()


