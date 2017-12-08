''' list handler '''

from ..utils import Logger

async def list_handle(messenger, _):
    ''' handle list command '''
    messenger.send('LIST')
    responses = await messenger.read(messenger.get_nick())
    Logger.logline()
    for res in responses:
        Logger.log(res)
    Logger.logline()
