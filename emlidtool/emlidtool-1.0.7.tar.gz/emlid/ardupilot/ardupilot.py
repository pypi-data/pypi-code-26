import subprocess as sub
import configparser
import re

from emlid.util.util import root_should_execute


class CannotConfigureException(Exception):
    pass


class ArdupilotConfiguration:
    def __init__(self, product, vehicle, frame, version):
            self.product = product
            self.vehicle = vehicle
            self.frame = frame
            self.version = version


class EdgeBoardConfig():
    ardupilot_path = '/etc/ardupilot/ardupilot.conf'

    def __init__(self, product):
        self.vehicles = ['arducopter', 'arducopter-heli', 'arduplane', 'ardurover', 'ardusub']
        self._product = product

    @staticmethod
    def get_edge_vehicle():
        config_parser = configparser.ConfigParser()
        config_parser.read(EdgeBoardConfig.ardupilot_path)
        return config_parser.get('Vehicle', 'type')

    @staticmethod
    def get_product():
        return "edge"

    @staticmethod
    def get_frames(vehicle, product, version):
        return [""]

    @staticmethod
    def get_versions(vehicle, product):
        return [""]

    @staticmethod
    def try_to_configure(config):
        try:
            config_parser = configparser.ConfigParser()
            config_parser.read(EdgeBoardConfig.ardupilot_path)
            config_parser.set('Vehicle', 'type', config.vehicle)

            with open(EdgeBoardConfig.ardupilot_path, 'w') as configfile:
                config_parser.write(configfile)
        except (configparser.NoSectionError, IOError):
            raise CannotConfigureException('Cannot open ardupilot.conf')

        return " {}\n".format(config.vehicle)


class NavioBoardConfig():
    def __init__(self, product):
        self.vehicles = ['copter', 'plane', 'rover']
        self._product = product

    @staticmethod
    def get_all_versions(vehicle, product):
        output = sub.check_output('update-alternatives --display ardu' + vehicle, shell=True).decode('utf-8')
        available_versions = ''
        for alternative in output.splitlines():
            if '/' + product + '/' in alternative:
                available_versions += alternative + '\n'
        return available_versions

    def get_versions(self, vehicle, product):
        output = self.get_all_versions(vehicle, product)
        versions = list(set(re.findall(r'[0-9]+\.[0-9]+', output)))
        versions = sorted(versions)
        return versions

    def get_product(self):
        if self._product == "Navio+":
            return "navio"
        else:
            return "navio2"

    @staticmethod
    def get_frames(vehicle, product, version):
        output = sub.check_output('update-alternatives --display ardu' + vehicle, shell=True).decode('utf-8')
        available_frames = ''
        for alternative in output.splitlines():
            if '/' + product + '/' in alternative:
                if '/ardu' + vehicle + '-' + version + '/' in alternative:
                    available_frames += alternative + '\n'
        frames = list(map(lambda s: s[:-2], re.findall(r'ardu' + vehicle + '-?[a-z-0-9]* -', available_frames)))
        return frames

    @staticmethod
    def try_to_configure(config):
        try:
            sub.check_call(
                "update-alternatives --set ardu" + config.vehicle +
                " /opt/ardupilot/" + config.product + "/ardu" + config.vehicle +
                "-" + config.version + "/bin/" + config.frame + " > /dev/null", shell=True)
        except sub.CalledProcessError:
            raise CannotConfigureException('Cannot run update-alternatives')

        return("\n{} with frame {}.\nardu{} version: {}\n".
            format(config.vehicle, config.frame, config.vehicle, config.version))


class ArdupilotConfigurator:
    def __init__(self, product):
        self._product = product
        self.board = EdgeBoardConfig(product) if product == "Edge" \
            else NavioBoardConfig(product)

        self._vehicles = self.board.vehicles

    @property
    def vehicles(self):
        return self._vehicles

    @staticmethod
    def ask_for_choice(items, name):
        for number in range(len(items)):
            print('{0}) {1}'.format(number + 1, items[number]))
        choice = input("Type selection number for your {}: ".format(name))
        return choice

    def get_choice(self, items, name):
        if len(items) > 1:
            option = self.ask_for_choice(items, name)
            if not 1 <= int(option) <= len(items):
                raise IndexError
            try:
                choice = items[int(option) - 1]
            except (IndexError, ValueError) as e:
                print("Inappropriate {}".format(name))
                raise e
            return choice
        else:
            return items[0]

    def choose_if_exists(self, items, name):
        choice = None
        while choice is None:
            try:
                choice = self.get_choice(items, name)
            except (IndexError, ValueError):
                continue
        return choice

    @root_should_execute
    def get_configuration(self):
        product = self.board.get_product()
        vehicle = self.choose_if_exists(self.vehicles, "vehicle")
        versions = self.board.get_versions(vehicle, product)
        version = self.choose_if_exists(versions, "version")
        frames = self.board.get_frames(vehicle, product, version)
        frame = self.choose_if_exists(frames, "frame")
        return ArdupilotConfiguration(product, vehicle, frame, version)

    @staticmethod
    def configure(config):
        success_message = ArdupilotConfigurator.try_to_configure_board(config)
        return("\nYou've successfully configured"
               "{}".format(success_message))

    @staticmethod
    def try_to_configure_board(config):
        if config.product == "edge":
            return EdgeBoardConfig.try_to_configure(config)
        else:
            return NavioBoardConfig.try_to_configure(config)

