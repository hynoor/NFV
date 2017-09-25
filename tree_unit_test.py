from nfv_tree.nfvtree import NfvTree, NfvFile, NfvIoTactic


def deploy_tree():
    """  deploy a file tree
    """
    # NfvTree
    # NfvPolicy
    # NfvIoMocker

    mytree = NfvTree(tree_root='testshare/numbertest')
    iotactic = NfvIoTactic(io_size='2k', data_check=False)
    mytree.set_io_tactic(iotactic)
    mytree.resize(number=0)
    print("init: %d" % mytree.get_property('file_number'))
    mytree.resize(number=100, file_size='100K')
    print("affter resize 100: %d" % mytree.get_property('file_number'))
    mytree.resize(number=90, file_size='100K')
    print("affter resize 90: %d" % mytree.get_property('file_number'))
    mytree.resize(number=0, file_size='100k')
    print("affter resize 0: %d" % mytree.get_property('file_number'))
    mytree.resize(number=40, file_size='100k')
    print("affter resize 40: %d" % mytree.get_property('file_number'))
    #mytree.create_file(number=100, size='1M')
    #print(len(mytree._files))


if __name__ == '__main__':
    deploy_tree()
