from nfv_tree.nfvtree import NfvTree, NfvFile, NfvIoTactic

def create_tree():
    """ create a file tree with 3 width and 3 depth, then fill 10 test files
    """
    # initialize a file tree
    demotree = NfvTree(tree_root="E:\\testdir\\testtree2", tree_width=3, tree_depth=2)

    # create io tactic for subsequent file deployment 
    iot = NfvIoTactic(data_pattern='random', seek_type='random', io_size='1k')

    # apply the io tactic on the file tree
    demotree.set_tactic(iot)

    # start to deploy 10 files with each has 2k file size
    demotree.create_file(number=10, size='2k')

    # wipe the entire file tree
    demotree.wipe()

    del demotree


def tailor_tree():
    """ tailor the number of the files within the file tree
    """
    # initialize a file tree
    demotree = NfvTree(tree_root="E:\\testdir\\testtree2", tree_width=3, tree_depth=2)

    # create io tactic for subsequent file deployment 
    iot = NfvIoTactic(data_pattern='fixed', seek_type='reverse', io_size='2k')
    
    # apply the io tactic on the file tree
    demotree.set_tactic(iot)

    # start to deploy 10 files with each has 2k file size
    demotree.create_file(number=10, size='2k')

    # tailor the number of files to 5 
    demotree.tailor(file_number=5)

    # tailor the number of files to 20, the size of increamental file 1kb
    demotree.tailor(file_number=20, file_size='1K')

    # tailor the number of file to 0, which equivalent to wipe()
    demotree.tailor(file_number=0)

    # tailor the number of file to 10, which equivalent 
    # to craete_file(number=10,size='2k')
    demotree.tailor(file_number=10, file_size='2k')

    demotree.wipe()

    del demotree



if __name__ == '__main__':
    
    #create_tree()
    tailor_tree()
