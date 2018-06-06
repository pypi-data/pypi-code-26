from pubnub.pubnub import PubNub, SubscribeListener
from pubnub.pnconfiguration import PNConfiguration
from uuid import uuid4
from pubsub import (
    get_secret,
    call_mapped_method,
)
import importlib
import redis
import time
import os

IS_VERBOSE = os.environ.get('VERBOSE', 'True') == 'True'


class RedisBackend:
    """
    * list listening apps
    * show recent events and their subscribers' acknowledgments
    """

    def __init__(self, channel, appname):
        self.channel = channel
        self.appname = appname
        self.redis = redis.StrictRedis(
            host=get_secret('PUBSUB_HOST', 'redis'),
            password=get_secret('PUBSUB_PASSWORD', None),
            port=6379,
            db=0
        )

    def __ack(self, event, event_id):
        """
        Inform the puslisher that we've received the message
        """
        key = 'pubsub.events.actions.{}.{}.received'.format(event, event_id)
        self.redis.sadd(key, self.appname)

        if IS_VERBOSE:
            print('<< - {} received by {}'.format(event, self.appname))

    def clean(self):
        """
        Clean old subscribers from the registry
        """
        pass

    def register(self, events):
        """
        Register a subscriber: Inform the pubsub appname and what events
        we're listening to events is a list of events to which this app will
        listen
        """
        print('Registering: {}'.format(self.appname))
        print('------------------------------------')
        for event in events:
            key = 'pubsub.events.{}.subscribers'.format(event)
            # for event, get subscrived apps
            self.redis.sadd(key, self.appname)

            # for app, get events
            key = 'pubsub.applications.{}.events'.format(self.appname)
            self.redis.sadd(key, event)

            print(" - {}".format(event))
        print('------------------------------------')

    def de_register(self, events):
        """
        If a subscriber disappears, it must de-register itself
        TODO: make sure this is called on ctrl-C
        """
        for event in events:
            key = 'pubsub.events.{}.subscribers'.format(event)
            # for event, get subscrived apps
            self.redis.srem(key, self.appname)

            # for app, get events
            key = 'pubsub.applications.{}.events'.format(self.appname)
            self.redis.srem(key, event)

    def check_in(self, events):
        """
        A subscriber must check in periodically to let the system know that
        it's still there and listening
        """
        print('Checking in:')
        self.register(events)

    def publish(self, key, payload):
        event_id = str(uuid4())
        data = {
            "key": key,
            "id": event_id,
            "payload": payload
        }
        result = self.redis.publish(self.channel, data)
        redis_key = 'pubsub.events.actions.{}.{}.published'.format(key,
                                                                   event_id)
        self.redis.sadd(redis_key, self.appname)

        if IS_VERBOSE:
            print('>> {} -> {}.{}'.format(self.appname, self.channel, key))
        return result

    def subscribe(self, function_mapper):
        p = self.redis.pubsub()
        p.subscribe(self.channel)
        events = [key for key, value in function_mapper.items()]
        self.register(events)

        count = 0
        while True:
            message = p.get_message()
            if message:
                event, event_id = call_mapped_method(message, function_mapper)
                if event is not None:
                    self.__ack(event, event_id)
            count += 1
            if count > 60000:  # every minute:
                self.check_in(function_mapper)
                count = 0
            time.sleep(0.001)  # be nice to the system :)


class PubNubBackend:
    """
    Usage:

    **Subscribe**
    ```
    pubsub = PubNubBackend(channel, pub_key, sub_key)
    pubsub.subscribe()
    ```

    Requires environment variables:
    * PUBNUB_PUBLISH_KEY
    * PUBNUB_SUBSCRIBE_KEY

    """

    def __init__(self, channel):
        publish_key = get_secret('PUBNUB_PUBLISH_KEY', None)
        subscribe_key = get_secret('PUBNUB_SUBSCRIBE_KEY', None)

        if None in [subscribe_key, publish_key]:
            msg = ('Please make sure you\'ve set environment varialbes: '
                   'PUBNUB_PUBLISH_KEY and PUBNUB_SUBSCRIBE_KEY')
            raise Exception(msg)
        pnconfig = PNConfiguration()
        pnconfig.subscribe_key = subscribe_key
        pnconfig.publish_key = publish_key
        pnconfig.ssl = False
        self.channel = channel
        self.pubnub = PubNub(pnconfig)

    def publish(self, key, payload):
        def publish_callback(result, status):

            if result:
                print(result)
            if status.error is not None:
                raise Exception('PubSub publish error: %s: %s' %
                                (status.error, status.error_data))
        data = {
            "key": key,
            "payload": payload
        }
        self.pubnub.publish() \
            .channel(self.channel) \
            .message(data) \
            .async(publish_callback)

    def listen(self, function_mapper):
        """
        Implements a multicast pub/sub. It is the responsibility of the
        subscriber determine if it needs to perform any actions based on
        the message key

        functionmapper is a dict that maps payload keys to methods to call
        Methods will receive the payload as the first argument.

        e.g.:

        ```
        function_mapper = {
            'test': {
                'module': 'config',
                'method': 'foo'
            }
        }
        ```
        """
        my_listener = SubscribeListener()
        self.pubnub.add_listener(my_listener)
        self.pubnub.subscribe().channels(self.channel).execute()
        # self.pubnub.add_channel_to_channel_group()\
        #     .channel_group("test")\
        #     .channels(channels)\
        #     .sync()

        my_listener.wait_for_connect()
        print('connected')

        while True:
            result = my_listener.wait_for_message_on(self.channel)
            print(result.message)
            event_key = result.message.get('key')
            task_definition = function_mapper.get(event_key, None)
            print('key: %s' % event_key)
            print('task definition: %s' % task_definition)

            if task_definition is not None:
                mod = importlib.import_module(task_definition.get('module'))
                method = task_definition.get('method')
                getattr(mod, method)(result.message)
