"""
This file defined the block io manipulations
"""
from nfv_tree.nfvtree import NfvFile, NfvIoTactic, encipher_data
from os.path import getsize


class NfvBlock(NfvFile):
    """
    Nfv block device
    """

    __slots__ = (
        '_path',
        '_size',
        '_name',
        '_iotactic',
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
        self._size = getsize(self._path)
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

    def write(self, start_offset=0, stop_offset=4096):
        """
        Issue IO on the block device
        :return:
        """
        start = start_offset
        stop = stop_offset
        if stop - start > self._size:
            stop = self._size
        if start > self._size:
            raise RuntimeError("ERROR: Start offset should no larger than volume size!")
        io_range = stop - start
        remainder = io_range % self._iotactic.get_property('io_size')
        indexsupplier = self._iotactic.seek_to(start_offset=start, stop_offset=stop)
        if remainder > 0:
            rindex = next(indexsupplier)

        with open(self._path, 'rb+') as fh:
            if remainder > 0 and self._iotactic._seek == 'reverse':
                data = self._iotactic.get_data_pattern()
                if self._iotactic._datacheck:
                    NfvFile._io_check_db[encipher_data(data, NfvFile._io_check_db)] = True
                fh.seek(rindex)
                fh.write(data[:remainder])
            for idx in indexsupplier:
                data = self._iotactic.get_data_pattern()
                if self._iotactic._datacheck:
                    self._io_check_db[encipher_data(data, self._io_check_db)] = True
                fh.seek(idx)
                fh.write(data)
            if remainder > 0 and (self._iotactic.seek_type == 'sequential' or self._iotactic.seek_type == 'random'):
                data = self._iotactic.get_data_pattern()
                if self._iotactic._datacheck:
                    self._io_check_db[encipher_data(data, self._io_check_db)] = True
                fh.seek(rindex)
                fh.write(data[:remainder])

        pass

    def read(self):
        """
        Read data
        :return: None
        """
        pass

