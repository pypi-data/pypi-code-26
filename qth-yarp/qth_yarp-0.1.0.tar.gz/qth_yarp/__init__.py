import asyncio

import qth
from yarp import NoValue, Value

from .version import __version__


__names__ = [
    "set_property",
    "get_property",
    "watch_event",
    "send_event",
    "run_forever",
    "set_default_qth_client",
    "get_default_qth_client",
]

_default_client = None

def set_default_qth_client(client):
    """
    Set the default :py:class:`qth.Client` object to be used by qth_yarp.
    """
    global _default_client
    _default_client = client


def get_default_qth_client():
    """
    Get the default :py:class:`qth.Client` object.
    
    One will be created with the name ``qth_yarp_based_client`` if no client
    has been provided by :py:func:`set_default_client`.
    """
    global _default_client
    if _default_client is None:
        _default_client = qth.Client("qth_yarp_based_client",
                                     "A qth_yarp based client.")
    return _default_client


def get_property(topic, initial_value=None,
                 register=False, description=None, one_to_many=False,
                 delete_on_unregister=True,
                 qth_client=None, loop=None, **kwargs):
    """
    Return a (continuous) :py:class:`yarp.Value` containing the value of a qth property.
    
    Parameters
    ----------
    topic : str
        The Qth topic name. (Not verified for existance).
    initial_value : object
        The initial value to assign to the returned :py:class:`yarp.Value`
        while waiting for the property to arrive from Qth. Defaults to ``None``
        but you may wish to choose an alternative dummy value which won't crash
        later processing.
        
        If (and only if) ``register`` is True, also sets the Qth property to
        this value.
    register : bool
        If True, registers this property with Qth. The 'description' argument
        must also be provided if this is True.
    description : str
        If ``register`` is True, the description of the property to include
        with the registration.
    one_to_many : bool
        If ``register`` is True, is this a one-to-many (True) or many-to-one
        (False) property. Defaults to many-to-one (False).
    on_unregister : value
        (Keyword-only argument). The value to set this property to when this
        Qth client disconnects. If not provided, no change is made. If this
        argument is used, set ``delete_on_unregister`` to False since it
        defaults to ``True`` and will conflict with this argument.
    delete_on_unregister : bool
        (Keyword-only argument). Should this value be deleted when this Qth
        client disconnects? Defaults to ``True``.
    qth_client : :py:class:`qth.Client`
        The Qth :py:class:`qth.Client` object to use. If not provided, uses the
        client returned by :py:func:`get_default_qth_client`.
    loop : :py:class:`asyncio.BaseEventLoop`
        The :py:mod:`asyncio` event loop to use. If not provided uses the lop
        returned by :py:func:`asyncio.get_event_loop`.
    """
    qth_client = qth_client or get_default_qth_client()
    loop = loop or asyncio.get_event_loop()
    
    output_value = Value(initial_value)
    
    def set_value(topic, value):
        output_value.value = value
    
    async def bind_value():
        if register:
            await qth_client.register(
                topic,
                qth.PROPERTY_ONE_TO_MANY
                    if one_to_many else
                    qth.PROPERTY_MANY_TO_ONE,
                description,
                delete_on_unregister=delete_on_unregister,
                **kwargs)
            await qth_client.set_property(topic, initial_value)
        await qth_client.watch_property(topic, set_value)
    loop.create_task(bind_value())
    
    return output_value


def watch_event(topic,
              register=False, description=None, one_to_many=False,
              qth_client=None, loop=None, **kwargs):
    """
    Return an (instantaneous) :py:class:`yarp.Value` representing a qth event.
    
    Parameters
    ----------
    topic : str
        The Qth topic name. (Not verified for existance).
    register : bool
        If True, registers this event with Qth. The 'description' argument
        must also be provided if this is True.
    description : str
        If ``register`` is True, the description of the event to include with
        the registration.
    one_to_many : bool
        If ``register`` is True, is this a one-to-many (True) or many-to-one
        (False) event. Defaults to many-to-one (False).
    on_unregister : value
        (Keyword-only argument). The value send for this event to when this
        Qth client disconnects. If not provided, event is sent.
    qth_client : :py:class:`qth.Client`
        The Qth :py:class:`qth.Client` object to use. If not provided, uses the
        client returned by :py:func:`get_default_qth_client`.
    loop : :py:class:`asyncio.BaseEventLoop`
        The :py:mod:`asyncio` event loop to use. If not provided uses the lop
        returned by :py:func:`asyncio.get_event_loop`.
    """
    qth_client = qth_client or get_default_qth_client()
    loop = loop or asyncio.get_event_loop()
    
    output_value = Value()
    
    def set_value(topic, value):
        output_value.set_instantaneous_value(value)
    
    async def bind_value():
        if register:
            await qth_client.register(
                topic,
                qth.EVENT_ONE_TO_MANY
                    if one_to_many else
                    qth.EVENT_MANY_TO_ONE,
                description,
                **kwargs)
        await qth_client.watch_event(topic, set_value)
    loop.create_task(bind_value())
    
    return output_value


def set_property(topic, value,
                 register=False, description=None, one_to_many=True,
                 delete_on_unregister=True,
                 qth_client=None, loop=None, **kwargs):
    """
    Set a Qth property to the value of a continuous :py:class:`yarp.Value`.
    
    Parameters
    ----------
    topic : str
        The Qth topic name. (Not verified for existance).
    value : :py:class:`Value`
        The :py:class:`yarp.Value` whose value will be written to the specified
        qth property.
    register : bool
        If True, registers this property with Qth. The 'description' argument
        must also be provided if this is True.
    description : str
        If ``register`` is True, the description of the property to include
        with the registration.
    one_to_many : bool
        If ``register`` is True, is this a one-to-many (True) or many-to-one
        (False) property. Defaults to one-to-many (True).
    on_unregister : value
        (Keyword-only argument). The value to set this property to when this
        Qth client disconnects. If not provided, no change is made. If this
        argument is used, set ``delete_on_unregister`` to False since it
        defaults to ``True`` and will conflict with this argument.
    delete_on_unregister : bool
        (Keyword-only argument). Should this value be deleted when this Qth
        client disconnects? Defaults to ``True``.
    qth_client : :py:class:`qth.Client`
        The Qth :py:class:`qth.Client` object to use. If not provided, uses the
        client returned by :py:func:`get_default_qth_client`.
    loop : :py:class:`asyncio.BaseEventLoop`
        The :py:mod:`asyncio` event loop to use. If not provided uses the lop
        returned by :py:func:`asyncio.get_event_loop`.
    """
    qth_client = qth_client or get_default_qth_client()
    loop = loop or asyncio.get_event_loop()
    
    @value.on_value_changed
    def update_property(new_value):
        loop.create_task(qth_client.set_property(topic, new_value))
    
    async def bind_value():
        if register:
            await qth_client.register(
                topic,
                qth.PROPERTY_ONE_TO_MANY
                    if one_to_many else
                    qth.PROPERTY_MANY_TO_ONE,
                description,
                delete_on_unregister=delete_on_unregister,
                **kwargs)
        update_property(value.value)
    loop.create_task(bind_value())

def send_event(topic, value,
               register=False, description=None, one_to_many=True,
               qth_client=None, loop=None, **kwargs):
    """
    Return an (instantaneous) :py:class:`yarp.Value` representing a qth event.
    
    Parameters
    ----------
    topic : str
        The Qth topic name. (Not verified for existance).
    value : :py:class:`yarp.Value`
        An instantaneous :py:class:`yarp.Value` whose changes will be turned
        into qth events.
    register : bool
        If True, registers this event with Qth. The 'description' argument
        must also be provided if this is True.
    description : str
        If ``register`` is True, the description of the event to include with
        the registration.
    one_to_many : bool
        If ``register`` is True, is this a one-to-many (True) or many-to-one
        (False) event. Defaults to one-to-many (True).
    on_unregister : value
        (Keyword-only argument). The value send for this event to when this
        Qth client disconnects. If not provided, event is sent.
    qth_client : :py:class:`qth.Client`
        The Qth :py:class:`qth.Client` object to use. If not provided, uses the
        client returned by :py:func:`get_default_qth_client`.
    loop : :py:class:`asyncio.BaseEventLoop`
        The :py:mod:`asyncio` event loop to use. If not provided uses the lop
        returned by :py:func:`asyncio.get_event_loop`.
    """
    qth_client = qth_client or get_default_qth_client()
    loop = loop or asyncio.get_event_loop()
    
    @value.on_value_changed
    def update_event(new_value):
        loop.create_task(qth_client.send_event(topic, new_value))
    
    async def bind_value():
        if register:
            await qth_client.register(
                topic,
                qth.EVENT_ONE_TO_MANY
                    if one_to_many else
                    qth.EVENT_MANY_TO_ONE,
                description,
                **kwargs)
    loop.create_task(bind_value())


def run_forever():
    """
    Run the main event loop forever.
    
    This function is a convenience method which is exactly equivalent to
    calling::
    
        import asyncio
        loop = asyncio.get_event_loop()
        loop.run_forever()
    """
    asyncio.get_event_loop().run_forever()
