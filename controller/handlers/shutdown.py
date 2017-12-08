''' shutdown '''

from ..utils import Logger

async def shutdown_handle(messenger, _):
    ''' Request the botnet to shutdown '''

    Logger.log('issuing shutdown...')

    messenger.send_channel('shutdown')

    # Collect responses and perform analytics
    responses = await messenger.read('shutting')
    failures = list(response for response in responses if 'fail' in response)

    # Report diagnostics
    Logger.logline()
    map(lambda msg: Logger.log('Shutdown failure: {}'.format(msg)), failures)
    Logger.log('Total: {} bots shut down out of {}'.format(
        len(responses) - len(failures),
        len(responses)))
    Logger.logline()
