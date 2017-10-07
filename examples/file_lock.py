""" byte-range file lock instructions

- One NfvLockManger object can attach one file obejct only
- One NfvLockManger object can manage multiple NfvLock obejcts
- One NfvLock object can attach one NfvFile Object only 

"""
import time
from nfv_tree.nfvtree import NfvTree, NfvFile, NfvIoTactic
from nfv_tree.nfvlockmanager import NfvLockManager, NfvLock
from nfv_tree.utils import random_string


def create_10_lock_on_single_file():
    """ create 100 byte range locks on a file

    This test creates a lock manager object to manager all
    locks on a single file, highly recommand using NfvLockManager
    to manipulate multiple locks for sole file
    """
    
    # create a lock manger object
    lckmgr = NfvLockManager() 
    # create a io tactic object
    iot = NfvIoTactic()
    # create a file object 
    myfile = NfvFile("E:\\testdir\\testfile.txt", size='8k', io_tactic=iot)
    # attach file object to lock manager
    lckmgr.attach(myfile)
    # produce 10 sequencial byte-range locks (1 byte length)
    producelock = lckmgr.create_lock(mode='exclusive')
    for i in range(10):
        next(producelock)

    # switch on all the 100 locks
    # pdb.set_trace()
    for lck in lckmgr:
        lck.on()
        print("lock %s was turned on" % lck.get_property('id'))

    print("wait a few seconds")
    time.sleep(10)

    # switch off all the 100 locks after waiting 10 seconds
    for lck in lckmgr:
        lck.off()
        print("lock %s was turned off" % lck.get_property('id'))

    lckmgr.wipe_lock()



def create_1_lock_on_10_files():
    """ create 1 byte range locks on 10 test file respectively

    this test creates NfvLock objects directly with absent of NfvLockManger,
    which is unneccessary when it comes one file lock with each test file respectively
    """

    # create a file tree
    demotree = NfvTree(tree_root="E:\\testdir\\testtree")

    # adjust the number of file of the tree to 10, with 1k size
    demotree.tailor(file_number=10)

    # create 10 file lock objects and attach each respectively
    locks = []
    for f in demotree:
        demolock = NfvLock(mode='exclusive_blk')
        demolock.attach(f)
        # switch on the lock
        demolock.on()
        print("lock %s was turned on" % demolock.get_property('id'))
        locks.append(demolock)

    time.sleep(10)
    
    # switch off all lock after 10 seconds
    for lck in locks:
        lck.off()
        print("lock %s was turned off" % lck.get_property('id'))
        del lck 


if __name__ == '__main__':
    """ test main
    """
    create_10_lock_on_single_file()

    create_1_lock_on_10_files()

