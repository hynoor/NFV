from nfv_tree.nfvtree import NfvTree, NfvFile, NfvIoTactic

def customize_data_pattern():
    """ build a complex data pattern for I/O manipulations
    """

    # build a compress data pattern with 90%  each byte hascompressible ratio
    dp1 = NfvIoTactic.compress_pattern(compress_ratio=90, io_size='10k', chunk=10)

    # build a data pattern with binary zero
    dp2 = NfvIoTactic.hex_pattern(hex_value='ff', io_size='10k')

    # build a 20KB size data pattern with each byte has customized bits like '10000001'  
    dp3 = NfvIoTactic.bit_pattern(bits='10000001', io_size='10k')

    # compound all built data pattern together
    dp = dp1 + dp2 + dp3

    # initialize a NfvIoTactic object and set the data pattern
    iot = NfvIoTactic()
    iot.set_data_pattern(dp)

    # create a file tree then create 100 files with assigned data pattern
    mytree=NfvTree(tree_root="test_dir\\test_tree", io_tactic=iot)
    mytree.tailor(file_number=100, file_size='1M')

  
def create_tree():
    """ create a file tree with 3 width and 2 depth, then fill 10 test files
    """
    # initialize a file tree
    demotree = NfvTree(tree_root="testdir\\testtree2", tree_width=3, tree_depth=2)
    print("Tree initialzed")

    # create io tactic for subsequent file deployment 
    iot = NfvIoTactic(data_pattern='random', seek_type='random', io_size='1k')
    print("Io tactic initialzed")

    # apply the io tactic on the file tree
    demotree.set_tactic(iot)
    print("Io tactic deployed")

    # start to deploy 10 files with each has 2k file size
    demotree.create_file(number=10, size='1m')
    print("File deployed")

    # wipe the entire file tree
    demotree.wipe()
    print("Tree wiped")

    del demotree
    print("Tree deleted")


def tailor_tree():
    """ tailor the number of the files within the file tree
    """
    # initialize a file tree
    demotree = NfvTree(tree_root="testdir\\testtree2", tree_width=3, tree_depth=2)

    # create io tactic for subsequent file deployment 
    iot = NfvIoTactic(data_pattern='fixed', seek_type='reverse', io_size='2k')
    
    # apply the io tactic on the file tree
    demotree.set_tactic(iot)

    # start to deploy 10 files with each has 2k file size
    # demotree.create_file(number=10, size='2k')

    # tailor the number of files to 5 
    demotree.tailor(file_number=5)

    # tailor the number of files to 20, the size of increamental file 1kb
    demotree.tailor(file_number=20, file_size='1K')

    # tailor the number of file to 0, which equivalent to wipe()
    demotree.tailor(file_number=0)

    # tailor the number of file to 10, which equivalent to craete_file(number=10,size='2k')
    demotree.tailor(file_number=10, file_size='2k')

    demotree.wipe()

    del demotree


if __name__ == '__main__':
    """ main test
    """
    create_tree()
    tailor_tree()
    customize_data_pattern()

