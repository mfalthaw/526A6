''' status '''

from ..utils import Logger

async def status_handle(messenger):
    ''' Request status from the bots '''
    await messenger.send_channel('status')

    # Collect responses & perform analytics
    responses = await messenger.read()
    names = ', '.join(responses)

    # Report diagnostics
    Logger.log('----------------------------------------------------')
    Logger.log('Number of bots: {}'.format(len(names)))
    if names:
        Logger.log('Bot names: {}'.format(names))
    Logger.log('----------------------------------------------------')
