''' quit '''

from ..errors import QuitSignal

async def quit_handle(messenger):
    ''' Break the connection with the server '''
    await messenger.quit()
    raise QuitSignal()
