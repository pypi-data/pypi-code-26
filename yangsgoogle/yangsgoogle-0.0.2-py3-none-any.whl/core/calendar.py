from yangsgoogle.credentials import CredentialManager, ServiceMap
from yangsutil import LogUtil, DateTimeUtil

SERVICE = {
    'version': 'v3',
    'scope': [
        'https://www.googleapis.com/auth/calendar'
    ]
}

CONTAIN_HOLIDAY_NAME = [
    '설날',
    '추석',
    ['대통령', '선거'],
    ['전국동시지방', '선거'],
    ['국회의원', '선거'],
    '대체'
]

HOLIDAY_LIST = [
    '신정',
    '삼일절',
    '어린이날',
    '석가탄신일',
    '현충일',
    '광복절',
    '개천절',
    '한글날',
    '크리스마스',
]


class YangsGoogleCalendar:

    def __init__(self, app_name, user_name, credential_root, logger=None):
        self.logger = LogUtil.get_logger(app_name=app_name) if logger is None else logger

        self.service = CredentialManager(logger=self.logger).service(
            service_name=ServiceMap.CALENDAR,
            app_name=app_name,
            user_name=user_name,
            credential_root=credential_root
        )

        self.holiday_list = None

    # public
    def get_holiday_list(self):

        basic = DateTimeUtil.get_string(output_form='%Y')

        last_year = DateTimeUtil.get_object(
            src_object=basic,
            src_object_form='%Y',
            gap=-1,
            datetime_type=DateTimeUtil.YEARS
        )

        next_year = DateTimeUtil.get_object(
            src_object=DateTimeUtil.get_object(
                src_object=basic,
                src_object_form='%Y',
                gap=2,
                datetime_type=DateTimeUtil.YEARS
            ),
            gap=-1
        )

        event_results = self.service.events().list(
            calendarId='ko.south_korea#holiday@group.v.calendar.google.com',
            timeMin=last_year.isoformat() + 'Z',
            timeMax=next_year.isoformat() + 'Z',
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        events = event_results.get('items', [])

        return [
            {
                'date': event['start']['date'],
                'name': event['summary']
            } for event in events
        ]

    def is_holiday(self, datetime=None, datetime_form='%Y%m%d'):

        if self.holiday_list is None:
            self.holiday_list = self.get_holiday_list()

        event_list = self.holiday_list

        target_date = DateTimeUtil.get_string(
            src_object=datetime,
            src_object_form=datetime_form,
            output_form='%Y-%m-%d'
        )

        target_event = None
        for event in event_list:
            if event['date'] == target_date:
                target_event = event
                break

        if target_event is None:
            return False

        name = target_event['name']
        if name in HOLIDAY_LIST:
            return True

        is_holiday = False
        for contain in CONTAIN_HOLIDAY_NAME:

            if type(contain) == list:

                flag = True
                for contain_item in contain:
                    if contain_item not in name:
                        flag = False

                if flag is True:
                    is_holiday = True
                    break

            else:
                if contain in name:
                    is_holiday = True
                    break

        return is_holiday
