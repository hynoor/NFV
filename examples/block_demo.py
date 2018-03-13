"""
demo file for block io
"""
from nfv_tree.nfvtree import NfvIoTactic
from nfv_tree.nfvblock import NfvBlock
import itertools
import sys


if __name__ ==  '__main__':
    blockd_obj = NfvBlock(path='/dev/sdd')
    iot = NfvIoTactic(io_size='8k', data_pattern='random')
    #dp = NfvIoTactic.hex_pattern(hex_value='00', io_size='4k')
    #iot.set_data_pattern(dp)
    blockd_obj.set_iotactic(iot)
    wrote_size = 0
    count = 0
    while True:
        io_writer = blockd_obj.io(operation='write', start_offset=0, stop_offset='400M')
        for s in io_writer:
            wrote_size += s
            count += 1
            sys.stdout.write('\r')
            sys.stdout.write("%d" % wrote_size)
            sys.stdout.flush()
        del io_writer
