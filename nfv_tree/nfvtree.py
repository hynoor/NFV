""" nfvtree.py implemented fundamental data structures of file tree, file and I/O tactic

:class NfvTree      : a data structure represent a file tree
:class NfvLock      : a data structure represent a file  
:class NfvAdsStream : a data structure represent a Alternate Data Stream
:class NfvIoTactic  : a class defines I/O charactors, such as data_pattern, seek_type etc.

NOTEs:
- newly initialized NfvTree object doesn't have any NfvFile object
- NfvFile object(s) can deployed into a NfvTree object
- NfvIoTactic object is required to be applied on either NfvFile or NfvTree object beofore any I/O manipulation
- NfvAdsStream object nested in NfvFile object, it can not exist independently

Layout of demo file tree:

                    tree_root
                          |
           --------------------------------------------------------------------------
           |                        |                   |                           |
--------xyuse34(dir)-----           --t4fk2s(dir)---    ------45dwwf(dir)-----  5dfeu7f    
|      |            |               |         |    |                 |
4tdre erk3d  ---df9jd(dir)---     dr3nmv   6yqsa uy98jv            bdw54(dir)
             |              |                                        |
           xwetj4      87deeu                                     zakdj98

"""

# stardand modules
import os
import sys
import re
import copy

import time
import logging
import hashlib
import string

from random import Random
from shutil import copyfile, move, rmtree
from hashlib import md5
from random import randint, shuffle
from os import path, makedirs, listdir, walk, remove
from os.path import isfile, isdir, exists, getsize, exists, join, getsize, split
from collections import defaultdict
from itertools import cycle


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

    def __init__(self, tree_root=None, tree_width=0, tree_depth=0, dir_length=8, io_tactic=None):
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
        if tree_root is None:
            raise ValueError("ERROR: Paramter tree_root is required!")
        self._root = tree_root
        if tree_width <= 0:
            tree_depth = 0
        elif tree_width > 0 and tree_depth <= 0:
            tree_depth = 1
        self._width = tree_width
        self._depth = tree_depth
        self._files = set()
        self._dirs = set()
        self._treesize = 0 
        self._dirlen = 0  

        if io_tactic is None:
            self._iotactic = NfvIoTactic()
        else:
            self._iotactic = io_tactic

        if exists(tree_root):
            self.load_tree(self._root)
        else:
            self.new(self._root, self._width, self._depth)

    def new(self, dir=None, tree_width=0, tree_depth=0):
        """ initialize a tree object
        
        this function will be called for creating a new file tree

        :param tree_width : the width of file tree
        :param tree_depth : the depth of file tree
        """
        width = tree_width
        depth = tree_depth
        # create tree root first
        if not exists(dir):
            makedirs(dir)
            self._dirs.add(dir)
        for _ in range(width):
            entry = join(dir, random_string(8))
            makedirs(entry)
            self._dirs.add(entry)

        if depth > 1:
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
        else:
            self._dirs.add(tree_root)
        treedepth = 0
        treewidth = 0
        path = os.path.normpath(tree_root)
        for dirpath, dirs, files in walk(tree_root, topdown=True):
            for filename in files:
                fullname = join(dirpath, filename)
                self._files.add(NfvFile(path=fullname))
            for dirname in dirs:
                self._dirs.add(join(dirpath, dirname))
        treelistgen = (f for f in listdir(tree_root) if isdir(join(tree_root, f)))
        for _ in treelistgen:
            treewidth += 1
        # recursively dive into immedia left child   
        # this strategy only works when the existing tree is standard NfvTree structure

        def dive_dir(dir=None):
            subdirs = [f for f in listdir(dir) if isdir(join(dir, f))]
            while len(subdirs):
                yield
                dir = join(dir, subdirs[0])
                subdirs = [f for f in listdir(dir) if isdir(join(dir, f))]

        divegen = dive_dir(dir=tree_root)
        for _ in divegen:
            treedepth += 1
        self._width=treewidth
        self._depth=treedepth
        # initialize io tactic
        for f in self._files:
            f.set_tactic(self._iotactic)

        self.update()

    def set_tactic(self, io_tactic=None):
        """ set io tactic for the file tree

        attach a NfvIoTactic object to current file tree,
        which could leverage the tactic to do I/O operation

        :param tactic : NfvIoTactic object
        :return       : *none*
        """
        if type(io_tactic) is not NfvIoTactic:
            raise ValueError("ERROR: Given parameter tactic is not NfvIoTactic object!")
        self._iotactic = io_tactic
        for f in self._files:
            f.set_tactic(io_tactic)

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
        if not exists(self._root):
            raise Exception("file tree does not exist!")

        deltanum = abs(file_number - len(self._files))

        if file_number > len(self._files):
            self.create_file(number=deltanum, size=file_size, io_tactic=self._iotactic)
        if file_number < len(self._files):
            self.remove_file(number=deltanum)

        self.update()

    def truncate(self, target_size=None):
        """ truncate the on-disk file tree to specific size

        :param target_size : size of each file to be truncated to
        :return            : *none*
        """
        if target_size is None:
            pass
        else:
            target_size = convert_size(target_size)

        for f in self._files:
            f.truncate(target_size)
        
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
        :return            : *none*
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

        read all files within file tree with io_size 
        and seek type specified in io tactic object

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

        del self
  
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
    __slots__ = (
            '_path', 
            '_size', 
            '_dir', 
            '_name', 
            '_checksum', 
            '_iotactic', 
            '_adsstreams',
            '_lockmgr',
            '_locks',
    )

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
        self._adsstreams = {} 
        self._locks = set()

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
        indexsupplier = self._iotactic.seek_to(file_size=self._size)
        if remainder > 0:
            rindex = next(indexsupplier)
        with open(self._path, openmode) as fh:
            if remainder > 0 and self._iotactic._seek == 'reverse':
                data = self._iotactic.get_data_pattern()
                if self._iotactic._datacheck:
                    NfvFile._io_check_db[encipher_data(data, NfvFile._io_check_db)] = True
                fh.seek(rindex)
                fh.write(data[:remainder])
            for idx in indexsupplier:
                data = self._iotactic.get_data_pattern()
                if self._iotactic._datacheck:
                    NfvFile._io_check_db[encipher_data(data, NfvFile._io_check_db)] = True
                fh.seek(idx)
                fh.write(data)
            if remainder > 0 and (self._iotactic._seek == 'sequencial' or self._iotactic._seek == 'random'):
                data = self._iotactic.get_data_pattern()
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

    def set_tactic(self, io_tactic=None):
        """ set the tactic for file I/O manipulations

        :param io_tactic : NfvIoTactic object
        :return          : *none*
        """
        if io_tactic is None:
            raise ValueError("ERROR: parameter io_tactic must be a NfvIoTactic object!")
        self._iotactic = io_tactic

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
            if remainder > 0 and self._iotactic.get_property('seek-type') == 'reverse':
                fh.seek(rindex)
                fh.read(remainder)
            for idx in indexsupplier:
                fh.seek(idx)
                fh.read(self._iotactic._iosize)
            if remainder > 0 and (self._iotactic.get_property('seek-type') == 'sequencial'\
                    or self._iotactic.get_property('seek-type') == 'random'):
                fh.seek(rindex)
                fh.read(remainder)

    def checksum(self, chunk_size=4096):
        """ checksum the data of on-disk file
        
        :param chunck_size : size of each chunck to be read for md5
        :return            : checksum value  
        """
        if chunk_size > self._size:
            chunk_size = self._size

        hashmd5 = md5()
        with open(self._path, 'rb') as fh:
            for chunk in iter(lambda : fh.read(chunk_size), b""):
                hashmd5.update(chunk)

        self._checksum = hashmd5.hexdigest()
        return self._checksum

    def remove(self):
        """ remove the ondisk file

        :return  : *none*
        """
        try: 
            os.remove(self._path)
        except IOError as e:
            raise IOError(e)
        
        del self

    def create_ads(self, streams=None, size='8k'):
        """ create one or more ads stream

        :param streams : the name of ads streams to be created
        :param size    : the size of streams to be created
        :return        : *none*
        """

        if streams is None:
            raise ValueError("ERROR: parameter streams is required")
        streamlist = string_to_list(streams)
        for s in streamlist:
            stream = NfvAdsStream(path=self._path + ":" + s, size=size, io_tactic=self._iotactic)
            self._adsstreams[s] = stream

    def overwrite_ads(self, streams=None, size='8k'):
        """ overwrite ads streams

        :param streams : the name of ads streams to be overwrote
        :param size    : the size of streams to be created
        :return        : *none*
        """

        if streams is None:
            raise ValueError("ERROR: parameter streams is required")

        streamlist = string_to_list(streams)
        for n, o in self._adsstreams.items():
            if n in streamlist:
                o.overwrite() 
        
    def remove_ads(self, streams=None):
        """ overwrite ads streams

        :param streams : the name of ads streams to be overwrote, it will remove
                         all streams object if not specified
        :return        : *none*
        """
        if streams is None:
            if len(self._adsstreams) > 0:
                for s in self._adstreams:
                    s.remove()
            else:
                raise ValueError("ERROR: parameter streams should be specified")
        else:
            streamnames = string_to_list(streams)
            for sn in streamnames:
                try:
                    if sn in self._adsstreams.keys():
                        self._adsstreams[sn].remove()
                        del self._adsstreams[sn]
                    else:
                        remove(self._path + ":" + sn)
                except IOError as e:
                    print("stream %s not found" % sn)
                    pass 
       

class NfvIoTactic:
    """ Nfv I/O Tactic 
    the class defines the tactic of I/O
    """ 
    __slots__ = (
            '_iosize', 
            '_datapattern', 
            '_seek', 
            '_property', 
            '_data', 
            '_datacheck',
            '_ioregions',
    )

    _seeks = ('sequencial', 'random', 'reverse')
    _patterns = ('fixed', 'random', 'bit', 'hex')
    _datagranary = os.urandom(1048576)  # 1MB size data granary for random data pattern

    def __init__(self, io_size='8k', data_pattern='fixed', seek_type='sequencial', \
                 data_check=True, io_regions=[[0,0]]):
        """ NfvIoTactic constructor

        :param io_size      : io size of tactic to be adopted
        :param data_pattern : data pattern of io tactic to be adopted
        :param seek_type    : seek type of tactic to be adopted
        :param data_check   : a bool flag indicates if perform 
                              immediate data check on each file
        :return             : NfvIoTactic object
        """
        if seek_type not in self._seeks:
            raise ValueError("ERROR: Given seek_type %s is invalid!" % seek_type)
        if data_pattern not in self._patterns:
            raise ValueError("ERROR: Given data_pattern %s is invalid!" % data_pattern)

        self._iosize = convert_size(io_size)
        self._datapattern = data_pattern
        self._seek = seek_type
        self._data = bytes()
        self._ioregions = io_regions[:]
        self._datacheck = data_check
        if self._datapattern == 'random':
            self.set_data_pattern(self.random_pattern(io_size=self._iosize))
        elif self._datapattern == 'fixed':
            self.set_data_pattern(self.fixed_pattern(io_size=self._iosize))
        elif self._datapattern == 'bit':
            self.set_data_pattern(self.bit_pattern(io_size=self._iosize))
        elif self._datapattern == 'hex':
            self.set_data_pattern(self.hex_pattern(io_size=self._iosize))
            
    def set_property(self, attrs={}):
        """ set given properties

        :param attrs : a dictionary contains the property-value pairs to be set
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

    def set_data_pattern(self, data=None):
        """ set data feed for each I/O 
        :param data: data to be set 
        :return    : *none*
        """
        if data is None:
            raise ValueError("ERROR: parameter data is required!")
        self._data = data
        self._iosize = len(self._data)

    def get_data_pattern(self):
        """ get data feed for each I/O 

        :return : *none*
        """
        if self._datapattern == 'random':
            self._data = NfvIoTactic.random_pattern(io_size=self._iosize)

        return self._data

    def clear_data_pattern(self):
        """ clear data

        :return : *none*
        """
        self._data = None

    @staticmethod
    def hex_pattern(hex_value='00', io_size=None):
        """ renew self._data with hex data pattern

        :return : data pattern generated
        """
        if io_size is None:
            raise ValueError("ERROR: parameter io_size is required!")
        else:
            iosize = int(convert_size(io_size))
        tmpbytes = bytes.fromhex(hex_value)
        numchunk = iosize // len(tmpbytes)
        rmdchunk = iosize % len(tmpbytes)

        return tmpbytes * numchunk + tmpbytes[:rmdchunk]

    @staticmethod
    def random_pattern(io_size='8k'):
        """ renew self._data with random data pattern

        :return : data pattern generated
        """
        iosize = int(convert_size(io_size))

        return NfvIoTactic.get_rand_buffer(iosize, NfvIoTactic._datagranary)

    @staticmethod
    def fixed_pattern(pattern=None, io_size='8k'):
        """ renew the fixed pattern

        generate a data with fixed data pattern 
        :return : data pattern in bytes
        """
        iosize = int(io_size)

        tmpbytes = bytes('content of data pattern is not important', encoding='utf-8')
        if pattern is not None:
            tmpbytes = bytes(tmpbytes, encoding='utf-8')

        if len(tmpbytes) >= iosize:
            return tmpbytes[:iosize]
        else:
            number = iosize // len(tmpbytes)  
            remainder = tmpbytes[:iosize % len(tmpbytes)]
            return tmpbytes * number + remainder 

    @staticmethod 
    def bit_pattern(bits='00000000', io_size='8k'):
        """ renew the data pattern with bit mode

        it supports 8 bits customization
        :param bin_str  : binary string to be converted
        :return         : data in bytes
        """
        iosize = int(convert_size(io_size))

        tmpbytes = NfvIoTactic.bits2byte(bits)
        numchunk = iosize // len(tmpbytes)
        remainderchunk = iosize % len(tmpbytes)

        return tmpbytes * numchunk + tmpbytes[:remainderchunk] 

    @property
    def seek_type(self):
        """
        The order of seeking
        :return: seek type
        """
        return self._seek

    @staticmethod
    def compress_pattern(pattern='abc', compress_ratio=50, io_size='8k', chunk=1):
        """ generate the compressible data pattern 

        parameter pattern accepts the compressible data pattern for
        assembling the chunk while compress_ratio defines it proportion 
        :param pattern        : data pattern for compressible chunk
        :param compress_ratio : the proportion of compressible data
        :param io_size        : size of data pattern to be generated
        :param num_chunk      : number of compressible chunks of data pattern
        :return               : a compressible data pattern composed of chunks
        """
        iosize = int(convert_size(io_size))
       
        chunksize = iosize // chunk
        if chunksize < 1024:
            raise ValueError("ERROR: size of chunk is too small to build compressible data properly")

        csize = int(chunksize*(float(compress_ratio)/float(100)))
        usize = chunksize - csize

        # build chunk 
        uchunk = NfvIoTactic.get_rand_buffer(usize, NfvIoTactic._datagranary)
        tmpchunk = bytes(pattern, 'utf-8')
        numtmpchunk = csize // len(tmpchunk) 
        rmdtmpchunk = csize % len(tmpchunk)
        cchunk = tmpchunk * numtmpchunk + tmpchunk[:rmdtmpchunk]

        return (uchunk + cchunk) * chunk 

    @staticmethod 
    def bits2byte(binary='00000000'):
        """ this method is to converted binary string to hex number

        :param bin_str : binary string to be converted
        :return        : hex number
        """
        binstr = binary
        hexres = ''
        if len(binstr) < 8:
            binstr = (8 - len(binstr)) * '0' + binstr
        if len(binstr) > 8:
            binstr = binstr[0:8]
        if int('0b' + binstr, 2) < 16:
           hexstr = hex(int('0b'+binstr, 2)).replace('0x', '0')

        else:
           hexstr = hex(int('0b'+binstr, 2)).replace('0x', '')

        return bytes.fromhex(hexstr)

    @staticmethod 
    def compound_pattern(container=None, pattern_func=None, *args, **kwargs):
        """ compound a data pattern on top of existing ones

        compound different data patterns into on data pattern
        :param pattern_func   : function object for generating data pattern
        :param *args **kwargs : arguments to be passed into pattern function object
        :return               : data pattern compounded
        """
        if container is None:
            raise ValueError("ERROR: parameter container is required!")
        if pattern_func is None:
            raise ValueError("ERROR: parameter pattern_func is required!")

        data = pattern_func(*args, **kwargs)
        container += data
        return container

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

    def seek_to(self, start_offset=0, stop_offset=None, file_size=None):
        """ calculate the index of each write will locates on 

        this is the fundamental algrithm for seek-type, which support three
        types of seeking, 'sequencial', 'random' and 'reverse'. wherer 'random' 
        is roughly 3x slower then the others

        :param file_size : file size of target file used to constituted the seek strategy
        :return          : a generate object to supply the indexes
        """
        if file_size is None:
            file_size = stop_offset - start_offset

        numwrite = file_size // self._iosize
        remainder = file_size % self._iosize
        if remainder > 0:
            yield (file_size - remainder)
        if self._seek == 'sequencial':
            for idx in range(start_offset, numwrite):
                yield idx * self._iosize
        elif self._seek == 'reverse':
            for idx in range(numwrite, start_offset, -1):
                yield ((idx*self._iosize) - self._iosize)
        elif self._seek == 'random':
            # one million roughly use 20MB memory
            # it's not the fully random algorithm
            # while the number of I/O beyond a million
            # according to trial, 'random' mode could be
            # up to 3x slower than 'seq'
            million = 1000 * 1000
            numslice = numwrite // million 
            remainder = numwrite % million
            slicegroup = []
            if numslice > 0:
                for idx in range(start_offset, numwrite, million):
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


class NfvAdsStream(NfvFile):
    """ Alternate Data Stream class
    
    inherited from NfvFile class, which is substantially 
    the same as NfvAdsStream class, for those CIFS/NTFS file(s), 
    there s alternate data stream can be manipulated other than 
    regular unnamed stream, one file could attched more ADS streams
    """

    pass


""" Code below implements 2 primary classes to manipulating file locks

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
import struct
import collections

from os.path import isfile, exists, getsize
# lock modules
if os.name == 'posix':
    import fcntl
    import struct
elif os.name == 'nt':
    import msvcrt

# NFV modules
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
        if type(lock) is not NfvLock:
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
        if type(lock) is NfvLock and lock in self._repository:
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

    def feed_lock(self, start=0, length=1, step=1, end=0, mode='exclusive', data=None):
        """ offer one lock at a time until the file end or user given strategy

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
        lockstart = start
        lockstep = step
        locklength = length
        lockend = end
        filesize = 0
        lock = None

        if self._file.get_property('path'):
            filesize = getsize(self._file.get_property('path'))
        else:
            raise Exception("It requires attached a file before producin any lock!")

        if os.name == 'nt':
            # nt lock will not merge the ajacent locks
            lockstep = 0

        locklocator = self.locator(file_size=filesize, start=lockstart, lock_length=locklength, step=lockstep, stop=lockend)
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
            lock = NfvLock(offset=loc[0], length=loc[1], mode=lockmode, data=data)
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

        if file is None:
            raise ValueError("Error: parameter file is required!")

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

    def _posix_lock(self, lock_mode='exclusive'):
        """ create a posix byte-range lock

        it's considered as private method, do not use via object directely 

        :param lock_mode : the locking mode to be applied  
        :return          : *none*
        """
        fh = self._filehandle
        mode = lock_mode
        data = self._data
        lockdata = struct.pack('hhllhh', self._LOCK_MODES[mode][1], \
                0, self._startoffset, self._length, 0, 0)

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


def random_string(size=8, seed=None):
    """ generate a random string
    :param size : length of target string to be generated
    :param seed : seed to be used for generating string
    :return     : generated string
    """
    randomstring = '' 

    if seed is None:
        chars = [(c) for c in string.ascii_lowercase + string.ascii_uppercase + '0123456789']
    else:
        chars = [(c) for c in seed]

    for _ in range(size):
        # rand chars will generate a random
        # number between 0 and length of chars
        randobj = Random()
        offset = randobj.randint(0, len(chars)-1)
        randomstring += chars[offset]

    return randomstring


def convert_size(raw_size):
    """ convert passed size with whatever units to byte unit
    param raw_size  : passed raw size
    return          : size in byte
    """
    rawsize = str(raw_size).lower()
    sm = re.search('^(\d+)(b|k|m|g|t|p)?', rawsize)
    if sm:
        number = sm.group(1)
        if sm.group(2):
            unit = sm.group(2)
            if unit == 'b':
                return number
            elif unit == 'k':
                return int(number) * 1024
            elif unit == 'm':
                return int(number) * 1024 ** 2
            elif unit == 'g':
                return int(number) * 1024 ** 3
            elif unit == 't':
                return int(number) * 1024 ** 4
            elif unit == 'p':
                return int(number) * 1024 ** 5
            else:
                sys.exit("Invalid unit: %s" % unit)
        else:
            return int(number)
    else:
        sys.exit("ERROR: Passed size is malformed!")


def encipher_data(data=None, store=None):
    """ encode the given string to a checksum code, then put it in to store db
    :encipher : target string to be enciphered
    :return   : checksum of given string
    """
    if data is None:
        raise  ValueError("Parameter data is required")
    # using md5 result as unique db key to reduce the hosts' memory consumption
    hashmd5 = hashlib.md5()
    hashmd5.update(data)
    datacks = hashmd5.digest()
    # Start over if the data is already in the Database
    if store:
        store[datacks] = True
    else:
        return datacks

 
def random_string(length=8, seed=None):
    """ generate a random string
    :param length : length of target string to be generated
    :return       : generated string
    """
    strlength= length
    randomstring = '' 

    if seed is None:
        chars = [(c) for c in string.ascii_lowercase + string.ascii_uppercase + '0123456789']
    else:
        chars = [(c) for c in seed]

    for _ in range(strlength):
        # rand chars will generate a random
        # number between 0 and length of chars
        randobj = Random()
        offset = randobj.randint(0, len(chars)-1)
        randomstring += chars[offset]

    return randomstring


def string_to_list(string=None):
    """ examine passed string to list

    :param string  : string to be converted
    :return values : a list stores the result
    """
    global grandomace
    targetstr = string
    head = None
    rear = None
    hindex = None
    rindex = None
    finalres = []
    rawres = targetstr.split(',')
    for r in rawres:
        m = re.search('^.*(-|~){1}.*$', r)
        if m is not None:
            if m.group(1) == '-':
                fineres = r.split('-')
            elif m.group(1) == '~':
                fineres = r.split('~')
                grandomace = True
            else:
                sys.exit("Error: Invalid name format passed!")
            if len(fineres) == 2:
                m = re.search('^\s*(\S*\D)(0*)(\d+)$', fineres[0])
                head = m.group(1)
                hmedium = m.group(2)
                hindex = m.group(3)
                m = re.search('^\s*(\S*\D)(0*)(\d+)$', fineres[1])
                rear = m.group(1)
                rmedium = m.group(2)
                rindex = m.group(3)
                if head != rear:
                    raise ValueError("Invalid format passed!")
                else:
                    for i in range(int(hindex), int(rindex) + 1):
                        digits = len(str(i)) - len(hindex)
                        finalres.append(head + '0' * (len(hmedium)-digits) + str(i))
            elif len(fineres) == 1:
                finalres.append(fineres[0])
            else:
                sys.exit("Error: Invalid name format passed!")
        else:
            finalres.append(r)
    return finalres

