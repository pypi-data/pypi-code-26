"""gcal_to_xlsx: Converting Google Calendar calendars to XLSX

<month_and_year> as well as <google_calendar_name> need to be surrounded
by quotes.

Usage:
    amvernon_gcal_to_xlsx [options] <month_and_year>

Arguments:
    client_secret.json                      Name of client secret (in quotes)
    google_calendar_name                    Name of calendar in Google Calendar (in quotes)
    <month_and_year>                        Example: "September 2017"

Options:
    --client_secret=client_secret.json      Specify location of client_secret [default: client_secret.json]
    --calendar=google_calendar_name         Specify name of calendar. [default: Arthur Murray Vernon Calendar]
    -h --help                               Show this screen.
    --version                               Show version.

"""
import os
import maya
import json
import pathlib
import datetime
import calendar
import httplib2
import xlsxwriter
import argparse
import pandas as pd
from docopt import docopt
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage


__version__ = "0.1.0"
__author__ = "Vincent Chov"
__license__ = "MIT"


def get_credentials(CLIENT_SECRET_FILE='client_secret.json', flags=None):
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    if not os.path.isfile(CLIENT_SECRET_FILE):
        raise IOError("{} not found...".format(CLIENT_SECRET_FILE))
    SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
    APPLICATION_NAME = 'Arthur Murray Vernon Calendar'
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'amvernoncal_credentials.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        print(type(flow))
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else:
            credentials = tools.run_flow(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def get_gcal_by_summary(desired_month_string, summary, service):
    """
        Gets all events from Google Calendar for the current month where the
        calendar's name matches the inputted one.
    """
    # Get the calendarId for the inputted calendar name
    cals = service.calendarList().list().execute()['items']
    calendars = [x for x in cals if summary.lower() in x['summary'].lower()][0]

    cal_id = calendars['id']

    # Get the first and last days of the month
    desired_month = maya.when(desired_month_string)
    first_day = (desired_month.subtract(days=desired_month.day-1)
                              .datetime(to_timezone='US/Eastern').isoformat())
    next_month_string = '{} {}'.format(desired_month.month + 1,
                                       desired_month.year)
    next_month = maya.when(next_month_string)
    last_day = (next_month.subtract(days=next_month.day-1)
                          .datetime(to_timezone='US/Eastern').isoformat())

    # Get all events for this month for the selected calendar
    events = service.events().list(calendarId=cal_id, singleEvents=True,
                                   timeMin=first_day, timeMax=last_day,
                                   orderBy='startTime').execute()

    return events['items']


def format_gcal_to_json(events, raw_filename=''):
    """
        Condenses the relevant info from the Google Calendar events down to be
        closer to the JSON structure we'd get if we went from PDF to JSON.
    """
    fmtd_events = []
    for event in events:
        index = len(fmtd_events) - 1

        date_time = (maya.parse(event['start']['dateTime'])
                         .datetime(to_timezone='US/Eastern'))
        date = date_time.strftime('%d').lstrip('0')

        # Get or create an object for the current date
        obj_exists = len(fmtd_events) != 0 and date in fmtd_events[-1]['date']
        if obj_exists:
            obj = fmtd_events[-1]
        else:
            obj = {'date': date, 'events': []}

        # Event Category/Title
        category = event['summary']

        # Get the timestamp for this event only if the studio is open right now
        if 'Studio Closed'.lower() not in event['summary'].lower():
            time = date_time.strftime('%I:%M%p').lstrip('0') + '\n'
        else:
            time = ''

        event_obj = {
            'Event': category,
            'Time': time
        }

        description_str = event.get('description', '')
        has_style = 'style' in description_str.lower()
        descriptions = description_str.splitlines()
        if has_style:
            style = descriptions[0].replace('Style: ', '')
            if len(descriptions) > 1:
                event_obj['Description'] = description
            else:
                style += ' '
        else:
            if descriptions:
                style = '\n '
                description = '\n'.join(descriptions) + '\n'
                obj['Description'] = description
            else:
                style = ''

        event_obj['Style'] = style
        # Add the event object to the current day's object
        obj['events'].append(event_obj)

        # Either modify the existing event in-place or add a new one
        if obj_exists:
            fmtd_events[index] = obj
        else:
            fmtd_events.append(obj)

    filename = "Output/{}.json".format(raw_filename)
    with open(filename, 'w') as json_file:
        json_file.write(json.dumps(fmtd_events, indent=4, sort_keys=True))
    return fmtd_events


def generate_cal_strings(day_json, workbook):
    """
        For a given day's JSON object, generate string of the structure that
        the printable PDF would use, with xlsxwriter formats.
    """
    bold_italics_fmt = workbook.add_format({
        'bold': True,
        'italic': True,
        'font_name': 'Times New Roman'
    })
    italics_fmt = workbook.add_format({
        'italic': True,
        'font_name': 'Times New Roman'
    })

    events_list = day_json['events']
    event_strings = []
    for e in events_list:
        event_strings += [bold_italics_fmt, e['Event'] + '\n']
        event_strings += [italics_fmt, e['Style']]
        event_strings += [bold_italics_fmt, e.get('Description', '')]
        event_strings += [italics_fmt, '{}\n'.format(e['Time'])]

    event_strings[-1] += '\n'

    day_str = (
        [bold_italics_fmt, day_json['date'] + '\n\n'] +
        event_strings +
        [bold_italics_fmt, day_json.get('Description', '')]
    )
    return day_str


def gcal_events_to_xlsx(desired_month_string, calendar_title, service):
    """
        For a given month, put all of the Google Calendar events into a JSON
        and then output an XLSX file with the JSON's data formatted.
    """
    events = [
        e for e in
        get_gcal_by_summary(desired_month_string, calendar_title, service)
        if 'dance lesson' not in e['summary'].lower()
    ]

    filename = desired_month_string.lower().replace(' ', '_')
    fmtd_events = format_gcal_to_json(events, filename)

    # ints arranged like a calendar's days of the week
    month = maya.when(desired_month_string)
    month_cal = (calendar.TextCalendar(calendar.SUNDAY)
                         .monthdayscalendar(month.year, month.month))

    # Create the XLSX writer and set the font format
    filename = desired_month_string.lower().replace(' ', '_')
    workbook = xlsxwriter.Workbook('Output/{}.xlsx'.format(filename))
    worksheet = workbook.add_worksheet()

    # Add on the event strings to each day in the calendar
    for i, week_cell in enumerate(month_cal):
        for j, day_cell in enumerate(week_cell):
            if day_cell != 0 and day_cell <= len(fmtd_events):
                day_json = fmtd_events[day_cell-1]
                day_strings = generate_cal_strings(day_json, workbook)
                worksheet.write_rich_string(i, j, *day_strings)
    print('Done!')
    return workbook


def main():
    args = docopt(__doc__, version=__version__)

    client_secret_path = args.get('--client_secret', None)
    month_year = args['<month_and_year>']
    calendar_name = args.get('--calendar', None)
    
    # Prompt user for permission using argparse if we don't already have it
    try:
        flags = tools.argparser.parse_args([])
    except:
        flags = None

    if not client_secret_path:
        credentials = get_credentials(flags=flags)
    else:
        credentials = get_credentials(CLIENT_SECRET_FILE=client_secret_path,
                                      flags=flags)
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    pathlib.Path('JSONs').mkdir(parents=True, exist_ok=True)
    pathlib.Path('PDFs').mkdir(parents=True, exist_ok=True)
    pathlib.Path('Output').mkdir(parents=True, exist_ok=True)

    if not calendar_name:
        calendar_name = "Arthur Murray Vernon Calendar"
    
    try:
        book = gcal_events_to_xlsx(month_year, calendar_name, service)
        book.close()
    except IndexError as e:
        raise ValueError("Calendar not found or no events found") from e


if __name__ == '__main__':
    main()
