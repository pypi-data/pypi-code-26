import re
import time
import urwid
import asyncio
import subprocess as sub
import concurrent.futures
from emlid.devices.tester import Tester
from emlid.devicefactory import DeviceFactory
from emlid.ardupilot.ardupilot import ArdupilotConfigurator, ArdupilotConfiguration, EdgeBoardConfig
from emlid.deviceinfo import DeviceInformation, NotVersionControlledOSReleaseException
from emlid.util.util import ardupilot_should_not_run, ArdupilotIsRunningException

palette = [
    ('body', '', '', '', '#fff', '#111'),
    ('pg complete', '', '', '', '#fff', '#05d'),
    ('invitation', '', '', '', '#fff', '#000'),
    ('test ok', '', '', '', '#fff', '#05d'),
    ('test fail', 'white', 'dark red'),
    ('pg normal', '', '', '', '#fff', '#333'),
]


class Device:
    @staticmethod
    def get_device_information():
        try:
            information = DeviceInformation()
            return information
        except NotVersionControlledOSReleaseException as e:
            MainWindow.quit()

    @staticmethod
    def get_device():
        information = Device.get_device_information()
        device = DeviceFactory(information).create()
        return device


class Emlidtool:
    @staticmethod
    def get_version():
        import pkg_resources
        try:
            version = pkg_resources.require("emlidtool")[0].version
            return "emlidtool version: " + version
        except pkg_resources.DistributionNotFound:
            return "Tool not installed systemwide!"


class InfoWidget:
    def __init__(self):
        self._information = Device.get_device_information()
        self._emlidtool_version = Emlidtool.get_version()

        device_text = urwid.Text(str(self._information), align='left')
        emlidtool_text = urwid.Text(str(self._emlidtool_version), align='left')

        body = [urwid.Divider(), device_text, emlidtool_text]
        body = MainWindow.wrap(body, 'Info')
        self._main_widget = MainWindow.overlay(body)

    @property
    def widget(self):
        return self._main_widget


class TestWidget:
    def __init__(self):
        self._body = [urwid.Divider()]
        try:
            self.run_tests()
        except ArdupilotIsRunningException:
            self._body.append(urwid.Text("Could not run tests because ArduPilot is running"))

        body = MainWindow.wrap(self._body, 'Tests')
        self._main_widget = MainWindow.overlay(body)

    @ardupilot_should_not_run
    def run_tests(self):
        device = Device.get_device()
        tester = Tester(device)
        results = tester.run_tests('all')

        for name, result in results.items():
            if result.result:
                test = urwid.Text("{}: Passed".format(name))
                test = urwid.Padding(test, left=1, right=1)
                test = urwid.AttrWrap(test, 'test ok')
            else:
                test = urwid.Text("{}: Failed\n -- Reason: {}".format(name, result.description))
                test = urwid.Padding(test, left=1, right=1)
                test = urwid.AttrWrap(test, 'test fail')
            self._body.append(test)

    @property
    def widget(self):
        return self._main_widget


class ArdupilotController:

    @staticmethod
    def determine_enabled_on_boot(vehicles):
        on_boot_vehicles = []
        on_boot_count = 0
        for vehicle in vehicles:
            try:
                on_boot_result = sub.check_output('systemctl is-enabled ' + vehicle, shell=True) \
                    .decode('utf-8').strip()
                on_boot_count += 1
                on_boot_vehicles.append(vehicle)
            except sub.CalledProcessError:
                on_boot_result = 'disabled'

        if on_boot_count > 1:
            return on_boot_vehicles, 'warning'

        return on_boot_vehicles, on_boot_result

    def gather_info():
        vehicles_services = ArdupilotController.get_vehicles_services()
        board = Device.get_device_information().product

        vehicles, result = ArdupilotController.determine_enabled_on_boot(vehicles_services)
        if result is 'warning':
            return "You have multiple Ardupilots enabled on boot: {}. Please, fix it.".format(vehicles)

        if not vehicles:
            on_boot_info = "Ardupilot isn't enabled on boot\n"
        else:
            on_boot_info = 'On boot enabled: {}\n'.format(EdgeBoardConfig.get_edge_vehicle()) if board == "Edge" else \
                'On boot enabled: {}\n'.format(vehicles)

        running_vehicle = ArdupilotController.determine_running_ardupilot(vehicles_services)
        if running_vehicle:
            if board == "Edge":
                ardupilot_info = "{} - active (running)".format(EdgeBoardConfig.get_edge_vehicle().title())
            else:
                output = sub.check_output('update-alternatives --display ' + running_vehicle, shell=True).decode('utf-8')
                current = re.findall(r'link[a-z0-9 /.\-]*', output)
                version = re.findall(r'ardu[a-z]+-[0-9].[0-9]', current[0])
                cur_frame = re.findall(r"ardu[a-z\-]*$", current[0])
                ardupilot_info = '{} - active (running)\n' \
                                 'Version: {}\n' \
                                 'Frame: {}\n'.format(running_vehicle.title(), version[0], cur_frame[0])
        else:
            ardupilot_info = "Ardupilot isn't running"
        return on_boot_info + ardupilot_info

    @staticmethod
    def determine_running_ardupilot(vehicles):
        for vehicle in vehicles:
            try:
                sub.check_output('systemctl status ' + vehicle, shell=True).decode('utf-8')
                return vehicle
            except sub.CalledProcessError:
                continue
        return None

    @staticmethod
    def stop_ardupilot(widget, vehicle):
        try:
            sub.check_call('systemctl stop ' + vehicle[0], shell=True)

            info = ArdupilotController.gather_info()
            ArdupilotInfoWidget.update_ardupilot_info(vehicle[1], info)
        except sub.CalledProcessError:
            ArdupilotInfoWidget.update_ardupilot_info(vehicle[1], 'Cannot stop Ardupilot')

    @staticmethod
    def get_vehicles_services():
        board = Device.get_device_information().product
        if board == "Edge":
            edge_vehicles_wrapper = 'ardupilot-wrapper'
            return [edge_vehicles_wrapper]
        else:
            return ['arducopter', 'arduplane', 'ardurover']


class ArdupilotInfoWidget:
    def __init__(self):
        info = ArdupilotController.gather_info()
        status = urwid.Text(str(info))

        body = [urwid.Divider(), status]
        body = MainWindow.wrap(body, 'Ardupilot Info')
        self._main_widget = body

    @staticmethod
    def update_ardupilot_info(main_window, info):
        main_loop = main_window._window
        columns = main_loop.widget
        left_column = columns.contents[1][0]
        ardupilot_info_widget = left_column.contents[1][0]
        main_widget = ardupilot_info_widget.base_widget
        main_widget.body[1] = urwid.Text(info)

    @property
    def widget(self):
        return self._main_widget


class ArdupilotWidget:
    def __init__(self, main_window):
        vehicles_services = ArdupilotController.get_vehicles_services()
        self._number_of_widgets, self._widgets_places = ArdupilotWidget.get_widgets_places()

        self._version = ""
        self._frame = ""

        self._main_window = main_window
        self._help_title = urwid.Text("Press 'q' to quit", align='left')
        body = [self._help_title]

        vehicle = ArdupilotController.determine_running_ardupilot(vehicles_services)

        autopilot_is_running = vehicle is not None
        if autopilot_is_running:
            enabled, button = self.set_ardupilot_stop_button(vehicle)
            body.extend((urwid.Divider(), enabled, button))

        self._on_boot_dict = {
            'enable': urwid.Button("enable"),
            'disable': urwid.Button("disable")
        }

        self._run_dict = {
            'start': urwid.Button("start"),
            'stop': urwid.Button("stop")
        }

        self._contents_list = self._number_of_widgets * [None]

        information = Device.get_device_information()
        self._configurator = ArdupilotConfigurator(information.product)
        self._product = self._configurator.board.get_product()

        self._vehicles_checkboxes = self.create_checkboxes('vehicle', self.set_current_vehicle)
        self._checkboxes_widget = urwid.Pile([self._vehicles_checkboxes])

        self._contents_list[self._widgets_places['vehicle']] = self._vehicles_checkboxes

        body.extend((urwid.Divider(), self._checkboxes_widget))
        body = MainWindow.wrap(body, 'Ardupilot')
        self._main_widget = MainWindow.overlay(body)

    @staticmethod
    def get_widgets_places():
        board = Device.get_device_information().product
        if board == "Edge":
            number_of_widgets = 4
            widgets_places = {
                'vehicle':  0,
                'version':  None,
                'frame' :   None,
                'boot'  :   1,
                'run'   :   2,
                'apply' :   3,
                'result':   4
            }
        else:
            number_of_widgets = 6
            widgets_places = {
                'vehicle':  0,
                'version':  1,
                'frame' :   2,
                'boot'  :   3,
                'run'   :   4,
                'apply' :   5,
                'result':   6
            }
        return number_of_widgets, widgets_places

    def set_ardupilot_stop_button(self, vehicle):
        enabled = urwid.Text("{} is running".format(vehicle.title()), align='left')
        stop_button = urwid.Button("Stop")
        urwid.connect_signal(stop_button, 'click', ArdupilotController.stop_ardupilot, [vehicle, self._main_window])
        return enabled, urwid.AttrMap(stop_button, 'pg normal', 'pg complete')

    def create_checkboxes(self, type, signal):
        invitation = urwid.Text('Choose your ' + type)
        invitation = urwid.AttrMap(invitation, 'invitation')
        checkboxes = [urwid.Divider(), invitation]

        if type is 'vehicle':
            items = self._configurator.vehicles
        elif type is 'version':
            items = self._configurator.board.get_versions(self._vehicle, self._product)
        elif type is 'frame':
            items = self._configurator.board.get_frames(self._vehicle, self._product, self._version)

        for i in range(len(items)):
            checkbox = urwid.Button(items[i])
            urwid.connect_signal(checkbox, 'click', signal, items[i])
            checkbox = urwid.AttrMap(checkbox, 'pg normal', 'pg complete')
            checkboxes.append(checkbox)

        return urwid.Pile(checkboxes)

    def create_menu(self, invitation_text, items, handler):
        invitation = urwid.Text(invitation_text)
        menu = [urwid.Divider(), invitation]

        for text, item in items.items():
            urwid.connect_signal(item, 'click', handler, text)
            choice = urwid.AttrMap(item, 'pg normal', 'pg complete')
            menu.append(choice)

        return urwid.Pile(menu)

    def create_apply_menu(self):
        apply_button = urwid.Button("Apply")
        urwid.connect_signal(apply_button, 'click', self.add_hint_and_apply)
        apply_button = urwid.AttrMap(apply_button, 'pg normal', 'pg complete')

        quit_button = urwid.Button("Quit")
        urwid.connect_signal(quit_button, 'click', MainWindow.quit)
        quit_button = urwid.AttrMap(quit_button, 'pg normal', 'pg complete')

        menu = [urwid.Divider(), apply_button, quit_button]
        return urwid.Pile(menu)

    def clear_and_insert_widgets(self, focus):
        self._checkboxes_widget.contents.clear()
        for i in range(0, focus + 1):
            self._checkboxes_widget.contents.insert(i, (self._contents_list[i], self._checkboxes_widget.options()))
        self._checkboxes_widget.focus_item = focus

    def set_current_vehicle(self, widget, vehicle):
        self._vehicles_checkboxes.contents[2][0].keypress(1, '')
        self._vehicle = vehicle
        if Device.get_device_information().product != "Edge":
            self._version_menu = self.create_checkboxes('version', self.set_current_version)
            self._contents_list[self._widgets_places['version']] = self._version_menu
            self.clear_and_insert_widgets(self._widgets_places['version'])
        else:
            self._on_boot_menu = self.create_menu('On boot:', self._on_boot_dict, self.set_on_boot)
            self._contents_list[self._widgets_places['boot']] = self._on_boot_menu
            self.clear_and_insert_widgets(self._widgets_places['boot'])

    def set_current_version(self, widget, version):
        self._version = version
        self._frame_menu = self.create_checkboxes('frame', self.set_current_frame)
        self._contents_list[self._widgets_places['frame']] = self._frame_menu
        self.clear_and_insert_widgets(self._widgets_places['frame'])

    def set_current_frame(self, widget, frame):
        self._frame = frame
        self._on_boot_menu = self.create_menu('On boot:', self._on_boot_dict, self.set_on_boot)
        self._contents_list[self._widgets_places['boot']] = self._on_boot_menu
        self.clear_and_insert_widgets(self._widgets_places['boot'])

    def set_on_boot(self, widget, on_boot):
        self._on_boot = on_boot
        self._run_menu = self.create_menu('Ardupilot:', self._run_dict, self.set_run)
        self._contents_list[self._widgets_places['run']] = self._run_menu
        self.clear_and_insert_widgets(self._widgets_places['run'])

    def set_run(self, widget, run):
        self._run = run
        self._apply_menu = self.create_apply_menu()
        self._contents_list[self._widgets_places['apply']] = self._apply_menu
        self.clear_and_insert_widgets(self._widgets_places['apply'])

    def apply(self):
        configuration = ArdupilotConfiguration(self._product, self._vehicle, self._frame, self._version)
        output = ArdupilotConfigurator.configure(configuration)
        result = urwid.Text(output)
        ardupilot_service = "ardupilot-wrapper" if self._product == "edge" else "ardu"+self._vehicle

        try:
            sub.check_call('systemctl ' + self._on_boot + ' ' + ardupilot_service + " 2> /dev/null", shell=True)
            on_boot_result_text = '{} is {}d on boot\n'.format(self._vehicle.title(), self._on_boot)
        except sub.CalledProcessError:
            on_boot_result_text = 'Failed to setup {} on boot\n'.format(self._vehicle)
        on_boot_result = urwid.Text(on_boot_result_text)

        try:
            sub.check_output('systemctl ' + self._run + ' ' + ardupilot_service, shell=True)
            if self._run is 'start':
                time.sleep(10)
                sub.check_output('systemctl status ' + ardupilot_service, shell=True)
            run_result_text = '{} {}'.format(self._run, self._vehicle)
        except sub.CalledProcessError as e:
            run_result_text = 'Failed to {} {}. Status:\n'.format(self._run, self._vehicle)
            run_result_text += e.output.decode('utf-8')

        info = ArdupilotController.gather_info()
        ArdupilotInfoWidget.update_ardupilot_info(self._main_window, info)

        run_result_text = urwid.Text(run_result_text)
        widg = urwid.Pile([result, on_boot_result, run_result_text])
        self._checkboxes_widget.contents[self._widgets_places['result']] = (widg, self._checkboxes_widget.options())
        self._future.shutdown()

    def add_hint_and_apply(self, widget):
        self.add_hint()
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)
        self._future = executor.submit(self.apply)

    def add_hint(self):
        wait_text = urwid.Pile([urwid.Text('Please, wait while changes are applying')])
        self._checkboxes_widget.contents.insert(self._widgets_places['result'], (wait_text, self._checkboxes_widget.options()))

    @staticmethod
    def cancel(widget):
        MainWindow.quit()

    def get_items(self, type):
        if type is None:
            items = ArdupilotConfigurator.vehicles()
        return items

    @property
    def widget(self):
        return self._main_widget


class MainWindow:
    def __init__(self):
        self._info_widget = InfoWidget()
        self._test_widget = TestWidget()
        self._ardupilot_widget = ArdupilotWidget(self)
        self._ardupilot_info_widget = ArdupilotInfoWidget()
        self._window = self.create_window()
        self._window.screen.set_terminal_properties(colors=256)

    def create_window(self):
        left_column = urwid.Pile([self._ardupilot_widget.widget])
        right_column = urwid.Pile([self._info_widget.widget,
                                   self._ardupilot_info_widget.widget,
                                   self._test_widget.widget])
        columns = urwid.Columns([left_column, right_column])

        loop = asyncio.get_event_loop()

        return urwid.MainLoop(columns, palette, unhandled_input=self.exit_on_q,
                              event_loop=urwid.AsyncioEventLoop(loop=loop))

    def run(self):
        self._window.run()

    @staticmethod
    def overlay(body):
        return urwid.Overlay(body, urwid.SolidFill(u' '), align='left',
                             width=('relative', 100), valign='bottom',
                             height=('relative', 100), min_width=55, min_height=10)

    @staticmethod
    def wrap(body, text):
        body = urwid.ListBox(urwid.SimpleFocusListWalker(body))
        body = urwid.Padding(body, left=1, right=1)
        body = urwid.LineBox(body, text)
        return urwid.AttrWrap(body, 'body')

    @staticmethod
    def exit_on_q(key):
        if key in ('q', 'Q'):
            raise urwid.ExitMainLoop()

    @staticmethod
    def quit(widget):
        raise urwid.ExitMainLoop()
