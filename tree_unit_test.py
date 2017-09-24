from nfv_tree.nfvtree import NfvTree, NfvFile, NfvIoTactic


def deploy_tree():
    """  deploy a file tree
    """
    # NfvTree
    # NfvPolicy
    # NfvIoMocker

    mytree = NfvTree(tree_root='testshare/testtree')
    iopolicy = NfvIoTactic(io_size='2k',  data_pattern='fixed')
    mytree.io_tactic(iopolicy)
    mytree.create_file(quantity=100, size='11k')
    mytree.create_file(quantity=20, size='2k')
    filenumber = mytree.get_property('file_number')
    treesize = mytree.get_property('tree_size')
    dirnum = mytree.get_property('dir_number')
    print(filenumber)
    print(treesize)
    print(dirnum)
    mytree.remove_file(quantity=1620)
    filenumber = mytree.get_property('file_number')
    treesize = mytree.get_property('tree_size')
    dirnum = mytree.get_property('dir_number')
    print(filenumber)
    print(treesize)
    print(dirnum)
    #mytree.create_file(quantity=100, size='1M')
    #print(len(mytree._files))


if __name__ == '__main__':
    deploy_tree()
