import hippasos.schema as schema
from pelops.abstractmicroservice import AbstractMicroservice
from hippasos.soundevent import SoundEvent
import pygame
from hippasos import version


class SoundService(AbstractMicroservice):
    """
    Hippasos plays preconfigured sound files upon reception of predefined mqtt messages. The events are handled
    independently.

    mqtt:
        mqtt-address: localhost
        mqtt-port: 1883
        mqtt-credentials: ~/credentials.yaml
        log-level: WARNING

    logger:
        log-level: DEBUG
        log-file: hippasos.log

    sound-mappings:
        - name: bell_building  # unique name for sound event
          sound-file: ../resources/church_bell.ogg  # uri to sound file. must be ogg or wav.
          topic-sub: /test/button1  # react to published values on this channel
          message-value: PRESSED  # react to this message content
          volume: 0.1  # 0..1 - volume relative to system volume
          active: True  # entry ignored if set to False
    """

    _version = version

    _sound_events = None  # list of registered sound events

    def __init__(self, config, mqtt_client=None, logger=None):
        """
        Constructor.

        :param config: config yaml structure
        :param mqtt_client: instance of an mqtt client (optional)
        :param logger: instance of a logger (optional)
        """

        AbstractMicroservice.__init__(self, config, "sound-mappings", mqtt_client, logger)

        self._logger.debug("SoundService.__init__ - initializing pygame")
        pygame.init()
        pygame.mixer.init()

        self._logger.info("SoundService.__init__ initializing sound events")
        self._sound_events = []
        for entry in self._config:
            if entry["active"]:
                sound_event = SoundEvent(entry, self._mqtt_client, self._logger, pygame.mixer)
                self._sound_events.append(sound_event)

    @classmethod
    def _get_schema(cls):
        return schema.get_schema()

    def _start(self):
        """
        Starts all sound events.
        """
        for sound_event in self._sound_events:
            sound_event.start()

    def _stop(self):
        """
        Stops all sound events.
        """
        for sound_event in self._sound_events:
            sound_event.stop()

    @classmethod
    def _get_description(cls):
        return "Mqtt microservice to play sounds."


def standalone():
    SoundService.standalone()


if __name__ == "__main__":
    SoundService.standalone()
