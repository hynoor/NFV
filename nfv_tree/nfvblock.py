"""
This file defined the block io manipulations
"""
import os
import mmap
from nfv_tree.nfvtree import NfvFile, NfvIoTactic, encipher_data, convert_size
from os.path import getsize
from os import statvfs

import pdb



class NfvBlock(NfvFile):
    """
    Nfv block device
    """

    __slots__ = (
        '_path',
        '_size',
        '_name',     # optional
        '_iotactic', #
    )

    def __init__(self, path=None, name='RestineLun', io_tactic=NfvIoTactic()):
        """
        Initialize a block device
        :param path: path to the block device
        :param name: name the of device (optional)
        :param io_tactic: tactic to perform IO
        """
        if path is None:
            raise RuntimeError("ERROR: Parameter 'path' is required!")

        self._path = path
        self._size = statvfs(self._path).f_bsize * statvfs(self._path).f_blocks
        self._name = name
        self._iotactic = io_tactic

    def set_iotactic(self, io_tactic=None):
        """
        Config IO tactic to the block device
        :param io_tactic: io_tactic object to be set
        :return: None
        """
        if io_tactic is None:
            raise RuntimeError("ERROR: Parameter io_tactic is required!")

        self._iotactic = io_tactic

    def io(self, operation='write', direct=False, start_offset=0, stop_offset=0):
        """
        Generator Function
        Issue IO on the block device, this func serves as the major role of block I/O
        :param operation    : operation type, either 'read' or 'write'
        :param direct       : Indicate if use direct I/O
        :param start_offset : offset of the I/O to be started
        :param stop_offset  : offset of the I/O to be stopped
        :return: generator object
        """
        start = convert_size(start_offset)
        stop = convert_size(stop_offset)
        openmode = os.O_RDONLY
        if stop == 0 and start == 0:
            stop = self._size
        elif stop - start > self._size:
            stop = self._size
        elif start > self._size:
            raise RuntimeError("ERROR: Start offset should no larger than volume size!")
        io_range = stop - start
        if operation == 'write':
            openmode = os.O_RDWR
        elif operation == 'read':
            pass
        else:
            raise ValueError("ERROR: Invalid operation!")
        if direct:
            openmode |= os.O_DIRECT
            # anyone wants direct is required to use 512 bytes aligned boundary
            data = mmap.mmap(-1, self._iotactic._iosize)
            data.write(self._iotactic._data)
        else:
            data = self._iotactic._data()
        remainder = io_range % self._iotactic.get_property('io_size')
        indexsupplier = self._iotactic.seek_to(start_offset=start, stop_offset=stop)
        if remainder > 0:
            rindex = next(indexsupplier)
        try:
            fd = os.open(self._path, openmode)
            if remainder > 0 and self._iotactic._seek == 'reverse':
                if self._iotactic._datacheck:
                    self._io_check_db[encipher_data(data, self._io_check_db)] = True
                os.lseek(fd, rindex, os.SEEK_CUR)
                if operation == 'write':
                    os.write(fd, data[:remainder])
                    yield len(data[:remainder])
                else:
                    yield len(os.read(fd, len(data[:remainder])))
            for idx in indexsupplier:
                if self._iotactic._datacheck:
                    self._io_check_db[encipher_data(data, self._io_check_db)] = True
                os.lseek(fd, idx, os.SEEK_CUR)
                if operation == 'write':
                    os.write(fd, data)
                    yield len(data)
                else:
                    yield len(os.read(fd, len(data)))
            if remainder > 0 and (self._iotactic.seek_type == 'sequential' or self._iotactic.seek_type == 'random'):
                if self._iotactic._datacheck:
                    self._io_check_db[encipher_data(data, self._io_check_db)] = True
                os.lseek(fd, rindex, os.SEEK_CUR)
                if operation == 'write':
                    os.write(fd, data[:remainder])
                    yield len(data)
                else:
                    yield len(os.read(fd, len(data[:remainder])))
        except OSError as e:
            print("Parameters Dump: fd:%d, idx:%d" % (fd, idx))
            raise OSError(str(e))
        finally:
            if fd:
                os.close(fd)


