''' Errors '''

class ShutdownError(Exception):
    ''' Thrown when controller sends a shutdown command '''

    def __init__(self):
        super(ShutdownError, self).__init__('shutdown command received')
