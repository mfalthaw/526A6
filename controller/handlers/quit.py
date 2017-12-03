''' quit '''

from ..errors import QuitSignal

async def quit_handle(_, __):
    ''' Break the connection with the server '''
    raise QuitSignal()
