import click
from .commands.encoding import encoding
from .commands.esub import esub
from .commands.run import run, rune
from .commands.sdel import sdel
from .commands.which import which
from .commands.pn import pn

@click.group()
def main():
    pass


main.add_command(encoding)
main.add_command(esub)
main.add_command(run)
main.add_command(rune)
main.add_command(sdel)
main.add_command(which)
main.add_command(pn)

if __name__ == '__main__':
    main()
