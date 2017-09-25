import os
import sys
import re
import time
import logging
import hashlib
import pdb
import string
from random import Random

from os.path import exists
from random import Random

class MyLogger:
    """ MyLogger Class
    Customerised logger class based upon python standard libarary logging.Logger
    """
    LOG_LEVELS = {
        'INFO'     : logging.INFO,
        'WARNING'  : logging.WARNING,
        'CRITICAL' : logging.CRITICAL,
        'DEBUG'    : logging.DEBUG,
    }

    def __init__(self, logger_name=__name__, 
                 record_path=__name__, log_level='INFO'):
        """
        init definition
        :param self        : self object
        :param logger_name : name of logger
        :param record_path : file path used to store log files
        :param log_level   : log level, on of ['INFO', 'WARN', 'DEBUG', 'ERROR']
        """ 
         
        if log_level not in self.LOG_LEVELS:
            sys.exit("parameter log_level is invalid")  
       
        if not exists(record_path):
            os.makedirs(record_path)

        self.__recordpath__ = record_path + '_' + str(time.time())

        self.__loggername__ = logger_name
        self.__loglevel__ = log_level
       
        self.__logger__ = logging.getLogger(logger_name)
        self.__logger__.setLevel(self.LOG_LEVELS[log_level])

        # create a logging format
        formatter = logging.Formatter(
            '%(asctime)s - %(process)s - %(levelname)s:  %(message)s'
        )

        # create a file handlers
        self.__recordhandler__ = logging.FileHandler(self.__recordpath__)
        self.__recordhandler__.setLevel(self.LOG_LEVELS[log_level])
        self.__consolehandler__ = logging.StreamHandler()
        self.__consolehandler__.setFormatter(formatter)

        # add the handlers to the logger
        self.__recordhandler__.setFormatter(formatter)
        self.__logger__.addHandler(self.__recordhandler__)
        self.__logger__.addHandler(self.__consolehandler__)
    
 
    def get_logger(self): 
        return self.__logger__


    def update_logger(self, log_level=None):
        """" Update logger, for now only log level need to be udpated
        :param log_level  : level to be updated to 
        :return           : None
        """
        if log_level is None:
            return

        self.__recordhandler__.setLevel(self.LOG_LEVELS[log_level])
        self.__consolehandler__.setLevel(self.LOG_LEVELS[log_level])


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
    rawsize = raw_size
    sm = re.search('^(\d+)(b|B|k|K|m|M|g|G|t|T|p)?', str(rawsize))
    if sm:
        number = sm.group(1)
        if sm.group(2):
            unit = sm.group(2)
            if unit.upper() == 'B':
                return number
            elif unit.upper() == 'K':
                return int(number) * 1024
            elif unit.upper() == 'M':
                return int(number) * 1024 * 1024
            elif unit.upper() == 'G':
                return int(number) * 1024 * 1024 * 1024
            elif unit.upper() == 'T':
                return int(number) * 1024 * 1024 * 1024 * 1024
            elif unit.upper() == 'P':
                return int(number) * 1024 * 1024 * 1024 * 1024 * 1024
            else:
                sys.exit("Invalid unit: %s" % unit)
        else:
            return int(number )
    else:
        sys.exit("ERROR: Passed size is malformed!")


def encipher_data(data=None, store=None):
    """ encode the given string to a checksum code, then put it in to store db
    :encipher : target string to be enciphered
    :return   : checksum of given string
    """
    if data is None:
        raise  ValueError("Parameter data is required")
    # using 'sha' result as unique db key to reduce the hosts' memory consumption
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
