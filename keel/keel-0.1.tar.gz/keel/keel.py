from ui import TerminalUI, start
import argparse
import logging


def arg_setup(p):
    p.add_argument('-u', '--username', type=str, required=True,
                   help="specify a specific username or root will be used by default. problems if user is not real")

    p.add_argument('-m', '--mode', type=str, choices=['connections', 'regular'], required=True,
                   help='select the mode to start out with. default is regular')


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, filename='output.log')
    # todo: see which arguments are needed
    parser = argparse.ArgumentParser(description="Kill processes easily.")
    arg_setup(parser)
    args = vars(parser.parse_args())

    username = args.get('username')
    mode = args.get('mode')

    ui = TerminalUI()
    ui.setup(username, mode)
    start(ui)  # call to the start() method in ui
