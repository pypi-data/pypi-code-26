import click
from presentation import Presentation


'''
TODO commands

folmon status
(show current overall status)

- to show diff in size, percentage increased for all below

folmon diff --start-date 14-01-2018 --end-date 20-01-2018 /usage/fruits
(show the diff in size of all the folders under /usage/fruits also the overall folder size)
  - to show diff in size, percentage increased

folmon diff --numofdays 7 /usage/vegetables
(show the diff in size of the folders under /usage/vegetables for the last 7 days)

folmon show --numofdays 10 /usage
(show a matrix of the folder and subfolder's size for the past 10 days )

'''

presentation_obj = Presentation('/home/arun/Projects/bingoarun/folmon/sample-data')

@click.group()
def main():
    pass

@click.command()
def status():
    presentation_obj.getRecentStatus()

@click.command()
@click.option('--start_date','-s',help='Start date in format yyyy-mm-dd')
@click.option('--end_date','-e',help='End date in format yyyy-mm-dd')
@click.option('--num_days','-n',type=int,help='Recent number of days')
@click.option('--folder','-f',type=str,help='Absolute folder path')
def diff(start_date,end_date,num_days,folder):
    if start_date != None and end_date != None :
        presentation_obj.getBetweenDates(start_date,end_date,folder)



    
main.add_command(status)
main.add_command(diff)

if __name__ == "__main__":
    main()