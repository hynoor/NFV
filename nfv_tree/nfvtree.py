import os
import sys
import pdb
import re

from shutil import rmtree
from random import randint
from os import path, makedirs, listdir, walk
from os.path import exists, join, getsize
from collections import namedtuple
from itertools import cycle
from nfv_utils.utils import convert_size, random_string



class NfvTree:
    """ NfvTree
    represent a file tree object 
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
        """ init
        Constructor for instaniate a empty file tree
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
        """ deploy dirs of file tree
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

        return
   
    def update(self):
        """ update
        recalculate the total size of tree
        """      
        self._treesize = 0
        for f in self._files:
            self._treesize += f.get_property('size')
        

    def create_file(self, size='8K', quantity=1, io_tactic=None):
        """ create_file
        create user specific number of files with given io tactic 
        """
        if io_tactic is None and self._iotactic is None: 
            raise ValueError("ERROR: need io_tactic specific before any I/O operation!")
        elif self._iotactic is None and io_tactic is not None:
            self._iotactic = io_tactic
        elif self._iotactic and io_tactic:
            self._iotactic = io_tactic

        for _, dir in zip(range(quantity), cycle(self._dirs)):
            self._files.add(NfvFile(path=join(dir, random_string(8)), size=size, io_tactic=self._iotactic))
        
        self.update()


    def load_tree(self, tree_root=None):
        """ load_tree
        load a existing file tree into memory
        """
        if not exists(tree_root):
            raise Exception("Given dir %s doesn't exist!" % tree_root)

        for dirpath, dirs, files in walk(tree_root):
            for filename in files:
                fullname = join(dirpath, filename)
                self._files.add(NfvFile(path=fullname))
            for dirname in dirs:
                self._dirs.add(join(dirpath, dirname))


    def io_tactic(self, tactic=None):
        """ io_tactic
        load tactic for manipulating file tree
        """
        if type(tactic) is not NfvIoTactic:
            raise ValueError("ERROR: Given parameter tactic is not NfvIoTactic object!")
        self._iotactic = tactic

    
    def deploy_file(self, file_number=1):
        """ deploy_file
        deploy or add NfvFile object into file tree
        """
        pass

    
    def remove_file(self, file=None, quantity=1):
        """ remove files from tree randomly
        :param quantity : number of file to be removed
        """
        if file is not None and file in self._files:
            self._files(path)
        else:
            for f in range(quantity):
                try: 
                    self._files.pop().remove()
                except Exception as e:
                    if re.search('pop from an empty set', str(e)):
                        pass
                    else:
                        raise Exception(e)
        self.update()

    def get_property(self, name=None):
        """ get_property
        get the value of given property
        :param name : name of property to be got
        :return     : value of given parameter name, 
                      if param name was not given, return all properies
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
    
    
    def is_empty(self):
        """ check if current file tree is empty
        """
        if len(self._files) > 0:
            return True
        else:
            return False


    def resize(self, file_number):
        """ resize the total number of files within file tree
        :param file_number  : number of files to be resized
        """
        pass


    def wipe(self):
        """ wipe 
        wipe the entire tree and including its containing files
        """        
        for f in self._files:
            f.remove()
        
        rmtree(self._root)
        del self
        

    def __iter__(self):
        """ iter 
        iterator implemention
        """
        for f in self._files:
            yield f

   

class NfvFile:
    """ NfvFile
    represent a file object
    """
    __slots__ = ('_path', '_size', '_inode', '_dir', '_name', '_uid', '_iotactic')

    def __init__(self, path=None, size='8k', io_tactic=None):
        """ init
        """
        if path is None:
            raise ValueError("Error: parameter file_path is required!")
        self._path = path 
        self._size = convert_size(size)
        self._iotactic = io_tactic
        self._dir, self._name = os.path.split(path)

        if not exists(path):
            self.new()
        else:
            self.load_file(path)

    def new(self):
        """ new
        Create a new file
        """
        if self._iotactic is None:
            raise ValueError("Error: parameter tactic is required!")
        numwrite = self._size // self._iotactic.get_property('io_size')
        remainder = self._size % self._iotactic.get_property('io_size')
        with open(self._path, 'w+') as fh:
            while numwrite > 0:
                fh.write(self._iotactic.get_data())
                numwrite -= 1
            fh.write(self._iotactic.get_data()[:remainder])


    def load_file(self, path):
        """ load_file
        load a existing file
        """
        self._size = getsize(path) 
        self._dir, self._name = os.path.split(path)
        pass

  
    def get_property(self, name=None):
        """ get_property
        get the value of given property
        :param name : name of property to be got
        :return     : value of given parameter name, 
                      if param name was not given, return all properies
        """
        properties = {
                'path'       : self._path,
                'name'       : self._name,
                'size'       : self._size,
                'directory'  : self._dir,
        }

        if name is None:
            return properties
        if name in properties.keys():
            return properties[name]
        else:
            raise Exception("Given property name not found")


    def io_tactic(io_tactic=None):
        """ load_tactic
        load tactic for file manipulations
        """
        if io_tactic is None:
            raise ValueError("ERROR: parameter io_tactic must be a NfvIoTactic object!")
        self._iotactic = io_tactic
        pass


    def truncate(self):   
        """ truncate
        truncate self to specific size
        """
        pass

    def append(self):
        """ truncate
        append self to specific size with specific tactic
        """
        pass


    def copy(self):
        """ copy
        copy self with specific tactic
        :return  : a copied NfvFile object
        """
        pass


    def move(self):
        """ copy
        move self with specific tactic
        :return  : a  NfvFile object
        """
        pass

    def overwite(self):
        """ copy
        overwrite self with specific tactic
        """
        pass


    def read(self):
        """ copy
        overwrite self with specific tactic
        """
        pass

   
    def checksum(self):
        """ copy
        overwrite self with specific tactic
        """
        pass

  
    def remove(self):
        """ copy
        overwrite self with specific tactic
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
    __slots__ = ('_iosize', '_datapattern', '_seek', '_property', '_data')
    _seeks = ('seq', 'rand', 'reverse')
    _datagranary = os.urandom(1048576)  # 1MB size data granary for random data pattern

    def __init__(self, io_size='8k', data_pattern='random', seek_type='seq'):
        """ init 
        constructor
        """
        if seek_type not in self._seeks:
            raise ValueError("ERROR: Given seek type %s is invalid!" % seek_type)

        self._iosize = convert_size(io_size)
        self._datapattern = data_pattern
        self._seek = seek_type
        self._data = None
        if self._datapattern == 'random':
            self.random_pattern()
        elif self._datapattern == 'fixed':
            self.fixed_pattern()

        self._property = {
            'io_size'      : self._iosize,
            'data_pattern' : self._datapattern,
            '_seek_type'   : self._seek,
        }

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


    def get_data(self):
        """ get_data
        offer the prepare data for I/O 
        """
        return self._data

    def random_pattern(self):
        """ random pattern
        renew random data pattern
        """
        self._data = self.get_rand_buffer(self._iosize, self._datagranary)


    def fixed_pattern(self, pattern=None):
        """ fixed pattern
        """
        tmpstr = "This is a string used for NFV testing"
        if pattern is not None:
            tmpstr = pattern

        if len(tmpstr) >= self._iosize:
            self._data = tmpstr[:self._iosize]
        else:
            number = self._iosize // len(tmpstr)  
            remainder = tmpstr[:self._iosize % len(tmpstr)]
            self._data = tmpstr * number + remainder 


    @staticmethod
    def get_rand_buffer(size, buffer):
        """ fetch a piece of random data
        :param size   : data size to be fetched
        :param buffer : source buffer pool where data stores
        """
        bufsize = len(buffer) - 33
        offset = randint(0,bufsize)
        bufend = bufsize - 1
        ret = ''
        while size>0:
            if (size > bufsize):
                buf = buffer[offset:bufend]
                ret+= buf
                size-= len(buf)
                offset = 0
            else:
                start = randint(0,bufsize-size)
                buf = buffer[start:start+size]
                ret += str(buf)
                size-= len(buf)
        return ret


    @staticmethod
    def seek_to(self):
        """ seek_to
        offer the next io location (generator function)
        """
        pass





        

