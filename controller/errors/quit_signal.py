''' QuitSignal '''

class QuitSignal(Exception):
    ''' Error thrown to quit '''

    def __init__(self):
        Exception.__init__(self, 'sending signal to quit')
