from nfv_tree.nfvtree import NfvTree, NfvFile
from nfv_utils.utils import random_string
import pdb

def deploy_tree():
    """  deploy a file tree
    """
    # NfvTree
    # NfvPolicy
    # NfvIoMocker
    mytree = NfvTree(tree_root='E:\\testshare\\VohcqS2V')


"""
    treeconfig1 = NfvTreeConfigure()
    treeconfig1.io = NfvPatternGenerator(pattern='random', size=8k)
    treeconfig1.seek_type = 'seq'
    treeconfig1.data_check = True
    treeconfig1.file_size = '1G'

    treeconfig2 = NfvIoConfigure()
    treeconfig2.io = NfvPatternGenerator(pattern='random', size=8k)
    treeconfig2.seek = 'seq'
    treeconfig2.data_check = False
    treeconfig2.file_size = '10M'
    treeconfig2.file_number = '10M'

    mydeployer=load_config(config=treeconfig1)

    # start to deploy
    mydeployer.deploy()
"""

if __name__ == '__main__':
    deploy_tree()
