
Network Filesystem Validator (nfv_tree)
========================

NFV is a module designed to simulate end to end test scenarios regarding file tree, which can be manipulated along with NFS, SMB even local file systems

### Installation
_nfv_tree_  was published onto pypi, that means you can install from pip directly 
```
python -m pip install nfv_tree
Collecting nfv_tree
  Using cached nfv_tree-0.7.tar.gz
Installing collected packages: nfv-tree
  Running setup.py install for nfv-tree ... done
Successfully installed nfv-tree-0.7
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
> **NfvTree**
> NfvTree is the fundamental class represent the file tree, which is comprised of multiple sub folders and NfvFile objects. NfvTree object support bunch of manipulations on containing files , such as _overwrite_, _copy_, _move_, _checksum_ etc.
> 
> **NfvFile**
> NfvFile is the class represents a file. NfvFile object support bunch of file manipulations on itself, such as _overwrite_, _copy_, _move_, _checksum_ etc.
>
> **NfvIoTactic**
> Tactic of the I/O to be adopted, including data_pattern, seek_type, io_size etc.
>
> **NfvLockManager**
> A class designed to manager byte range locks, by which way, user could easily manage large number of locks with small snippet of code
> 
> **NfvLock**
> A class represent a byte range locks, which can be manipulate either independently or managed by NfvLockManager object

 - **Basic File Tree Manipulations**
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
- **Basic File Manipulations**
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

- **Basic File Lock Manipulations**

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
for _ in lckgen:
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


- **Basic ADS Manipulation**



### Methods Overview (TBD)

