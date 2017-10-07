""" This module implements 2 primary class to manipulating file locks

:class NfvLockManager : a data structure represent managing bunch of file locks
:class NfvLock        : a data structure represent a file lock

Notes:
- One NfvLockManger object can attach one file obejct only
- One NfvLockManger object can manage multiple NfvLock obejcts
- One NfvLock object can attach one NfvFile Object only 

Layout:
--- NfvLockManger Object 1  ---attach---> |testfile1.txt|
        |--> NfvLocks object 1
        |--> NfvLocks object 2
        |--> NfvLocks object ... 
        |--> NfvLocks object (n-1)
--- NfvLockManger Object 2  ---attach---> |testfile2.txt|
        |--> NfvLocks object 1
        |--> NfvLocks object 2
        |--> NfvLocks object ... 
        |--> NfvLocks object (n-1)
...

--- NfvLockManger Object n-1 ---attach---> |testfile(n-1).txt|
        |--> NfvLocks object 1
        |--> NfvLocks object 2
        |--> NfvLocks object ... 
        |--> NfvLocks object (n-1)
"""

# standard modules
import os
import sys
import struct
import errno
import pdb
import random
import collections

from os.path import isfile, exists, getsize
# lock modules
if os.name == 'posix':
    import fcntl
    import struct
elif os.name == 'nt':
    import msvcrt

# NFV modules
from nfvtree import NfvTree, NfvFile, NfvIoTactic
if os.name == 'posix':
    import fcntl
    import struct
elif os.name == 'nt':
    import msvcrt



class NfvLockManager:
    """ a class designed to manage multiple NfvLock obejcts

    Support manipulating both NFS and CIFS locks
    Designed to manage multiple NfvLock objects on a NfvFile Object, 
    other than that, it's able to produce NfvFile object sequencially
    or stragitically, when it comes need multiple byte-range lock on
    a file, it could offer flexible and powerful privilege
    """


    def __init__(self, file=None, locks=[]):
        """ initialize self object 

        :param  file: a NfvFile object to be attach
        """
        self._file = None
        self._repository = set(locks)
        self._isattached = False

        if file is None:
            pass
        elif type(file) is NfvFile:
            self._file = file
            self._isattached = True
        elif isfile(file):
            self._file = file.get_property('path')
            self._isattached = True


    def add_lock(self, lock=None):
        """ add a existing NfvLock object

        it only add existing lock rather than creating new lock
        if manager object is attached a specific, the added lock
        will be attached automatically

        :param lock : lock object to be added to be managed
        :return     : *none*
        """
        if lock is not NfvLock:
            raise ValueError("Given lock is not NfvLock type object!")
        elif lock.isattached:
            raise ValueError("Given lock is attached, unable be added into NfvLockManager object ")
        else: 
            self._repository.add(lock)

        if self._isattached:
            lock.attach(self._file)


    def remove_lock(self, lock=None):
        """ remove a NfvLock object from NfvLockManager repository

        it only reomve lock from manager rather than deleting the lock object
        :param lock : NfvLock object to be removed, if it's None, 
                     a random lock will be removed
        :return     : NfvLock object was removed 
        """
        if lock is NfvLock and lock in self._repository:
            if lock.islocked:
                lock.off() # switch off
            elif lock.isattached():
                lock.detach() # detatch
            self._repository.remove(lock)
            return lock
        elif lock is None:
            return self._repository.pop()
        else:
            raise ValueError("Given NfvLock object is invalid!")


    def attach(self, file=None):
        """ attach lock manager objects to a NfvFile object

        :param  file : NfvFile object to be attached
        :return      : *none*
        """
        if self._isattached:
            raise Exception("Current NfvLogManager object already being attached")
        if type(file) is not NfvFile:
            raise Exception("Passed file is not a NfvFile object")

        self._file = file

        for lock in list(self._repository):
            lock.attach(file)

        self._isattached = True
        

    def detach(self):
        """ detach lock manager from a specific file

        all containing NfvLock object will be detached automatically
        :return : *none*
        """
        if not self._isattached:
            pass
        else:
            self._file = None
            for lock in list(self._repository):
                lock.detach()

    
    def create_lock(self, length=1, mode='exclusive', data=None):
        """ create one lock at a time

        generator function: sequencially create a NfvLock object 
        at a time, try best to produce maximu number of locks(which number
        depends on the size of attached file) which attach status will be 
        sync-ed up with NfvLockManager status

        :param start        : the start offset of first lock to be set
        :param length       : the length of each lock to be created 
        :param step         : the interval of each adjacent locks
        :param end          : the start offset of last lock should not exceeded
        :param locking_mode : the locking mode to be used
        :yield              : yield a lock object
        """
        lockstep = 1        
        filesize = 0
        lock = None

        if self._file.get_property('path'):
            filesize = getsize(self._file.get_property('path'))
        else:
            raise Exception("It requires attached a file before producin any lock!")

        if os.name == 'nt':
            # nt lock will not merge the ajacent locks
            lockstep = 0

        locklocator = self.locator(file_size=filesize, start=0, lock_length=1, step=lockstep, stop=0)
        for loc in locklocator:
            lock = NfvLock(loc[0], loc[1], mode, data)
            if self._isattached:
                lock.attach(self._file)
            self._repository.add(lock)
            yield lock 


    def deploy_lock(self, start=0, step=1, length=1, \
            stop=1, mode='exclusive', data=None):
        """ strategically created multiple target locks

        it will create multiple NfvFile objects on the attached file with 
        specific strategy user provided, or using default strategy if no 
        parameter was given

        :param start        : the start offset of first lock to be set
        :param length       : the length of each lock to be created 
        :param step         : the interval of each adjacent locks
        :param end          : the start offset of last lock should not exceeded
        :param locking_mode : the locking mode to be used
        :return             : *none*
        """
        if self._file.get_property('path'):
            filesize = getsize(self._file.get_property('path'))
        else:
            raise Exception("It requires attached a file before producing any lock!")

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


    def locator(self, file_size=0, start=0, lock_length=1, step=1, stop=0):
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
        self._file = None
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
        """ initialize self object

        :param offset : start offset of the lock 
        :param length : length of the lock 
        :param mode   : locking mode of the lock to be applied
        :param data   : the data used to write on the lock region, for data check
        :return       : *none*
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
        self._id = self._startoffset

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


    def attach(self, file):
        """ attach self object to a NfvFile object

        :param file : NfvFile object to be atteched
        :return     : *none*
        """
        if self._isattached:
            raise Exception("Current lock already attach, need to detach first")

        if type(file) is not NfvFile:
            raise Exception("Passed file is not a NfvFile object")

        self._filehandle = open(file.get_property('path'), 'r+b')
        self._filepath = file.get_property('path')
        self._isattached = True


    def detach(self):
        """ detach
        detach lock from file handle
        """
        if not self._islocked:
            self._filepath = None
            self._filehandle.close()
            self._filehandle=None
            self._isattached = False
        else:
            raise Exception("Lock is on, can't be detached")


    def is_attached(self):
       """ check if current lock being attached to a file

       :return : attaching state of the lock
       """

       return self._isattached


    def is_locked(self):
       """ check if current lock's state (on/off)

       :return : locking state of the lock
       """

       return self._islocked


    def get_property(self, name=None):
        """ get the value of given property

        :param name : name of property to be got
        :return     : value of given parameter name, if param 
                      name was not given, return all properies
        """
        if name is None:
            return self._property
        if name in self._property.keys():
            return self._property[name]
        else:
            raise Exception("Given property name not found")


    def on(self):
        """ switch on the lock

        :return : *none*
        """
        if not self._isattached:
            raise Exception("lock hasn't attached to any file")

        if self._islocked:
            raise Exception("Current lock has already switched on")
        
        if os.name == 'posix':
            self._posix_lock(lock_mode=self._mode)
            pass
        elif os.name == 'nt':
            self._nt_lock(lock_mode=self._mode)
            pass

        self._islocked = True


    def off(self):
        """ switch off the lock (unlock)

        :return : *none*
        """
        if not self.is_attached():
            raise Exception("lock hasn't attached to any file")

        if os.name == 'posix':
            self._posix_lock(lock_mode='unlock')
            pass
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


    def _nt_lock(self, lock_mode='exclusive'):
        """ manipulate NT byte-range lock

        it's considered as private method, do not use via object directely 

        :param lock_mode : the locking mode to be applied  
        :return          : *none*
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
   

    def _posix_lock(self, lock_mode='exclusive'):
        """ create a posix byte-range lock

        it's considered as private method, do not use via object directely 

        :param lock_mode : the locking mode to be applied  
        :return          : *none*
        """
        fh = self._filehandle
        mode = lock_mode
        data = self._data
        lockdata = struct.pack('hhllhh', self._LOCK_MODES[mode][1], 0, self._startoffset, self._length, 0, 0)
        try:
            if self._data:
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
                rv = fcntl.fcntl(fh, self._LOCK_MODES[mode][2], lockdata)
            else:
                rv = fcntl.fcntl(fh, self._LOCK_MODES[mode][2], lockdata)
        except Exception as e:
            raise Exception(e)

