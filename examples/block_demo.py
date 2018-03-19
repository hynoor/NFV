"""
demo file for block io
"""
from nfv_tree.nfvtree import NfvIoTactic as Tactic
from nfv_tree.nfvblock import NfvBlock as Block
import sys


def block_trial():
    """
    A trial to probe cyclone data path
    """
    my_block = Block(path='/dev/sdb')

    iot = Tactic(io_size='4k', data_pattern='fixed')

    # build data pattern
    dp = Tactic.bit_pattern(bits='11111111', io_size='4k')
    dp2 = Tactic.bit_pattern(bits='00000000', io_size='4k')
    dp_final = dp + dp2

    iot.set_data_pattern(dp_final)

    my_block.set_iotactic(iot)

    wrote_size = 0
    count = 0

    # create a I/O generator
    io_writer = my_block.io(
        operation='write', 
        start_offset=0, 
        stop_offset='400k'
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
