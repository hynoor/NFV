""" This module implements all locking manipulations for both NFS locks and CIFS locks
"""
import os
import sys
import errno

from os.path import isfile, exists

class NfvLockManager:
    """ NfvLockManager Class
    Implements and offers locks related manipulations
    Each target file need its own NfsLockManager object respectively
    """

    if os.name == 'posix':
        import fcntl
        import struct
        # locking modes
        LOCK_MODES = {
            'EXCLUSIVE'        : ('r+b', fcntl.F_WRLCK, fcntl.F_SETLK),
            'EXCLUSIVE_IO'     : ('r+b', fcntl.F_WRLCK, fcntl.F_SETLK),
            'EXCLUSIVE_BLK'    : ('r+b', fcntl.F_WRLCK, fcntl.F_SETLKW),
            'EXCLUSIVE_BLK_IO' : ('r+b', fcntl.F_WRLCK, fcntl.F_SETLKW),
            'SHARED          ' : ('r+b', fcntl.F_WRLCK, fcntl.F_SETLKW),
            'UNLOCK'           : ('r+b', fcntl.F_UNLCK, fcntl.F_SETLK),
        }
    elif os.name == 'nt':
        import msvcrt
        LOCK_MODES = {
            'EXCLUSIVE'        : ('r+b', msvcrt.LK_NBLCK),
            'EXCLUSIVE_IO'     : ('r+b', msvcrt.LK_NBLCK),
            'EXCLUSIVE_BLK'    : ('r+b', msvcrt.LK_LOCK),
            'EXCLUSIVE_BLK_IO' : ('r+b', msvcrt.LK_LOCK),
            'SHARED          ' : ('r+b', msvcrt.LK_NBRLCK),
            'UNLOCK'           : ('r+b', msvcrt.LKUNLCK),
        }
    
    }
    else:
        sys.exit('Unsupported Platform! Only accepts NT and POSIX system.')


    def __init__(self, file_path=None):
        """ init
        initialize the class's properties
        """
        if len(files) == 0:
            raise ValueError("Parameter files shouldn't be empty!")

        for f in files:
            if exists(f) or isfile(f):
                raise ValueError("Given file: %s doesn't exist" % f)
  
        self._file = file_path
        self._filehandle = None
        self._filehandle = open(file_path, LOCK_MODE['EXCLUSIVE'])
        self._lockedregions = dict()


    def getlock(self):
        pass


    def lock(self, file_handle=None, offset=None, length=None):
        """ setlock
        ceate a byte-range lock on specific location 
        :param file_handle : file hanle of target file where locks to be creatd  
        :param offset      : the start offset of the lock to be created
        :param length      : the length of the lock to be created
        :return            : a tuple which stores the lock's attributes (file_hanlde, offset, length)
        """
        pass


    def unlock(self, file_handle=None, offset=None, length=None):
        """ setlock
        remove a byte-range lock on specific location 
        :param file_handle : file hanle of target file where locks to be creatd  
        :param offset      : the start offset of the lock to be created
        :param length      : the length of the lock to be created
        """

        pass


    def multilock(self, file_handle=None, start=0, end=0, length=0, mode='EXCLUSIVE'):
        """ strategically created multiple target locks 
        """
        pass


    def _posixlock(self, file_handle=None, mode='EXCLUSIVE', offset=0, length=0, with_io=None):
        """ posixlock
        Create a posix byte-range lock
        """
        fh = file_handle
        lockmode = mode.lower()
        withio = with_io

        lockdata = struct.pack('hhllhh', self.LOCK_MODES[lockmode][1], 0, offset, length, 0, 0)

        try:
            print('Set %s lock on byte range[%d - %d] of file: %s' 
                    % (lockmode, offset, offset + length - 1, fh.name))
        
            if withio:
                if lockmode == 'exclusive_io' or lockmode == 'exclusive_blk_io':
                    rv = fcntl.fcntl(fh, self.LOCK_MODES[lockmode[2]], lockdata)
                    fh.seek(offset)
                    # truncate extra content which exceeds end offest
                    fh.write(withio[:length])
                elif lockmode == 'SHARED' or lockmode = 'UNLOCK':
                    # WARNING
                    # the minimal size of kernel read is one page (4KB)
                    # hence the read may failed if target bytes
                    # which page was overlappped on other byte(s)
                    # owned by other lockowners
                    fh.seek(offset)
                    readdata = fh.read(length)
                    if readdata != withio:
                        sys.exit("ERROR: data verification failed. expect: %s | actual: %s" 
                                % (withio, readdata))
                    rv = fcntl.fcntl(fh, self.LOCK_MODES[lockmode][2], lockdata)
            else:
                rv = fcntl.fcntl(fh, self.LOCK_MODES[lockmode[2], lockdata)

        except IOError as e:
            raise IOError(e)
        
        # register the lock
        self._lockedregions[(fh, self.LOCK_MODES[lockmode][2], lockdata)] = 1


    def _ntlock(self):
        pass



