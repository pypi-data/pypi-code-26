import click
from presentation import Presentation

presentation_obj = Presentation('/home/arun/Projects/bingoarun/folmon/sample-data')

@click.group()
def main():
    pass

@click.command()
def status():
    presentation_obj.getRecentStatus()
    
main.add_command(status)

if __name__ == "__main__":
    main()



