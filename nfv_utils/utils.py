import os
import sys
import logging



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



