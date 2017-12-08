''' status '''

from ..utils import Logger

async def status_handle(messenger, _):
    ''' Request status from the bots '''
    messenger.send_channel('status')

    # Collect responses & perform analytics
    responses = await messenger.read()
    names = ', '.join(responses)

    # Report diagnostics
    Logger.log('----------------------------------------------------')
    Logger.log('Number of bots: {}'.format(len(responses)))
    if names:
        Logger.log('Bot name{}: {}'.format('' if (len(responses) == 1) else 's', names))
    Logger.log('----------------------------------------------------')
