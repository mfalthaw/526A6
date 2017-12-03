''' shutdown '''

async def shutdown_handle(messenger):
    ''' Request the botnet to shutdown '''
    await messenger.send_channel('shutdown')
