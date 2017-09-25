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
    """
    mytree = NfvTree(tree_root="C:\\testshare\\numbertest", tree_width=2, tree_depth=2)
    mytree.wipe()
    mytree = NfvTree(tree_root="C:\\testshare\\numbertest", tree_width=1, tree_depth=1)
    iotactic = NfvIoTactic(io_size='8k', data_pattern='fixed', seek_type='random', data_check=True)
    mytree.set_io_tactic(iotactic)
    mytree.tailor(file_number=5, file_size='7K')
    mytree.checksum()
    print(iotactic.get_property())
    for f in mytree:
        print("checksum: %s" % f.get_property('checksum'))
    iotacticupdate = {
            'io_size'      : '2k',
            'data_pattern' : 'random',
            'seek_type'    : 'random',
    }
    iotactic.set_property(attrs=iotacticupdate)
    print(iotactic.get_property())
    mytree.overwrite()
    print("affter tailor 5: %d" % mytree.get_property('file_number'))
    for f in mytree:
        print("checksum: %s" % f.get_property('checksum'))
    """
    print("Before: %s" % mytree.get_property(name='tree_size'))
    mytree.truncate(file_size='10M')
    print("After: %s" % mytree.get_property(name='tree_size'))
    """


if __name__ == '__main__':
    deploy_tree()
