from nfv_tree.nfvtree import NfvTree, NfvFile, NfvIoTactic


def deploy_tree():
    """  deploy a file tree
    """
    # NfvTree
    # NfvPolicy
    # NfvIoMocker

    mytree = NfvTree(tree_root='testshare/testtree')
    print(mytree.get_property('file_number'))
    print(mytree.get_property('dir_number'))
    #mytree.create_file(quantity=100, size='1M')
    #print(len(mytree._files))


if __name__ == '__main__':
    deploy_tree()
