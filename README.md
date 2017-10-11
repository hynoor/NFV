
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

### Installation
_nfv_tree_  was published onto pypi, that means you can install from pip directly 
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
> Tactic of the I/O to be adopted, including data_pattern, seek_type, io_size etc.
>
> _**NfvLockManager**_
> A class designed to manager byte range locks, by which way, user could easily manage large number of locks with small snippet of code
> 
> _**NfvLock**_
> A class represent a byte range locks, which can be manipulate either independently or managed by NfvLockManager object

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
> 
> create_file(size='8K', number=1, io_tactic=None)
> desc.           : create a NfvFile object in NfvTree object
> param size      : size of the file to be created 
> param number    : number of files to be created
> param io_tactic : a NfvIoTactic object to be set for I/O manipulations
> return          : none
> 
> set_tactic(io_tactic=None)
> desc.           : set the IO tactic to be adopted for IO manipulation
> param io_tactic : a NfvIoTactic object to be set for I/O manipulations
> return          : none
> 
> remove_file(number=1)
> desc.           : remove NfvFile object in the NfvTree object
> param number    : number of file to be removed
> return          : none
> 
> get_property(name=None)
> desc.       : get value of given property of NfvTree object
> param name  : the name of property which value to be retrieved 
> return      : value of given property
> 
> tailor(file_number=None, file_size='8k')
> desc.             : tailor the NfvFile objects in NfvTree object to expected number
> param file_number : the number of NfvFile object to be tailored to
> param file_size   : the size of newly created NfvFile object in the NfvTree object
> return            : none
> 
> truncate(target_size=None)
> desc.      : truncate the size of all NfvFile objects in the NfvTree object to given size
> param size : the size of NfvFile object to be truncated to
> return     : none
> 
> append(delta=None)
> 
> copy(dest_tree=None, name_length=8, name_seed=None)
> 
> rename(name_seed=None, name_length=8)
> 
> overwrite()
> 
> read()
> 
> checksum(self, chunk_size=4096)
> 
> clear_file()
> ```

> NfvFile
> ``` python
> set_tactic(tactic=None)
> 
> get_property(name=None)
> desc.       : get value of given property of NfvIoTactic object
> param name  : the name of property which value to be retrieved 
> return      : value of given property
> 
> truncate(target_size=None)
> 
> append(delta=None)
> 
> copy(dest_tree=None, name_length=8, name_seed=None)
> 
> rename(name_seed=None, name_length=8)
> 
> overwrite()
> 
> read()
> 
> checksum(chunk_size=4096)
> 
> create_ads(streams=None, size='8k')
> 
> overwrite_ads(streams=None, size='8k')
> 
> remove_ads(streams=None)
> 
> ```

> NfvIoTactic
> ``` python
> set_property(self, attrs={})
> desc.       : set the property of NfvIoTactic object
> param attrs : a dict object contains key-value pairs of properties to be set
> return      : none
> 
> get_property(name=None)
> desc.       : get value of given property of NfvIoTactic object
> param name  : the name of property which value to be retrieved 
> return      : value of given property
> 
> get_data_pattern(self)
> desc.       : get current data pattern of the NfvIoTactic object
> return      : value of the data pattern
> 
> set_data_pattern(self, data=None)
> desc.       : set data pattern of NfvIoTactic object
> param data  : the data pattern to be applied to the NfvIoTactic object
> return      : value of the data pattern
> 
> clear_data_pattern(self)
> desc.       : clear the data pattern in current NfvIoTactic object
> return      : none
> 
> fixed_pattern(pattern=None, io_size='8k') : static_method
> desc.         : build  a fixed data pattern with given io_size
> param pattern : the pattern template used to build data pattern
> param io_size : the size of data pattern to be built
> return        : value of the data pattern just built
> 
> random_pattern(io_size='8k') : static_method
> desc.         : build a random data pattern with given io_size
> param io_size : the size of data pattern to be built
> return        : value of the data pattern just built
> 
> hex_pattern(hex_value='00', io_size='8k') : static_method
> desc.           : build a data pattern with given io_size which is customizable in hex value
> param hex_value : the patten template in hex value
> return          : value of the data pattern just built
> 
> bit_pattern(bits='00000000', io_size='8k') : static_method
> desc.           : build a data pattern with given io_size which is customizable in bit wise
> param bits      : the specific 8 long bits to be used as template for buiding data pattern
> return          : value of the data pattern just built
> 
> compound_pattern(contanier=None, pattern_func=None, *args, **kwargs) : static_method
> desc.              : build a data pattern which compounded on top of existing data pattern(s)
> param container    : a variable used for maintaining existing data pattern and data pattern built by current method
> param pattern_func : function object used for building data pattern
> param *args        : the array arguments passed for pattern builder function
> param bits         : the keywords arguments passed for pattern builder function
> return             : value of the data pattern just built and compounded
> ```


> NfvLockManager
> ``` python
> add_lock(lock=None)
> desc.      : add an existing NfvLock object to NfvLockManager object
> param lock : NfvLock object to be added
> return     : none
> 
> remove_lock(lock=None)
> desc.      : remove an existing NfvLock object from NfvLockManager object
> param lock : NfvLock object to be removed, if it's None, will randomly remove one
> return     : none
> 
> attach(file=None)
> desc.      : attach to a NfvFile object
> param file : NfvFile object to be attached on
> return     : none
> 
> detach()
> desc.      : dettach from a NfvFile object
> param file : NfvFile object to be dettached from
> return     : none
> 
> get_property(name=None)
> desc.      : get the value(s) of property of NfvLockManager object
> param name : name of target property to be retrieved, if it's None, a dict containing all properties will be returned
> return     : value of the given property
> 
> feed_lock(start=0, length=1, step=1, end=0, mode='exclusive', data=None)
> desc.        : a generator function for feeding NfvLock objects
> param start  : start offset the first lock object locates
> param length : length in bytes of lock object to be feeded
> param step   : the interval between adjacent lock object on the file
> param end    : end offset the last lock object locates
> param mode   : locking mode to be set (exclusive/shared/exclusive_blk)
> yield        : a NfvLock object
> 
> deploy_lock(start=0, step=1, length=1, stop=1, mode='exclusive', data=None)
> desc.        : function for creating NfvLock objects within NfvLockManager object
> param start  : start offset the first lock object locates
> param length : length in bytes of lock object to be feeded
> param step   : the interval between adjacent lock object on the file
> param end    : end offset the last lock object locates
> param mode   : locking mode to be set (exclusive/shared/exclusive_blk)
> return       : none
> 
> wipe_lock()
> desc.        : wipe all NfvLock object managed by NfvLockManager object
> return       : none
> ```

> NfvLock
> ``` python
> attach(file=None)
> desc.      : attach NfvLock object onto a NfvFile obejct
> param file : NfvFile object be attached
> return     : none
> 
> detach()
> desc.      : detach NfvLock object from its attached NfvFile object
> return     : none
> 
> is_attached()
> desc.      : check if current NfvLock is attached on NfvFile object already
> return     : True or False
> 
> is_locked()
> desc.      : check if current NfvLock is ON of OFF
> return     : True or False
> 
> get_property(name=None)
> desc.      : get the value of given property
> param name : name of the property to be retrieved
> return     : value of property given
> 
> on()
> desc.      : switch on the lock
> return     : none
> 
> off()
> desc.      : switch off the lock
> return     : none
> ```
