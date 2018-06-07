import os
from pelops import mylogger


class SoundEvent:
    """
    Waits for the specified message on the subscribed topic. Upon reception the sound is played.
    """

    _config = None  # yaml config structure
    _logger = None  # logger

    _name = None  # name of sound event
    _message_value = None  # play sound if this value is received
    _mqtt_client = None  # mqtt_client instance

    _pygame_mixer = None  # mixer instance from pygame
    _pygame_sound = None  # pygame sound instance containing the provided sound file
    _volume = None  # 0..1 volume setting

    def __init__(self, config, mqtt_client, parent_logger, pygame_mixer):
        """
        Constructor

        :param config: yaml config structure
        :param mqtt_client: mqtt_client instance
        :param logger: logger instance from the parent. a child will be spawned
        :param pygame_mixer: playback instance
        """
        self._config = config
        self._logger = mylogger.get_child(parent_logger, self.__class__.__name__)
        self._name = self._config["name"]

        self._logger.info("SoundEvent.__init__ - initializing {}.".format(self._name))
        self._logger.debug("SoundEvent.__init__ - config: ".format(self._config))

        self._pygame_mixer = pygame_mixer
        self._logger.debug("SoundEvent.__init__ - loading wav-file: ".format(self._config["sound-file"]))
        self._pygame_sound = self._pygame_mixer.Sound(os.path.expanduser(self._config["sound-file"]))

        self._volume = float(self._config["volume"])
        if not (0 <= self._volume <= 1):
            err = "SoundEvent.__init__ - volume must be 0<=x<=1 (value in config: {}).".format(self._config["volume"])
            self._logger.error(err)
            raise ValueError(err)
        self._pygame_sound.set_volume(self._volume)

        self._mqtt_client = mqtt_client
        self._message_value = self._config["message-value"]

    def _handler(self, value):
        value = value.decode("utf-8")
        if self._message_value == value:
            self.play()
        else:
            self._logger.debug("SoundEvent._handler ({}) - received unknown value '{}'. expected value '{}'".
                               format(self._name, value, self._message_value))

    def play(self):
        """
        Starts playing sound. If the sound is already beeing played, playback will be stopped and started from
        start.
        """
        self._logger.info("SoundEvent.play ({}) - playing sound.".format(self._name))
        self._pygame_sound.stop()
        self._pygame_sound.play()

    def start(self):
        """
        Subscribes to topic-sub.
        """
        self._logger.info("SoundEvent.start ({}) - subscribing to '{}'.".
                          format(self._name, self._config["topic-sub"]))
        self._mqtt_client.subscribe(self._config["topic-sub"], self._handler)

    def stop(self):
        """
        Unsubscribes from topic-sub and stops playback.
        """
        self._logger.info("SoundEvent.stop ({}) - unsubscribing from '{}'.".
                          format(self._name, self._config["topic-sub"]))
        self._mqtt_client.unsubscribe(self._config["topic-sub"], self._handler)
        self._pygame_sound.stop()
