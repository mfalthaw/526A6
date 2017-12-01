''' status '''

from ..utils import Logger

def status_handle(messenger, _):
    ''' Request the status of the bots '''
    Logger.debug('requesting status')
    messenger.send('status')
