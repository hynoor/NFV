""" This module implements 2 primary class to manipulating file locks
:class NfvLockManager : manage file locks
:class NfvLock        : file lock
"""
# standard modules
import os
import sys
import struct
import errno
import pdb
import random
import collections

# lock modules
if os.name == 'posix':
    import fcntl
    import struct
elif os.name == 'nt':
    import msvcrt

# NFV modules
from os.path import isfile, exists, getsize
from nfv_utils.utils import convert_size



class NfvLockManager:
    """ NfvLockManager Class
    Manages all lock objects it contains, do not support duplication locks
    Support manipulating both NFS and CIFS locks
    """


    def __init__(self, file_path=None, locks=[]):
        """ init
        initialize the class's property
        :param  locks  : a list stores all locks managed
        """
        self._fp = None
        self._fh = None
        self._repository = set(locks)
        self._isattached = False

        if file_path:
            self._fp = file_path
            self._fh = open(self._fp, 'r+b') 


    def add_lock(self, lock=None):
        """ add_lock
        add a nfv lock object to nfv manager
        it only add existing lock rather than creating new lock
        if manager object is attached a specific, the added lock
        will be attached automatically
        :param lock : lock object to be added to be managed
        """
        if lock is not NfvLock:
            raise ValueError("Given lock is not NfvLock type object!")
        elif lock.isattached:
            raise ValueError("Given lock is attached, unable be added into NfvLockManager object ")
        else: 
            self._repository.add(lock)

        if self._isattached:
            lock.attach(self._fh)


    def remove_lock(self, lock=None):
        """ remove_lock
        remove a NfvLock object from NfvLockManager repository
        it only reomve lock from manager rather than deleting the lock object
        """
        if lock is NfvLock and lock in self._repository:
            if lock.islocked:
                lock.off() # switch off
            elif lock.isattached():
                lock.detach() # detatch
            self._repository.remove(lock)
        else:
            raise ValueError("Given NfvLock object is invalid!")


    def attach(self, file_path=None):
        """ attach
        Attach lock objects to a specific file
        :param  : path of target file to be attached
        """
        if self._isattached:
            raise Exception("Current NfvLogManager object already being attached")

        if file_path is not None:
            self._fh = open(file_path)
            self._fp = file_path

        for lock in list(self._repository):
            lock.attach(self._fh)

        self._isattached = True
        

    def detach(self):
        """ detach
        detach this lock manager from a specific file
        it's containing NfvLock object will be detached automatically
        """
        if not self._isattached:
            pass
        else:
            self._fp = None
            for lock in list(self._repository):
                lock.detach()

    
    def produce_lock(self, length=1, mode='exclusive', data=None):
        """ sequencially create a NfvLock object at a time, 
            try best to produce maximu number of locks, 
            which attach status will be sync-ed up with NfvLockManager status
        :param start        : the start offset of first lock to be set
        :param length       : the length of each lock to be created 
        :param step         : the interval of each adjacent locks
        :param end          : the start offset of last lock should not exceeded
        :param locking_mode : the locking mode to be used
        :yield              : yield a lock object
        """
        lockstep = 1        
        filesize = 0

        if self._fp:
            filesize = getsize(self._fp)
        else:
            raise Exception("It requires attached a file before producin any lock!")

        if os.name == 'nt':
            # nt lock will not merge the ajacent locks
            lockstep = 0

        locklocator = locator(file_size=filesize, start=0, lock_length=1, step=lockstep, stop=0)
        
        for loc in locklocator:
            lock = NfvLock(loc[0], lock[1], mode, data)
            if self._isattached:
                lock.attch(self._fh)
            yield lock 


    def deploy_lock(self, start=0, step=1, length=1, \
            stop=1, mode='exclusive', data=None):
        """ strategically created multiple target locks, 
            which will attach status will sync up with NfvLockManager's attach status
        :param start        : the start offset of first lock to be set
        :param length       : the length of each lock to be created 
        :param step         : the interval of each adjacent locks
        :param end          : the start offset of last lock should not exceeded
        :param locking_mode : the locking mode to be used
        """
        if self._fp:
            filesize = getsize(self._fp)
        else:
            raise Exception("It requires attached a file before producin any lock!")

        lockstart = convert_size(start)
        locklen = convert_size(length)
        lockstop = convert_size(stop)
        lockstep = convert_size(step)
        lockmode = mode
        
        locklocator = locator(file_size=filesize, start=lockstart, \
                lock_length=locklen, step=lockstep, stop=lockstop)

        for loc in locklocator:
            lock =  NfvLock(offset=loc[0], length=loc[1], mode=lockmode, data=data)
            self._repository.add(lock)

        self.attach()


    @staticmethod 
    def locator(file_size=0, start=0, lock_length=1, step=1, stop=0):
        """ yield specific location a time the lock to be created on 
        :param start       : the start offset to lock
        :param lock_length : length of each byte-range
        :param step        : interval of each byte-range
        :param stop        : the stop offset to lock
        :yield             : yield a tuple comprised of (offset, length)
        """
        filesize = file_size
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

        for o in range(0, (numiterate+1)):
            activeoffset = start + o * (length+interval)
            if length + activeoffset <= filesize:
                yield (activeoffset, length)


    def wipe_lock(self):
        """ empty all locks from manager
        """
        self._fp = None
        self._fh = None
        self._isattached = False

        for lock in self._repository:
            lock.wipe()
            del lock

        self._repository.clear()


    def __iter__(self):
        """ iterator implementation
        """
        for lock in self._repository:
            yield lock



class NfvLock:
    """ NfvLock Class
    A class represent a lock (either a CIFS or NFS lock)
    """
    __slots__ = (
            '_filepath',
            '_filehandle',
            '_startoffset',
            '_stopoffset',
            '_length',
            '_mode',
            '_data',
            '_islocked',
            '_lockmode',
            '_isattached',
            '_property',
            '_id',
    )

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
            'unlock'           : ('r+b', msvcrt.LK_UNLCK),
        }
    else:
        sys.exit('Unsupported Platform! Only accepts NT and POSIX system.')


    def __init__(self, offset=0, length=1, mode='shared', data=None):
        """ constructor function
        :param offset : start offset of the lock 
        :param length : length of the lock 
        :param mode   : locking mode of the lock to be applied
        :param data   : the data used to write on the lock region, for data check
        """
        if mode not in self._LOCK_MODES.keys() or mode == 'unlock':
            raise ValueError("Given lock mode is invalid!")

        self._filepath =  None
        self._filehandle =  None
        self._startoffset = offset
        self._length = length
        self._stopoffset = offset + length - 1
        self._mode = mode.lower()
        self._data = data
        self._islocked = False
        self._isattached = False
        self._id = self._startoffset + self._stopoffset

        if data:
            self._data = data[:length]
        
        # property
        self._property = {
            'file'        : self._filepath,
            'offset'      : self._startoffset,
            'length'      : self._length,
            'mode'        : self._mode,
            'data'        : self._data,
            'is_locked'   : self._islocked,
            'is_attached' : self._isattached,
            'id'          : self._id,
        }


    def attach(self, file_handle):
        """ attach
        attach lock object to specific filehandle
        :param file_handle : file hanle to be atteched
        """
        if self._isattached:
            raise Exception("Current lock already attach, need to detach first")

        self._filehandle = file_handle
        self._filepath = file_handle.name
        self._isattached = True


    def detach(self):
        """ detach
        detach lock from file handle
        """
        if not self._islocked:
            self._filepath = None
            self._filehandle = None
            self._isattached = False
        else:
            raise Exception("Lock is on, can't be detached")


    def is_attached(self):
       """ is_attached
       return if current lock being attached to a file
       :return : attaching state of the lock
       """
       return self._isattached


    def is_locked(self):
       """ is_locked
       return if current lock's state (on/off)
       :return : locking state of the lock
       """
       return self._islocked


    def get_property(self, name=None):
        """ get_property
        get the value of given property
        :param name : name of property to be got
        :return     : value of given parameter name, 
                      if param name was not given, return all properies
        """
        if name is None:
            return self._property
        if name in self._property.keys():
            return self._property[name]
        else:
            raise Exception("Given property name not found")


    def on(self):
        """ switch on the lock
        """
        if not self.isattached:
            raise Exception("lock hasn't attached to any file")

        if self.islocked:
            raise Exception("Current lock has already switched on")
        
        if os.name == 'posix':
            self._posix_lock()
        elif os.name == 'nt':
            self._nt_lock()

        self._islocked = True


    def off(self):
        """ switch off the lock (unlock)
        """
        if not self.is_attached():
            raise Exception("lock hasn't attached to any file")

        if os.name == 'posix':
            self._posix_lock(lock_mode='unlock')
        elif os.name == 'nt':
            self._nt_lock(lock_mode='unlock')

        self._islocked = False 

    
    def wipe(self):
        """ delet current lock object
        """
        if self._isattached:
            if self._islocked:
                self.off()
        else:
            self.detach()


    def _nt_lock(self, lock_mode='shared'):
        """ _nt_lock
        manipulate NT byte-range lock
        :param lock_mode : the locking mode to be applied  
        """
        fh = self._filehandle
        mode = lock_mode
        offset = self._startoffset
        length = self._length
        data = self._data

        try:
            if data:
                if mode == 'exclusive_io' or mode == 'exclusive_blk_io':
                    fh.seek(offset)
                    msvcrt.locking(fh.fileno(), self._LOCK_MODES[mode][1], length)
                    # need to truncate extra content which exceeds end offset
                    fh.write(data)
                elif mode == 'shared' or mode == 'unlock':
                    fh.seek(offset)
                    readdata = fh.read(length) 
                    if fh.read(length) != data:
                        raise IOError("Data verification failed. expect:\
                                %s | actual: %s" % (data, readdata))
                    fh.seek(offset)
                msvcrt.locking(fh.fileno(), self._LOCK_MODES[mode][1], length)
            else:
                self._filehandle.seek(offset)  # this will change the position to offset
                msvcrt.locking(fh.fileno(), self._LOCK_MODES[mode][1], length)

        except Exception as e:
            raise Exception(e)
   

    def _posix_lock(self, lock_mode):
        """ posix_lock
        Create a posix byte-range lock
        :param lock_mode : the locking mode to be applied  
        """
        fh = self._filehandle
        mode = lock_mode 
        data = self._data
        lockdata = struct.pack('hhllhh', self._LOCK_MODES[mode][1], 0, offset, length, 0, 0)
        try:
            if withio:
                if mode == 'exclusive_io' or mode == 'exclusive_blk_io':
                    rv = fcntl.fcntl(fh, self._LOCK_MODES[mode][2], lockdata)
                    fh.seek(offset)
                    # truncate extra content which exceeds end offest
                    fh.write(data)
                elif mode == 'shared' or mode == 'unlock':
                    # NOTE
                    # the minimal size of kernel read is one page (4KB)
                    # hence the read may failed if target bytes
                    # which page was overlappped on other byte(s)
                    # owned by other lockowners
                    fh.seek(offset)
                    readdata = fh.read(len(self._data))
                    if readdata != data:
                        sys.exit("ERROR: data verification failed. expect: %s | actual: %s" % (data, readdata))
                rv = fcntl.fcntl(fh, self._LOCK_MODES[lockmode][2], lockdata)
            else:
                rv = fcntl.fcntl(fh, self._LOCK_MODES[lockmode][2], lockdata)
        except Exception as e:
            raise Exception(e)


