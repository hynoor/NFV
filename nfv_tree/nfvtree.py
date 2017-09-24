import os
import sys
import pdb

from os import path, makedirs, listdir, walk
from os.path import exists, join
from collections import namedtuple
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
            '_size',
            '_dirs',
            '_dirlen',
            '_property',
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
        self._size = 0 
        self._dirlen = 0  

        self._property = {
            'root'        : self._root,
            'width'       : self._width,
            'depth'       : self._depth,
            'size'        : self._size,
            'file_number' : len(self._files),
        } 
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


    def load_tree(self, tree_root=None):
        """ load_tree
        load a existing file tree into memory
        """
        if not exists(tree_root):
            raise Exception("Given dir %s doesn't exist!" % tree_root)

        for dirpath, dirs, files in walk(tree_root):
            for filename in files:
                fullname = join(dirpath, filename)
                self._files.add(NfvFile(file_path=fullname))
            for dirname in dirs:
                self._dirs.add(join(dirpath, dirname))



    def load_policy(self, policy=None):
        """ load_policy 
        load policy for manipulating file tree
        """
        pass

    
    def deploy_file(self, files=[]):
        """ deploy_file
        deploy or add NfvFile object into file tree
        """


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
    
    __slots__ = ('_path', '_size', '_inode', '_uid', '_policy', '_property')

    def __init__(self, file_path=None, size=8192, policy=None):
        """ init
        """
        if file_path is None:
            raise ValueError("Error: parameter file_path is required!")
        self._path = file_path 
        self._size = file_size
        slef._policy= policy
        self._dir, self._name = os.path.split(file_path)

        self._property = {
                path       : self._path,
                name       : self._name,
                size       : self._size,
                directory  : self._dir,
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

 
    def new(self): 
        """ create self with policy
        """
        if self._policy is None:
            raise ValueError("Error: parameter policy is required!")

    def load_policy(self):
        """ load_policy
        load policy for file manipulations
        """
        pass


    def truncate(self):   
        """ truncate
        truncate self to specific size
        """
        pass

    def append(self):
        """ truncate
        append self to specific size with specific policy
        """
        pass


    def copy(self):
        """ copy
        copy self with specific policy
        :return  : a copied NfvFile object
        """
        pass


    def move(self):
        """ copy
        move self with specific policy
        :return  : a  NfvFile object
        """
        pass

    def overwite(self):
        """ copy
        overwrite self with specific policy
        """
        pass


    def read(self):
        """ copy
        overwrite self with specific policy
        """
        pass

   
    def checksum(self):
        """ copy
        overwrite self with specific policy
        """
        pass

  

class NfvPolicy:
    """ Nfv Policy 
    the class defines io_size, data_pattern, seek_type to regulate IO
    """ 
    
    def __init__(self):
        """ init 
        constructor
        """
        self._iosize = io_size
        self._datapattern = data_pattern
        self._seek = seek_type









