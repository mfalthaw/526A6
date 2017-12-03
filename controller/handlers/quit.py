''' quit '''

from ..errors import QuitSignal

async def quit_handle(messenger, _):
    ''' Break the connection with the server '''
    raise QuitSignal()
