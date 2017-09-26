""" nfvtree.py implemented fundamental data structures of file tree, file and I/O tactic
"""

import os
import sys
import pdb
import re
import copy

from shutil import copyfile, move, rmtree
from hashlib import md5
from random import randint, shuffle
from os import path, makedirs, listdir, walk
from os.path import exists, join, getsize
from collections import namedtuple, defaultdict
from itertools import cycle
from nfv_utils.utils import convert_size, random_string, encipher_data



class NfvTree:
    """ Defines a tree structure like data structure and related methods

    NfvTree is a file tree which composed of directories and files
    directories within NfvTree are orgnized by with and depth which 
    represent how many sub folders in a sub-directory and what's the 
    depth of the sub-directories
    """
    __slots__ = (
            '_root',
            '_width', 
            '_depth', 
            '_files', 
            '_filesperdir', 
            '_treesize',
            '_dirs',
            '_dirlen',
            '_property',
            '_iotactic',
    )

    def __init__(self, tree_root=None, tree_width=1, tree_depth=1, dir_length=8):
        """ Constructor for instaniating a empty file tree

        Each NfvTree object should have a set of attributes as below,
        for any I/O related operations, a NfvIoTactic object is required
        for regulates the specific I/O strategy, such as data_pattern,
        seek type etc.
 
        :param tree_root  : root directory of file tree
        :param tree_width : the width of file tree
        :param tree_depth : the depth of file tree
        :param dir_length : the length of a sub folder name
        :return           : NfvTree object
        """
        self._root = tree_root
        self._width = tree_width
        self._depth = tree_depth
        self._files = set()
        self._dirs = set()
        self._treesize = 0 
        self._dirlen = 0  
        self._iotactic = NfvIoTactic()

        if tree_root is None:
            raise ValueError("ERROR: Paramter tree_root is required!")
        if exists(tree_root):
            self.load_tree(self._root)
        else:
            self.new(self._root, self._width, self._depth)


    def new(self, dir=None, tree_width=1, tree_depth=1):
        """ initialize a tree object
        
        this function will be called for creating a new file tree

        :param tree_width : the width of file tree
        :param tree_depth : the depth of file tree
        """
        width = tree_width
        depth = tree_depth

        for _ in range(width):
            entry = join(dir, random_string(8))
            makedirs(entry)
            self._dirs.add(entry)

        if depth > 0:
            for d in listdir(dir):
                self.new(dir=join(dir, d), tree_width=width, tree_depth=depth-1)


    def update(self):
        """ update some fundamental attributes of file tree
        
        So far, only _treesize will be re-calcualted 
        """      
        self._treesize = 0
        for f in self._files:
            self._treesize += f.get_property('size')
        

    def create_file(self, size='8K', number=1, io_tactic=None):
        """ create file(s) with given io tactic 
        
        This method will create new on-disk file with user given tactic
        """
        if io_tactic is None and self._iotactic is None: 
            raise ValueError("ERROR: need io_tactic specific before any I/O operation!")
        elif self._iotactic is None and io_tactic is not None:
            self._iotactic = io_tactic
        elif self._iotactic and io_tactic:
            self._iotactic = io_tactic

        for _, dir in zip(range(number), cycle(self._dirs)):
            self._files.add(NfvFile(path=join(dir, random_string(8)), size=size, io_tactic=self._iotactic))
        
        self.update()


    def load_tree(self, tree_root=None):
        """ load an existing on-disk file tree into memory

        If given tree_root exists already, load the which
        into memory instead of creating new one

        :param tree_root : root path of file tree
        :return          : NfvTree object
        """
        if not exists(tree_root):
            raise Exception("Given dir %s doesn't exist!" % tree_root)

        for dirpath, dirs, files in walk(tree_root):
            for filename in files:
                fullname = join(dirpath, filename)
                self._files.add(NfvFile(path=fullname))
            for dirname in dirs:
                self._dirs.add(join(dirpath, dirname))

        # initialize io tactic
        for f in self._files:
            f.set_tactic(self._iotactic)

        self.update()


    def set_tactic(self, tactic=None):
        """ set io tactic for the file tree

        attach a NfvIoTactic object to current file tree,
        which could leverage the tactic to do I/O operation

        :param tactic : NfvIoTactic object
        :return       : *none*
        """
        if type(tactic) is not NfvIoTactic:
            raise ValueError("ERROR: Given parameter tactic is not NfvIoTactic object!")
        self._iotactic = tactic
        
    
    def remove_file(self, number=1):
        """ remove files from tree randomly
        
        Remove user specified number of files within  file tree,
        all files chosen by random

        :param number : number of file to be removed
        :param file   : NfvFile object
        :return       : *none*
        """
        for f in range(number):
            try: 
                self._files.pop().remove()
            except Exception as e:
                if re.search('pop from an empty set', str(e)):
                    pass
                else:
                    raise Exception(e)
        self.update()


    def get_property(self, name=None):
        """ get the value of given property

        Retrieves the attribute value which name given by user

        :param name : name of property to be retrieved
        :return     : value of given parameter name, if param name was not given, 
                    : all properties will be returned
        """
        properties = {
            'root'        : self._root,
            'width'       : self._width,
            'depth'       : self._depth,
            'tree_size'   : self._treesize,
            'file_number' : len(self._files),
            'dir_number'  : len(self._dirs),
        } 

        if name is None:
            return properties
        if name in properties.keys():
            return properties[name]
        else:
            raise Exception("Given property name not found")
    

    def tailor(self, file_number=None, file_size='8k'):
        """ tailor the total number of files within file tree

        Expand or shrink the number of files within file tree
        to given value, if given file_number is larger than existing,
        all extra file will be created accroding to given file_size
        and attached NfvIoTactic object

        :param file_number : number of files to be tailord to
        :param file_size   : size of file which to be added
        :retrun            : *none*
        """
        deltanum = abs(file_number - len(self._files))
        if file_number > len(self._files):
            self.create_file(number=deltanum, size=file_size)
        if file_number < len(self._files):
            self.remove_file(number=deltanum)

        self.update()


    def truncate(self, file_size=None):   
        """ truncate the on-disk file tree to specific size

        :param file_size : size of each file to be truncated to
        :return          : *none*
        """
        if file_size is None:
            pass
        else:
            file_size = convert_size(file_size)

        for f in self._files:
            f.truncate(file_size)
        
        self.update()


    def append(self, delta=None):
        """ append the on-disk file tree

        Append the file with data, which regulated by attach NfvIoTactic object

        :param delta : delta size of to be appended
        :return     : *none*
        """
        pass


    def copy(self, dest_tree=None, name_length=8, name_seed=None):
        """ copy the on-disk files within tree to another path

        :param dest_tree : destination path the file to be copied to,
                           which will be auto created if doesn't exist.
                           if dest_tree is None, all files will be copied within
                           the file tree itself.
        :return          : a copied NfvTree object or self with copied within self
        """
        if dest_tree is None:
            dest_tree = self._root
            tmpset = set()
            for f in self._files:
                tmpset.add(f.copy(name_length=name_length, name_seed=name_seed))
            self._files = self._files.union(tmpset) 
            self.update()
            return self
        else:
            makedirs(dest_tree)
            for d in self._dirs:
                dstdir = d.replace(self._root, dest_tree)
                if not exists(dstdir):
                    makedirs(dstdir)
            desttree = NfvTree(tree_root=dest_tree)
            desttree._iotactic = self._iotactic
            for f in self._files:
                destpath = f._path.replace(self._root, dest_tree)
                desttree._files.add(f.copy(destpath))

            self.update()
            return  desttree


    def rename(self, name_seed=None, name_length=8):
        """ rename all on-disk file within file tree

        :param name_length : destination 
        :return          :  NfvFile object just been removed
        """
        tmpset = set()
        for f in self._files:
            f.rename(name_length, name_seed)
        
        self.update()


    def checksum(self):
        """ checksum all the on-disk files within file tree

        :return  : *none*
        """
        for f in self._files:
            f.checksum()


    def overwrite(self):
        """ overwrite the on-disk file tree

        :return  : *none*
        """
        if self._iotactic is None:
            raise ValueError("Error: parameter tactic is required!")
        
        for f in self._files:
            f.set_tactic(self._iotactic)
            f.overwrite()


    def read(self):
        """ read the data of on-disk file

        :return  : *none*
        """
        for f in self._files:
            f.read()
    

    def clear_file(self):
        """ clear all on-disk files within tree

        :return  : *none*
        """
        try:
            while True:
                f = self._files.pop()
                f.remove()
        except KeyError as e:
            if re.search('pop from an empty set', str(e)):
                pass
            else:
                raise KeyError(e)


    def wipe(self):
        """ wipe the entire tree and including its containing files

        """        
        # clear files
        for f in self._files:
            f.remove()
        self._files = {}
        # clear dirs
        rmtree(self._root)
        self._dirs = {}
  

    def __iter__(self):
        """ iterator implemention

        when caller iterates the NfvTree object, which will yield 
        the containing file object randomly 
        """
        for f in self._files:
            yield f

   

class NfvFile:
    """ represent a file object
    """
    __slots__ = ('_path', '_size', '_inode', '_dir', '_name', '_checksum', '_uid', '_iotactic')

    _io_check_db = defaultdict(lambda : None)

    def __init__(self, path=None, size='8k', io_tactic=None):
        """ initialize a NfvFile object
        :param path      : path of the on-disk file to be initialized
        :param size      : size of the file to be initialized (when creates a new file)
        :param io_tactic : NfvIoTactic object to be used for I/O operation
        :return          : NfvFile object
        """
        if path is None:
            raise ValueError("Error: parameter file_path is required!")
        self._path = path 
        self._size = convert_size(size)
        self._checksum = None
        self._iotactic = io_tactic
        self._dir, self._name = os.path.split(path)

        if not exists(path):
            self.new()
        else:
            self.load_file(path)


    def new(self, open_mode='create'):
        """ craete a NfvFile on-disk file object
        :return : *none*
        """
        if self._iotactic is None:
            raise ValueError("Error: parameter tactic is required!")
        openmode = 'w+b' 
        if open_mode == 'overwrite':
            openmode = 'rb+'
        numwrite = self._size // self._iotactic.get_property('io_size')
        remainder = self._size % self._iotactic.get_property('io_size')
        indexsupplier = self._iotactic.seek_to(self._size)
        if remainder > 0:
            rindex = next(indexsupplier)
        with open(self._path, openmode) as fh:
            if remainder > 0 and self._iotactic._seek == 'reverse':
                data = self._iotactic.get_data()
                if self._iotactic._datacheck:
                    NfvFile._io_check_db[encipher_data(data, NfvFile._io_check_db)] = True
                fh.seek(rindex)
                fh.write(data[:remainder])
            for idx in indexsupplier:
                data = self._iotactic.get_data()
                if self._iotactic._datacheck:
                    NfvFile._io_check_db[encipher_data(data, NfvFile._io_check_db)] = True
                fh.seek(idx)
                fh.write(data)
            if remainder > 0 and (self._iotactic._seek == 'seq' or self._iotactic._seek == 'random'):
                data = self._iotactic.get_data()
                if self._iotactic._datacheck:
                    NfvFile._io_check_db[encipher_data(data, NfvFile._io_check_db)] = True
                fh.seek(rindex)
                fh.write(data[:remainder])

        if self._iotactic._datacheck:
            self._verify_file()
   

    def _verify_file(self):
        """ verfiy the data of on-disk file (do not use it directly on a NfvFile object)
        :return : *none*
        """
        numread = self._size // self._iotactic.get_property('io_size')
        with open(self._path, 'rb') as fh:
            while numread > 0:
                if not NfvFile._io_check_db[encipher_data(fh.read(self._iotactic._iosize))]:
                    print('database dump: %s' % NfvFile._io_check_db)
                    raise Exception("ERROR: data check failed!")
                numread -= 1

        # rest db to release resource 
        NfvFile._io_check_db = {}


    def load_file(self, path):
        """ load an existing on-disk file and initialize a NfvFile object
        :param path : path of the on-disk file
        :return     : *none*
        """
        self._size = getsize(path) 
        self._dir, self._name = os.path.split(path)

  
    def get_property(self, name=None):
        """ get the value of given property
        :param name : name of property to be retrieved
        :return     : value of given parameter name, if param name was not given, return all properies
        """
        properties = {
                'path'       : self._path,
                'name'       : self._name,
                'size'       : self._size,
                'directory'  : self._dir,
                'checksum'   : self._checksum,
        }

        if name is None:
            return properties
        if name in properties.keys():
            return properties[name]
        else:
            raise Exception("Given property name not found")


    def set_tactic(self, tactic=None):
        """ set the tactic for file I/O manipulations
        :param io_tactic : NfvIoTactic object
        :return          : *none*
        """
        if tactic is None:
            raise ValueError("ERROR: parameter io_tactic must be a NfvIoTactic object!")
        self._iotactic = tactic


    def truncate(self, size=None):   
        """ truncate the on-disk to specific size
        :param size : size to be truncated to
        :return     : *none*
        """
        if size is None:
            pass
        else:
            size = convert_size(size)
            with open(self._path, 'ab') as fh:
                fh.truncate(size)

        self._size = getsize(self._path) 


    def copy(self, dest_path=None, name_length=8, name_seed=None):
        """ copy the on-disk file to another path
        :param dest_path : destination path the file to be copied to, if it's not 
                           provided, use current dir as destination  folder
        :return          : NfvFile object just been copied
        """
        if dest_path is None:
            dest_path = join(self._dir, random_string(8))
        try:
            cfile = copy.deepcopy(self)
            copyfile(self._path, dest_path)
            cfile = NfvFile(dest_path)
        except Exception as e:
            raise Exception(e)
           
        return cfile


    def rename(self, name_length=8, name_seed=None):
        """ move on-disk file to another path
        :param name_seed   : seed for constitution a file name
        :param name_length : length of new file name
        :return            : *none*
        """
        try:
            newpath = join(self._dir, random_string(name_length, name_seed))
            move(self._path, newpath)
            self._path = newpath
        except Exception as e:
            raise Exception(e)


    def overwrite(self):
        """ overwrite the on-disk file
        :return  :  NfvFile object just been rewrote
        """
        self.new(open_mode='overwrite')
        # update checksum
        if self._checksum is not None:
            self.checksum()


    def read(self):
        """ read the data of on-disk file
        :return  : *none*
        """
        numread = self._size // self._iotactic._iosize
        remainder = self._size % self._iotactic._iosize

        indexsupplier = self._iotactic.seek_to(self._size)
        if remainder > 0:
            rindex = next(index_supplier) # get index of remainder
        with open(self._path, 'rb') as fh:
            if remainder > 0 and self._seek == 'reverse':
                fh.seek(rindex)
                fh.read(remainder)
            for idx in indexsupplier:
                fh.seek(idx)
                fh.read(self._iotactic._iosize)
            if remainder > 0 and (self._seek == 'seq' or self._seek == 'random'):
                fh.seek(rindex)
                fh.read(remainder)

   
    def checksum(self, chunk_size=4096):
        """ checksum the data of on-disk file
        :return  : *none*
        """
        if chunk_size > self._size:
            chunk_size = self._size

        hashmd5 = md5()
        with open(self._path, 'rb') as fh:
            for chunk in iter(lambda : fh.read(chunk_size), b""):
                hashmd5.update(chunk)

        self._checksum = hashmd5.hexdigest()

  
    def remove(self):
        """ remove the ondisk file
        :return  : *none*
        """
        try: 
            os.remove(self._path)
        except IOError as e:
            raise IOError(e)
        
        del self


class NfvIoTactic:
    """ Nfv I/O Tactic 
    the class defines the tactic of I/O
    """ 
    __slots__ = ('_iosize', '_datapattern', '_seek', '_property', '_data', '_datacheck')
    _seeks = ('seq', 'random', 'reverse')
    _patterns = ('fixed', 'random')
    _datagranary = os.urandom(1048576)  # 1MB size data granary for random data pattern

    def __init__(self, io_size='8k', data_pattern='fixed', seek_type='seq', data_check=True):
        """ NfvIoTactic constructor
        :param io_size      : io size of tactic to be adopted
        :param data_pattern : data pattern of io tactic to be adopted
        :param seek_type    : seek type of tactic to be adopted
        :param data_check   : a bool flag indicates if perform immediate data check on each file
        :return             : NfvIoTactic object
        """
        if seek_type not in self._seeks:
            raise ValueError("ERROR: Given seek_type %s is invalid!" % seek_type)
        if data_pattern not in self._patterns:
            raise ValueError("ERROR: Given data_pattern %s is invalid!" % data_pattern)

        self._iosize = convert_size(io_size)
        self._datapattern = data_pattern
        self._seek = seek_type
        self._data = None
        self._datacheck = data_check
        if self._datapattern == 'random':
            self.random_pattern()
        elif self._datapattern == 'fixed':
            self.fixed_pattern()
            

    def set_property(self, attrs={}):
        """ set given properties
        :param attrs : a dict contains the property-value pairs to be set
        :return      : *none*
        """
        properties = {
            'io_size'      : '_iosize',
            'data_pattern' : '_datapattern',
            'seek_type'    : '_seek',
            'data_check'   : '_datacheck',
        }
        if type(attrs) is not dict:
            raise ValueError("ERROR: dictinonary param 'attrs' is required!")
        for key, value in attrs.items():
            if key in properties.keys():
                setattr(self, properties[key], value)
            else:
                raise Exception("Given property name not found")

        self._iosize = convert_size(self._iosize)


    def get_property(self, name=None):
        """ get the value of given property
        :param name : name of property to be retrieved
        :return     : value of given parameter name, if param name was not given, return all properies
        """
        properties = {
            'io_size'      : self._iosize,
            'data_pattern' : self._datapattern,
            'seek_type'    : self._seek,
            'data_check'   : self._datacheck,
        }
        if name is None:
            return properties
        if name in properties.keys():
            return properties[name]
        else:
            raise Exception("Given property name not found")


    def get_data(self):
        """ renew data for each I/O 
        :return : *none*
        """
        if self._datapattern == 'random':
            self.random_pattern()
        elif self._datapattern == 'fixed':
            # every time it'll renew a fixed data
            # this should be a place needs to be enhanced
            self.fixed_pattern()

        return self._data


    def random_pattern(self):
        """ renew self._data with random data pattern
        :return : *none*
        """
        self._data = self.get_rand_buffer(self._iosize, self._datagranary)


    def fixed_pattern(self, pattern=None):
        """ renew the fixed pattern
        :return : *none*
        """
        tmpbytes = bytes('This is a string used for NFV testing', encoding='utf_8')
        if pattern is not None:
            tmpbytes = bytes(pattern, encoding='utf_8')

        if len(tmpbytes) >= self._iosize:
            self._data = tmpbytes[:self._iosize]
        else:
            number = self._iosize // len(tmpbytes)  
            remainder = tmpbytes[:self._iosize % len(tmpbytes)]
            self._data = tmpbytes * number + remainder 


    @staticmethod
    def get_rand_buffer(size, buffer):
        """ randomly grab a piece of random bytes of data
        :param size   : size of data to be fetched
        :param buffer : buffer where data pool stores
        :return       : data grabbed 
        """
        bufsize = len(buffer) - 33
        offset = randint(0,bufsize)
        bufend = bufsize - 1
        ret = bytes()
        while size>0:
            if (size > bufsize):
                buf = buffer[offset:bufend]
                ret+= buf
                size-= len(buf)
                offset = 0
            else:
                start = randint(0,bufsize-size)
                buf = buffer[start:start+size]
                ret += buf
                size-= len(buf)

        return ret


    def seek_to(self, file_size=0):
        """ this method calculate the index of each write will locates on 
            this is the fundamental algrithm for seek-type
        :param file_size : file size of target file used to constituted the seek strategy
        :return          : a generate object to supply the indexes
        """
        numwrite = file_size // self._iosize
        remainder = file_size % self._iosize
        modfilesize = numwrite * self._iosize
        if remainder > 0:
            yield (file_size - remainder)
        if self._seek == 'seq':
            for idx in range(0, numwrite):
                yield idx * self._iosize
        elif self._seek == 'reverse':
            for idx in range(numwrite, 0, -1):
                yield ((idx*self._iosize) - self._iosize)
        elif self._seek == 'random':
            # one million rought use 20MB memory
            # it's not the fully random algorithm
            # while the number of I/O beyound a million
            # accroding to trial, 'random' mode could be 
            # up to 3x slower then 'seq'
            million = 1000 * 1000
            numslice = numwrite // million 
            remainder = numwrite % million
            slicegroup = []
            if numslice > 0:
                for idx in range(0, numwrite, million):
                    slicegroup.append([idx, idx+million])
                # remove last item is invalid which exceed 'numwrite'
                slicegroup.pop()
            if remainder > 0: 
                slicegroup.append([(numwrite - remainder), numwrite])
            shuffle(slicegroup)
            for s in slicegroup:
                slicelist = list(range(s[0], s[1]))
                shuffle(slicelist)
                for idx in slicelist:
                    yield idx * self._iosize
                slicelist = []

