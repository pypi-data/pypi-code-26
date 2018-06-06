import curses
from curses import textpad
import sys
import logging
from mode import *
log = logging.getLogger(__name__)


class TerminalUI:
    def __init__(self, padding_x=6, padding_y=1, spaces=3):
        self.current_mode = None
        self.current_user = None
        self.MIN_CURSOR_Y = 2
        self.MIN_CURSOR_X = 0
        self.cursor_x = 2
        self.cursor_y = 2
        self.stdscr = None
        self.last_key_pressed = 0
        self.START_HEIGHT, self.START_WIDTH = 0, 0
        self.HEIGHT, self.WIDTH = None, None
        self.PADDING_X = padding_x
        self.PADDING_Y = padding_y
        self.last_elem_x = self.last_elem_y = 2
        self.existing_elements = {}
        self.enter = 10
        self.title = ""
        self.spaces = ' ' * spaces
        # self.status_bar_setup('Press q to exit')

    def init_scr(self, stdscr):
        self.stdscr = stdscr
        # init height and width when knowing the screen size
        self.HEIGHT, self.WIDTH = self.stdscr.getmaxyx()
        self.color_setup()

    def change_mode(self, new_mode):
        self.current_mode = new_mode

    def change_user(self, new_user):
        self.current_user = new_user

    def setup(self, user, mode):
        # setup user
        if user is None:
            self.current_user = 'root'
        else:
            self.current_user = user

        # setup mode
        if mode == 'connections':
            self.current_mode = OpenConnectionsMode(user)
        else:
            self.current_mode = Mode(user)

    def set_title(self, string):
        string = string[:self.WIDTH - 1]
        start_y = 0
        start_x_title = int((self.WIDTH // 2) - (len(string) // 2) - len(string) % 2)
        self.stdscr.attron(curses.color_pair(2))
        self.stdscr.attron(curses.A_BOLD)
        self.stdscr.addstr(start_y, start_x_title, string)
        self.stdscr.attroff(curses.color_pair(2))
        self.stdscr.attroff(curses.A_BOLD)
        self.title = string

    # def status_bar_setup(self, statusbarstr):
    #     self.stdscr.attron(curses.color_pair(3))
    #     self.stdscr.addstr(self.HEIGHT - 1, 0, statusbarstr)
    #     self.stdscr.addstr(self.HEIGHT - 1, len(statusbarstr), " " * (self.WIDTH - len(statusbarstr) - 1))
    #     self.stdscr.attroff(curses.color_pair(3))

    @staticmethod
    def color_setup():
        curses.start_color()
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)

    def refresh(self):
        self.stdscr.refresh()
        # is this where I need to update the items so that they show up?
        self.last_key_pressed = self.stdscr.getch()

    def clear(self):
        self.stdscr.clear()

    def highlight(self):
        for elem in self.existing_elements.keys():
            y, x = self.existing_elements[elem][0], self.existing_elements[elem][1]
            if y == self.cursor_y:
                for i in range(0, len(elem) + 1):
                    self.stdscr.chgat(self.cursor_y, x + i, 1, curses.A_REVERSE)

    def shift_items_down(self):
        for elem in self.existing_elements.keys():
            self.existing_elements[elem][0] += self.PADDING_Y

    def shift_items_up(self):
        for elem in self.existing_elements.keys():
            self.existing_elements[elem][0] -= self.PADDING_Y

    def items_below_exist(self):
        items = []
        for elem in self.existing_elements.keys():
            if self.existing_elements[elem][0] > self.HEIGHT:
                items.append(elem)
        return len(items) != 0

    def items_above_exist(self):
        items = []
        for elem in self.existing_elements.keys():
            if self.existing_elements[elem][0] < self.MIN_CURSOR_Y:
                items.append(elem)
        return len(items) != 0

    def move(self):
        self.stdscr.move(self.cursor_y, self.cursor_x)

    def next_move(self):
        if self.last_key_pressed == curses.KEY_DOWN and self.items_below_exist():
            if self.cursor_y == self.HEIGHT - 1:
                self.shift_items_up()
            self.cursor_y = self.cursor_y + self.PADDING_Y
        elif self.last_key_pressed == curses.KEY_UP:
            if self.cursor_y == self.MIN_CURSOR_Y and self.items_above_exist():
                self.shift_items_down()
            self.cursor_y = self.cursor_y - self.PADDING_Y
        elif self.last_key_pressed == curses.KEY_RIGHT:
            self.cursor_x = self.cursor_x + self.PADDING_X
        elif self.last_key_pressed == curses.KEY_LEFT:
            self.cursor_x = self.cursor_x - self.PADDING_X

    # "pid : name" -> y,x coordinates
    def add(self, string):
        self.existing_elements[string] = [self.last_elem_y, self.last_elem_x]

    # def add(self, item):
    #     self.existing_elements[] = []

    def go_down(self):
        self.last_elem_y += self.PADDING_Y

    def go_up(self):
        self.last_elem_y -= self.PADDING_Y

    def go_right(self):
        self.last_elem_x += self.PADDING_X

    def go_left(self):
        self.last_elem_x -= self.PADDING_X

    def reset_x(self):
        self.last_elem_x = 0

    def reset_y(self):
        self.last_elem_y = 0

    def check_move_validity(self):
        self.cursor_x = max(self.MIN_CURSOR_X, self.cursor_x)
        self.cursor_x = min(self.WIDTH - 1, self.cursor_x)

        self.cursor_y = max(self.MIN_CURSOR_Y, self.cursor_y)
        self.cursor_y = min(self.HEIGHT - 1, self.cursor_y)

    def get_cursor_pointing_elem(self):
        for elem in self.existing_elements:
            y = self.existing_elements[elem][0]
            if y == self.cursor_y:
                return elem
        return None

    def check_kill(self):
        if self.last_key_pressed == self.enter:
            elem = self.get_cursor_pointing_elem()
            split_elem = elem.split(':')
            pid = int(split_elem[0].strip(' '))
            name = split_elem[1].strip(' ')
            log.info('Killing PID: ' + str(pid) + ' with name: ' + name)
            self.current_mode.kill_process(pid)
            y, x = self.existing_elements[elem]
            self.existing_elements.pop(elem, None)
            for item in self.existing_elements.keys():
                if self.existing_elements[item][0] > y:
                    self.existing_elements[item][0] -= self.PADDING_Y
            self.clear()
            self.draw()
            self.highlight()
            self.set_title(self.title)

    def check_if_empty(self):
        if len(self.existing_elements.keys()) == 0:
            sys.exit(0)

    def show(self):
        self.draw()
        self.next_move()
        self.check_move_validity()
        self.move()
        self.highlight()
        self.check_kill()
        self.check_if_empty()

    def get_last_key_pressed(self):
        return self.last_key_pressed

    def check_change_mode(self):
        if self.last_key_pressed == ord('m'):
            # todo: show textbox to input new mode and then update
            self.set_title('button pressed: m')

    def check_change_user(self):
        if self.last_key_pressed == ord('u'):
            # todo: show textbox to input new user and then update
            textpad.Textbox(self.stdscr).edit()

    def get_mode(self):
        return self.current_mode

    def get_current_user(self):
        return self.current_user

    def get_items(self):
        return self.current_mode.get_processes()

    def populate(self, processes):
        for item in processes:
            self.add(str(item['pid']) + self.spaces + ":" + self.spaces + item['name'])
            # self.add(item)
            self.go_down()

    def draw(self):
        for elem in self.existing_elements.keys():
            if self.HEIGHT > self.existing_elements[elem][0] >= self.MIN_CURSOR_Y:
                self.stdscr.addstr(self.existing_elements[elem][0], self.existing_elements[elem][1], elem)


def run(stdscr, ui):
    import logging
    ui.init_scr(stdscr)
    shown = False
    while ui.get_last_key_pressed() != ord('q'):
        # see if user clicked a button to change mode
        ui.check_change_mode()
        # see if user clicked a button to change user
        ui.check_change_user()

        ui.clear()
        # set title based on the current mode
        ui.set_title(ui.get_mode().get_title() + ', user: ' + ui.get_current_user() + ', mode: ' + str(ui.get_mode()))

        # populate
        if not shown:
            ui.populate(ui.get_items())
            shown = True

        # finally show
        ui.show()
        ui.refresh()


def start(ui):
    curses.wrapper(run, ui)

