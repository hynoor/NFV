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
    mytree = NfvTree(tree_root='/mnt/nfv/testshare/numbertest', tree_width=2, tree_depth=2)
    iotactic = NfvIoTactic(io_size='8k', data_pattern='random', seek_type='reverse', data_check=True)
    print(iotactic.get_property())
    #pdb.set_trace()
    updateattrs = {
            'io_size'      : '2k',
            'data_pattern' : 'random',
            'seek_type'    : 'random',
    }
    iotactic.set_property(attrs=updateattrs)
    print(iotactic.get_property())
    mytree.set_io_tactic(iotactic)
    mytree.tailor(number=40, file_size='10M')
    print("affter tailor 1: %d" % mytree.get_property('file_number'))
    print("total size of tree: %d" % mytree.get_property('tree_size'))

    # mytree.wipe()


if __name__ == '__main__':
    deploy_tree()
