"""
demo file for block io
"""
from nfv_tree.nfvtree import NfvIoTactic as Tactic
from nfv_tree.nfvblock import NfvBlock as Block


def block_trial():
    """
    A trial to probe cyclone data path
    """
    my_block = Block(path='/dev/mapper/mpathca')

    iot = Tactic(io_size='4k', data_pattern='random')

    # build data pattern
    #dp = Tactic.bit_pattern(bits='11111111', io_size='4k')
    #dp2 = Tactic.fixed_pattern(pattern="abcdefg", io_size='4k')

    #iot.set_data_pattern(dp2)
    iot = Tactic(io_size='4k', data_pattern='random')

    my_block.set_iotactic(iot)

    wrote_size = 0
    count = 0

    # create a I/O generator
    io_writer = my_block.io(
        operation='write', 
        start_offset='900k', 
        stop_offset='133300k'
    )

    for s in io_writer:
        wrote_size += s
        count += 1

    print("Data wrote: %d" % wrote_size)

        #sys.stdout.write('\r')
        #sys.stdout.write("%d" % wrote_size)
        #sys.stdout.flush()
    

if __name__ ==  '__main__':
     
    block_trial()
