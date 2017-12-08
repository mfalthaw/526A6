''' logger.py '''

from ..config import DEBUG

class Logger:
    ''' Logger '''

    @staticmethod
    def log(msg):
        ''' log a message '''
        print(msg)

    @staticmethod
    def debug(msg, log_msg=None):
        ''' log a debug message '''
        if DEBUG:
            print(msg)
        elif log_msg:
            print(log_msg)

    @staticmethod
    def logline():
        ''' Log a line to show results '''
        Logger.log('----------------------------------------------------')

    @staticmethod
    def debugline():
        ''' Debug a line to show results '''
        Logger.debug('----------------------------------------------------')
