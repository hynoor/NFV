""" This module implements all locking manipulations for both NFS locks and CIFS locks
"""
import os
import sys
import fcntl
import struct
import errno
import pdb
import random
import collections

if os.name == 'posix':
    import fcntl
    import struct
elif os.name == 'nt':
    import msvcrt

from os.path import isfile, exists, getsize
from nfv_utils.utils import MyLogger, convertsize



class NfvLockManager:
    """ NfvLockManager Class
    Implements and offers locks related manipulations
    Each target file need its own NfvLockManager object respectively
    Support manipulating both NFS and CIFS locks
    """
    # put lock modes into slot to save memory
    #__slots__ = '_LOCK_MODES'
    if os.name == 'posix':
        # locking modes
        _LOCK_MODES = {
            'exclusive'        : ('r+b', fcntl.F_WRLCK, fcntl.F_SETLK),
            'exclusive_io'     : ('r+b', fcntl.F_WRLCK, fcntl.F_SETLK),
            'exclusive_blk'    : ('r+b', fcntl.F_WRLCK, fcntl.F_SETLKW),
            'exclusive_blk_io' : ('r+b', fcntl.F_WRLCK, fcntl.F_SETLKW),
            'shared'           : ('r+b', fcntl.F_WRLCK, fcntl.F_SETLKW),
            'unlock'           : ('r+b', fcntl.F_UNLCK, fcntl.F_SETLK),
        }
    elif os.name == 'nt':
        _LOCK_MODES = {
            'exclusive'        : ('r+b', msvcrt.LK_NBLCK),
            'exclusive_io'     : ('r+b', msvcrt.LK_NBLCK),
            'exclusive_blk'    : ('r+b', msvcrt.LK_LOCK),
            'exclusive_blk_io' : ('r+b', msvcrt.LK_LOCK),
            'shared'           : ('r+b', msvcrt.LK_NBRLCK),
            'unlock'           : ('r+b', msvcrt.LKUNLCK),
        }
    else:
        sys.exit('Unsupported Platform! Only accepts NT and POSIX system.')


    def __init__(self, file_path=None, locking_mode='exclusive'):
        """ init
        initialize the class's properties
        """
        if not isfile(file_path):
            raise ValueError("Given file: %s doesn't exist" % file_path)
        if locking_mode not in self._LOCK_MODES.keys():
            raise ValueError("Given locking_mode: %s is invalid$" % locking_mode)
        if getsize(file_path) == 0:
            raise ValueError("Size of given file: %s is 0, \
                unable create lock on empty file!" % file_path)

        self._file = file_path 
        self._lockmode = locking_mode
        self._filehandle = open(file_path, self._LOCK_MODES[self._lockmode][0])
        self._locatenext = self._locator()
        self._lockdb = collections.defaultdict(lambda : False)


    def get_lock(self):
        """ get_lock
        get all lock detail information maintained by current LockManager object
        :return  : a dict object containing all byte-range lock records
        """
        # return a iterator object
        return self._lockdb.keys()


    def lock(self, offset=None, length=None, 
            locking_mode='shared', with_io=None):
        """ setlock
        ceate a byte-range lock on specific location 
        :param offset       : the start offset of the lock to be created
        :param length       : the length of the lock to be created
        :param locking_mode : the locking mode to be applied on lock
        :param with_io      : data used for subsequent write/verify data
        :return             : a tuple which stores the lock's attributes (file_hanlde, offset, length)
        """
        # parameters validation
        lockstart = int(convertsize(offset))
        locklen = int(convertsize(length))

        if offset is None and length is not None:
            lockstart, _ = next(self._locatenext)
        elif length is None and offset is not None:
            _, locklen = next(self._locatenext)
        elif length is None and offset is None:
            try:
                lockstart, locklen = next(self._locatenext)
            except StopIteration:
                return
        
        if os.name == 'posix':
            self._posix_lock(lockstart, locklen, locking_mode, with_io)
        elif os.name == 'nt':
            self._nt_lock(lockstart, locklen, locking_mode, with_io)

        # register to locking table
        # plan to storage wrote checksum in 'value' field
        self._lockdb[(lockstart, locklen)] = 1

    def unlock(self, offset=None, length=None, with_io=None):
        """ setlock
        remove a byte-range lock on specific or random location
        if offset or length was not given, random unlock one
        :param offset      : the start offset of the lock to be created
        :param length      : the length of the lock to be created
        """
        lockstart = convertsize(offset)
        locklen = convertsize(length)
        randlock = None

        # if offset is not given, randomly select one from db to unlock
        if offset is None and length is None:
            if bool(self._lockdb):
                randlock = random.choice(list(self._lockdb.keys()))
                lockstart, locklen = randlock 
            else:
                logger.info("locking table is empty")
                return
        elif offset is not None and length is not None:
            if not self._lockdb[(offset, length)]:
                raise ValueError("ERROR: Given lock(%d, %d) was not found" % (offset, length))
        
        if os.name == 'posix' and self._lockdb[(lockstart, locklen)]:    
            self._posix_lock(lockstart, locklen, 'unlock', with_io)
        elif os.name == 'nt' and self._lockdb[(lockstart, locklen)]:    
            self._nt_lock(lockstart, locklen, 'unlock', with_io)
        
        # udpate lock table
        del self._lockdb[(lockstart, locklen)] 


    def m_lock(self, start=0, step=1, stop=0, length=1, locking_mode='exclusive', with_io=None):
        """ strategically created multiple target locks 
        :param start        : the start offset of first lock to be set
        :param length       : the length of each lock to be created 
        :param step         : the interval of each adjacent locks
        :param end          : the start offset of last lock should not exceeded
        :param locking_mode : the locking mode to be used
        """
        # to be implemented
        lockstart = convertsize(start)
        locklen = convertsize(length)
        lockstop = convertsize(stop)
        lockstep = convertsize(step)
        
        locklocator = self._locator(start=lockstart, lock_length=locklen, step=lockstep, stop=lockstop)

        for loc in locklocator:
            if os.name == 'posix':    
                self._posix_lock(loc[0], loc[1], locking_mode, with_io)
            elif os.name == 'nt' and not self._lockdb[loc]:    
                self._nt_lock(lock[0], loc[1], locking_mode, with_io)
            

    def _posix_lock(self, offset=0, length=1, locking_mode='shared',  with_io=None):
        """ posix_lock
        Create a posix byte-range lock
        """
        fh = self._filehandle
        lockmode = locking_mode.lower()
        withio = with_io
        lockdata = struct.pack('hhllhh', self._LOCK_MODES[lockmode][1], 0, offset, length, 0, 0)
        try:
            print('Set %s lock on byte range[%d - %d] of file: %s' 
                    % (lockmode, offset, offset + length - 1, fh.name))
        
            if withio:
                if lockmode == 'exclusive_io' or lockmode == 'exclusive_blk_io':
                    rv = fcntl.fcntl(fh, self._LOCK_MODES[lockmode][2], lockdata)
                    fh.seek(offset)
                    # truncate extra content which exceeds end offest
                    fh.write(withio[:length])
                elif lockmode == 'shared' or lockmode == 'unlock':
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
                    rv = fcntl.fcntl(fh, self._LOCK_MODES[lockmode][2], lockdata)
            else:
                rv = fcntl.fcntl(fh, self._LOCK_MODES[lockmode][2], lockdata)

        except IOError as e:
            raise IOError(e)


    def _nt_lock(self):
        """ manipulate NT byte-range lock
        """
        # to be implemented
        pass


    def _locator(self, start=0, lock_length=1, step=1, stop=0):
        """ yield specific location the locks to be created on 
        :param start       : the start offset to lock
        :param lock_length : length of each byte-range
        :param step        : interval of each byte-range
        :param stop        : the stop offset to lock
        :return            : (offset, length)
        """
        filesize = getsize(self._file)
        start = int(start)
        stop = int(stop)
        length = int(lock_length)
        interval = int(step)

        if interval + start > filesize:
            interval = filesize - start

        if length > (filesize - start) or length == 0:
            length = filesize - start 
            stop = filesize

        if stop <= filesize and stop > 0:
            filesize = stop

        numiterate = int((filesize-start)/(interval+length))

        #if interval != 0:
        for o in range(0,(numiterate+1)):
            activeoffset = start + o * (length+interval)
            if length + activeoffset <= filesize:
                yield (activeoffset, length)



