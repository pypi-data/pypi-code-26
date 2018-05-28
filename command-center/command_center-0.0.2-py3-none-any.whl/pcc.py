from subprocess import Popen
import sys
import os
import json
from tkinter import Tk, Button


def load_scripts():
    if os.path.isfile('pcc.json'):
        with open('pcc.json') as f:
            return json.load(f)

    if os.path.isfile('package.json'):
        with open('package.json') as f:
            return json.load(f)['scripts']


def parse_args():
    args_data = {}
    extra = {}
    for arg in sys.argv[1:]:
        key, value = arg.split('=', maxsplit=1)
        if key.startswith('--'):
            args_data[key[2:]] = value
        else:
            extra[key] = value

    args_data['extra'] = extra
    return args_data


def print_header(line):
    bars = '\u2550' * (len(line)+2)
    print(''.join(['\u2554', bars, '\u2557']))
    print(' '.join(['\u2551', line, '\u2551']))
    print(''.join(['\u255A', bars, '\u255D']))


def script_wrapper(script_command):
    def execute_script():
        print_header('$ ' + script_command)
        Popen(script_command.split(' '))
    return execute_script


def print_help():
    print("""usage: pcc [options] [extra_commands]
    Will look for pcc.json or package.json on start

    options:
      --col=N           Specifies how many columns to display
      extra_commands:   Can specify any number of extra commands to display by
                        using key=value pairs. Note that the key should not
                        contain an equal sign, but the value can.
      """)


def main():
    if len(sys.argv) > 1 and (sys.argv[1] == 'help' or sys.argv[1] == '-h'):
        print_help()
        sys.exit()

    arg_data = parse_args()
    columns = int(arg_data['col']) if 'col' in arg_data else 8
    scripts = load_scripts()
    if len(arg_data['extra']) > 0:
        scripts.update(arg_data['extra'])

    if scripts is None or len(scripts) == 0:
        print_help()
        sys.exit()

    root = Tk()
    root.title('Python Command Center')
    button_settings = dict(ipadx=5, ipady=5, padx=3, pady=3, sticky='EW')
    for i, key in enumerate(scripts):
        button = Button(root, text=key, command=script_wrapper(scripts[key]))
        button.grid(row=i // columns, column=i % columns, **button_settings)
    root.mainloop()


if __name__ == '__main__':
    main()
