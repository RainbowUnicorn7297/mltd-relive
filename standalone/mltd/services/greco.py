from jsonrpc import dispatcher


@dispatcher.add_method(name='GrecoService.AppBoot')
def app_boot(params):
    """Service invoked at game client boot time.
    
    Args:
        params: An empty dict.
    Returns:
        An empty dict.
    """
    return {}

