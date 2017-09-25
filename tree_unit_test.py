from nfv_tree.nfvtree import NfvTree, NfvFile
from nfv_utils.utils import random_string
import pdb

from nfv_tree.nfvtree import NfvTree, NfvFile, NfvIoTactic


def deploy_tree():
    """  deploy a file tree
    """
    # NfvTree
    # NfvPolicy
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
    deploy_tree()
