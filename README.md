
Network Filesystem Validator (nfv_tree)
========================

NFV is a module designed to simulate E2E user scenarios based on manipulating file tree, which can be manipulated along with NFS, SMB and even local file systems.

With _nfv_tree_, manipulations regarding network filesystem could be more flexible and programmatic.

- Discreional files/directories deployment
- Manipulating files/diretories with more accessbilities
- Plaftform-crossed support (Windows and Linux)
- Alternate Data Stream supported
- File byte-range locks supported
- Rich and customizable data-pattern supported
- Innate user like test scenarios supported

### Platforms
- Windows 7 or above with python3 installed
- Linux with python3 installed

### Installation
_nfv_tree_ was published onto pypi, therefore you can install it from pip directly 
```
python -m pip install nfv_tree
Collecting nfv_tree
  Using cached nfv_tree-0.8.tar.gz
Installing collected packages: nfv-tree
  Running setup.py install for nfv-tree ... done
Successfully installed nfv-tree-0.8
```

### Usage
After installation, nfv_tree module is available for use, import it as usual before your using:
``` python
Python 3.6.1 (v3.6.1:69c0db5, Mar 21 2017, 17:54:52) [MSC v.1900 32 bit (Intel)] on win32
Type "help", "copyright", "credits" or "license" for more information.
>>> import nfv_tree.nfvtree
>>>
```

There are 6 primary classes defined in **nfv_tree** module
> _**NfvTree**_
> NfvTree is the fundamental class represent the file tree, which is comprised of multiple sub folders and NfvFile objects. NfvTree object support bunch of manipulations on containing files , such as _overwrite_, _copy_, _move_, _checksum_ etc.
> 
> _**NfvFile**_
> NfvFile is the class represents a file. NfvFile object support bunch of file manipulations on itself, such as _overwrite_, _copy_, _move_, _checksum_ etc.
>
> _**NfvIoTactic**_
> Tactic of the I/O to be adopted, including strategies of data pattern, seek type, io size etc.
>
> _**NfvLockManager**_
> A class designed to manager byte range locks, by which way, user could easily manage large number of locks with small snippet of code
> 
> _**NfvLock**_
> A class represents a byte range locks, which can be manipulate either independently or managed by NfvLockManager object

#### **_Sample: Basic File Tree Manipulations_**
 
``` python
from nfv_tree.nfvtree import NfvTree, NfvFile, NfvIoTactic

# Create a file tree with 3 tree width and 2 tree depth under directory test_dir\test_tree
mytree = NfvTree(tree_root="test_dir\test_tree", tree_width=3, tree_depth=2)

# Deploy 100 files with 1MB size in the file tree
mytree.create_file(number=100, size='1m')

# Tailor the number of files of the tree to 30
mytree.tailor(file_number=30)

# Tailor the number of containing file to 200 with size of incremental file 2 MB
mytree.tailor(file_number=200, file_size='2M')

# Create a NfvIoTactic object which adopts random data pattern
iot = NfvIoTactic(data_pattern='random')

# Apply the new i/o tactic
mytree.set_tactic(iot)

# overwrite with new i/o tactic
mytree.overwrite()
```
#### **_Sample: File Manipulations_**
``` python
from nfv_tree.nfvtree import NfvTree, NfvFile, NfvIoTactic

# Create a test file with 1MB file size
myfile = NfvFile(path="test_dir\test_file.txt", size='1M', io_tactic=NfvIoTactic())

# Checksum the file 
myfile.checksum()

# Report the checksum 
print(myfile.get_property('checksum'))

# Duplicate the file
copiedfile = myfile.copy(dest_path='copied_file.txt')

# Validate the checksum of copied_file.txt (should be the same as of test_file.txt)
print(copiedfile.get_property("checksum"))

# Overwrite the file with different data pattern, io size and seek mode
iot = NfvIoTactic(data_pattern='random', seek_type='reverse', io_size='3k')
myfile.set_tactic(iot)
myfile.overwirte()
```

#### **_Sample: Data Pattern Customization_**
``` python
from nfv_tree.nfvtree import NfvTree, NfvFile, NfvIoTactic

# build a compress data pattern with 90% compressible ratio
dp1 = NfvIoTactic.compress_pattern(comress_ratio=90, io_size='80k', chunk=10)

# build a data pattern with binary zero
dp2 = NfvIoTactic.hex_pattern(hex_value='00', io_size='10k')

# build a 20KB size data pattern with customized bits like '10000001'  
dp3 = NfvIoTactic.bit_pattern(bits='10000001', io_size='20k')

# compound all built data pattern together
dp = dp1 + dp2 + dp3

# initialize a NfvIoTactic object and set the data pattern
iot = NfvIoTactic()
iot.set_data_pattern(dp)

# create a file tree then create 100 files with assigned data pattern
mytree=(tree_root='test_dir\test_tree', io_tactic=iot)
mytree.tailor(file_number=100, file_size='1M')

```

#### **_Sample: File Lock Manipulations_**
``` python
from nfv_tree.nfvtree import NfvFile, NfvLock, NfvLockManager

# Create a file for later locking manipulation with default size 8k
myfile = NfvFile(path="test_file.txt", io_tactic=NfvIoTactic())

# Create a NfvLockManager object for managing multiple file locks
lckmgr = NfvLockManager()

# Attach lock manager to the file
lckmgr.attach(myfile)

# Produce 10 byte-range locks with each lock has 10 bytes of length 
lckgen = lckmgr.feed_lock(length=10)
for _ in range(10):
    next(lckgen)

# Switch on all 10 locks attached on the file
for lck in lckmgr:
    lck.on()
    
# Wait for 10 seconds then switch off the lock
import time
time.sleep(10)
for lck in lckmgr:
    lck.off()
    
```

#### **_Sample: Basic ADS Manipulation_**(TBD)


### Methods Overview

> NfvTree
> ``` python
> def create_file(size='8K', number=1, io_tactic=None):
> """ create a NfvFile object in NfvTree object
> 
> param size        : size of the file to be created 
> param number      : number of files to be created
> param io_tactic   : a NfvIoTactic object to be set for I/O manipulations
> return            : none
> """
> 
> def set_tactic(io_tactic=None):
> """ set the IO tactic to be adopted for IO manipulation
> 
> param io_tactic   : a NfvIoTactic object to be set for I/O manipulations
> return            : none
> """
> 
> def remove_file(number=1):
> """ remove NfvFile object in the NfvTree object
> 
> param number      : number of file to be removed
> return            : none
> """
> 
> def get_property(name=None):
> """ get value of given property of NfvTree object
> 
> param name        : the name of property which value to be retrieved 
> return            : value of given property
> """
> 
> def tailor(file_number=None, file_size='8k'):
> """ tailor the NfvFile objects in NfvTree object to expected number
> 
> param file_number : the number of NfvFile object to be tailored to
> param file_size   : the size of newly created NfvFile object in the NfvTree object
> return            : none
> """
> 
> def truncate(target_size=None):
> """ truncate the size of all NfvFile objects in the NfvTree object to given size
> 
> param size        : the size of NfvFile object to be truncated to
> return            : none
> """
> 
> def append(delta=None):
> """ append all NfvFile object in the NfvTree object
> 
> param delta       : the delta size to be appended
> return            : none
> """
> 
> def copy(dest_tree=None, name_length=8, name_seed=None):
> """ copy the NfvTree object 
> 
> param dest_tree   : the tree root path of destination NfvTree object, if it's None, the destination tree will be merged into current NfvTree object
> param name_length : the name of length of NfvFile objects of the  destination NfvTree object
> param name_seed   : the name seed of NfvFile objects of the  destination NfvTree object
> return            : the destination NfvTree object
> """
> 
> def rename(name_seed=None, name_length=8):
> """ rename the NfvFile object in the NfvTree object
> 
> param name_length : the name of length of NfvFile objects to be renamed to 
> param name_seed   : the name seed of NfvFile of the NfvFile object to be used when rename
> return            : none
> """
> 
> def overwrite():
> """ overwrite the data of NfvFile object of NfvTree object
> 
> return            : none
> """
> 
> def read():
> """ read the data of each NfvFile objects in the NfvTree object
> 
> return            : none
> """
> 
> def checksum(self, chunk_size=4096):
> """ checksum the data of NfvFile objects in NfvTree object
> return            : none
> """
> 
> def clear_file():
> """ clear all on-disk files with NfvTree object
> 
> return            : none
> """
> ```


> NfvFile
> ``` python
> def set_tactic(io_tactic=None):
> """ set the io tactic for I/O manipulation
> 
> param io_tactic   : the name of property which value to be retrieved 
> return            : value of given property
> """
>  
> def get_property(name=None):
> """ get value of given property of NfvIoTactic object
> 
> param name        : the name of property which value to be retrieved 
> return            : value of given property
> """
> 
> def truncate(target_size=None):
> """ truncate the size of all NfvFile object to given size
> 
> param size        : the size of NfvFile object to be truncated to
> return            : none
> """
> 
> def append(delta=None):
> """ append the size of NfvFile object
> 
> param delta       : the delta size to be appended
> return            : none
> """
> 
> def copy(dest_path=None, name_length=8, name_seed=None):
> """copy the NfvFile object
> 
> param dest_path   : the path of destination NfvFile object, if it's None, a random path will be used
> param name_length : the name of length of NfvFile objects of the  destination NfvFile object
> param name_seed   : the name seed of NfvFile objects of the destination NfvFile object
> return            : none
> """
> 
> def rename(name_seed=None, name_length=8):
> """ rename the NfvFile object
> 
> param name_length : the name of length of NfvFile objects to be renamed to
> param name_seed   : the name seed of NfvFile of the NfvFile object to be used when rename
> return            : none
> """
> 
> def overwrite():
> """ overwrite the data of NfvFile object 
> 
> return            : none
> """
> 
> def read():
> """ read the data of each NfvFile object
> 
> return            : none
> """
> 
> def checksum(chunk_size=4096):
> """ checksum the data of NfvFile objects in NfvTree object
> 
> return            : checksum value
> """
> 
> def create_ads(streams=None, size='8k'):
> """ create ADS stream on NfvFile object
> 
> param streams     : stream names to be created, accept dash and comma for easy input (ie: stream1-stream10, newstream)
> param size        : size of the each stream to be created
> return            : none
> """
> 
> def overwrite_ads(streams=None, size='8k'):
> """ overwrite ADS streams on NfvFile object
> 
> param streams     : stream names to be overwrote, accept dash and comma for easy input (ie: stream1-stream10, newstream)
> param size        : size of the each stream to be overwrote
> return            : none
> """
> 
> def remove_ads(streams=None):
> """ remove ADS streams on NfvFile object
> 
> param streams     : stream names to be removed, accept dash and comma for easy input (ie: stream1-stream10, newstream)
> return            : none
> """
> ```

> NfvIoTactic
> ``` python
> def set_property(self, attrs={}):
> """ set the property of NfvIoTactic object
> 
> param attrs        : a dict object contains key-value pairs of properties to be set
> return             : none
> """
> 
> def get_property(name=None):
> """ get value of given property of NfvIoTactic object
> 
> param name         : the name of property which value to be retrieved 
> return             : value of given property
> """
> 
> def get_data_pattern(self):
> """ get current data pattern of the NfvIoTactic object
> 
> return             : value of the data pattern
> """
> 
> def set_data_pattern(self, data=None):
> """ set data pattern of NfvIoTactic object
> param data         : the data pattern to be applied to the NfvIoTactic object
> return             : value of the data pattern
> """
> 
> def clear_data_pattern(self):
> """ clear the data pattern in current NfvIoTactic object
> 
> return             : none
> """
> 
> @staticmethod 
> def fixed_pattern(pattern=None, io_size='8k'):
> """ build  a fixed data pattern with given io_size
> 
> param pattern      : the pattern template used to build data pattern
> param io_size      : the size of data pattern to be built
> return             : value of the data pattern just built
> """
> 
> @staticmethod 
> def random_pattern(io_size='8k'):
> desc.              : build a random data pattern with given io_size
> param io_size      : the size of data pattern to be built
> return             : value of the data pattern just built
> """
> 
> @staticmethod
> def hex_pattern(hex_value='00', io_size='8k'):
> """ build a data pattern with given io_size which is customizable in hex value
> 
> param hex_value    : the patten template in hex value
> return             : value of the data pattern just built
> """
> 
> @staticmethod 
> def bit_pattern(bits='00000000', io_size='8k'):
> """ build a data pattern with given io_size which is customizable in bit wise
> 
> param bits         : the specific 8 long bits to be used as template for buiding data pattern
> return             : value of the data pattern just built
> """
> 
> @staticmethod 
> def compound_pattern(contanier=None, pattern_func=None, *args, **kwargs):
> """ build a data pattern which compounded on top of existing data pattern(s)
> 
> param container    : a variable used for maintaining existing data pattern and data pattern built by current method
> param pattern_func : function object used for building data pattern
> param *args        : the array arguments passed for pattern builder function
> param **kwargs     : the keywords arguments passed for pattern builder function
> return             : value of the data pattern just built and compounded
> """
> ```


> NfvLockManager
> ``` python
> def add_lock(lock=None):
> """ add an existing NfvLock object to NfvLockManager object
> 
> param lock   : NfvLock object to be added
> return       : none
> """
> 
> def remove_lock(lock=None):
> """ remove an existing NfvLock object from NfvLockManager object
> 
> param lock   : NfvLock object to be removed, if it's None, will randomly remove one
> return       : none
> """
> 
> def attach(file=None):
> """ attach to a NfvFile object
> 
> param file   : NfvFile object to be attached on
> return       : none
> """
> 
> def detach():
> """ dettach from a NfvFile object
> 
> param file   : NfvFile object to be dettached from
> return       : none
> """
> 
> def get_property(name=None):
> """ get the value(s) of property of NfvLockManager object
> 
> param name   : name of target property to be retrieved, if it's None, a dict containing all properties will be returned
> return       : value of the given property
> """
> 
> def feed_lock(start=0, length=1, step=1, end=0, mode='exclusive', data=None):
> """ a generator function for feeding NfvLock objects
> 
> param start  : start offset the first lock object locates
> param length : length in bytes of lock object to be feeded
> param step   : the interval between adjacent lock object on the file
> param end    : end offset the last lock object locates
> param mode   : locking mode to be set (exclusive/shared/exclusive_blk)
> yield        : a NfvLock object
> """
> 
> def deploy_lock(start=0, step=1, length=1, stop=1, mode='exclusive', data=None):
> """ function for creating NfvLock objects within NfvLockManager object
> 
> param start  : start offset the first lock object locates
> param length : length in bytes of lock object to be feeded
> param step   : the interval between adjacent lock object on the file
> param end    : end offset the last lock object locates
> param mode   : locking mode to be set (exclusive/shared/exclusive_blk)
> return       : none
> """
> 
> def wipe_lock():
> """ wipe all NfvLock object managed by NfvLockManager object
> 
> return       : none
> """
> ```
> 
> NfvLock
> ``` python
> def attach(file=None):
> """ attach NfvLock object onto a NfvFile obejct
> 
> param file : NfvFile object be attached
> return     : none
> """
> 
> def detach():
> """ detach NfvLock object from its attached NfvFile object
> 
> return     : none
> """
> 
> def is_attached():
> """ check if current NfvLock is attached on NfvFile object already
> 
> return     : True or False
> """
> 
> def is_locked():
> """ check if current NfvLock is ON of OFF
> 
> return     : True or False
> """
> 
> def get_property(name=None):
> """ get the value of given property
> 
> param name : name of the property to be retrieved
> return     : value of property given
> """
> 
> def on():
> """ switch on the lock
> 
> return     : none
> """
> 
> def off():
> """ switch off the lock
> 
> return     : none
> ```
