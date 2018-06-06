def authorize(action):
    """
    Endpoint decorator.
    It checks that ability allows to execute action defined by `action`.

    Args:
        action (Action): action to validate access

    Example:
        @authorize(actions.view_project)
        def on_get(self, request, response, project_id):
            pass
    """
    def decorator(function):
        def wrapper(handler, request, response, *args, **kwargs):
            request.context.ability.authorize(action, request=request, *args, **kwargs)
            function(handler, request, response, *args, **kwargs)
        return wrapper
    return decorator
