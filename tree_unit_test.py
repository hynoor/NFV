from nfv_tree.nfvtree import NfvTree, NfvFile, NfvIoTactic
from nfv_tree.nfvlockmanager import NfvLockManager, NfvLock
import pdb
import time


def ads_demo():
    """ ADS demoe test
    """

    mytree = NfvTree("E:\\fixed")
    mytree.tailor(file_number=2)
    mgrs = []
    for f in mytree:
        lockmgr = NfvLockManager()
        lockmgr.attach(f)
        lockproducer = lockmgr.create_lock()
        for i, lock in zip(range(10), lockproducer):
            mylock = lockproducer
        mgrs.append(lockmgr)

    for m in mgrs:
        for l in m:
            l.on()
    print("start to wait")
    time.sleep(000)
        

def deploy_tree():
    """  deploy a file tree
    """
    # NfvTree
    # NfvPolic 
    # NfvIoMocker
    """
    mytree = NfvTree(tree_root='/mnt/nfv/testshare/numbertest', tree_width=2, tree_depth=2)
    mytree.wipe()
    mytree = NfvTree(tree_root='/mnt/nfv/testshare/numbertest', tree_width=1, tree_depth=1)
    mytree = NfvTree(tree_root="testshare/numbertest")
    print(mytree.get_property('file_number'))
    print(mytree.get_property('tree_size'))
    mytree.wipe()
    mytree = NfvTree(tree_root="testshare/numbertest", tree_width=1, tree_depth=1)
    iotactic = NfvIoTactic(io_size='8k', data_pattern='fixed', seek_type='random', data_check=True)
    mytree.set_io_tactic(iotactic)
    mytree.create_file(number=5, size='1M')
    print(iotactic.get_property())
    mytree.overwrite()
    print("affter tailor 5: %d" % mytree.get_property('file_number'))
    print("Before: %s" % mytree.get_property(name='tree_size'))
    mytree.truncate(file_size='10M')
    print("After: %s" % mytree.get_property(name='tree_size'))
    """
    mytree = NfvTree(tree_root="testshare/numbertest")
    mytree.clear_file()
    mytree.tailor(file_number=10, file_size='1m')
    iotactic = NfvIoTactic(data_pattern='random', data_check=True)
    mytree.set_io_tactic(iotactic)
    mytree.overwrite()

if __name__ == '__main__':
    #deploy_tree()
    ads_demo()
