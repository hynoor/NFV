from nfv_tree.nfvtree import NfvTree, NfvFile


def delpoy_tree():
    """  deploy a file tree
    """
    # NfvTree
    # NfvPolicy
    # NfvIoMocker

    mytree = NfvTree(tree_root='testshare/testtree' width=3, depth=3)

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

