from yangsgoogle.credentials import CredentialManager, ServiceMap
from yangsutil import Printer, LogUtil

SERVICE = {
    'version': 'v4',
    'discovery_url': 'https://sheets.googleapis.com/$discovery/rest?version=v4',
    'scope': [
        'https://www.googleapis.com/auth/spreadsheets'
    ]
}


class YangsGoogleSheets:

    def __init__(self, app_name, user_name, credential_root, logger=None):
        self.logger = LogUtil.get_logger(app_name=app_name) if logger is None else logger

        self.service = CredentialManager(logger=self.logger).service(
            service_name=ServiceMap.SHEETS,
            app_name=app_name,
            user_name=user_name,
            credential_root=credential_root
        )

    # public
    def read(self, option):

        if option is None:
            self.logger.info('option is None')
            return

        sheet_id = option['id']
        self.logger.debug("Sheet ID >> %s" % sheet_id)

        if type(option['range']) is str:

            sheet_range = '%s!%s' % (option['sheet'], option['range'])
            self.logger.debug("Sheet range >> %s" % sheet_range)

            result = self.service.spreadsheets().values().get(
                spreadsheetId=sheet_id,
                range=sheet_range
            ).execute()
            values = result.get('values', [])

        elif type(option['range']) is list:

            sheet_ranges = [('%s!%s' % (option['sheet'], range_item)) for range_item in option['range']]
            self.logger.debug("Sheet range >> %s" % Printer.list(sheet_ranges, is_show=False))

            result = self.service.spreadsheets().values().batchGet(
                spreadsheetId=sheet_id,
                ranges=sheet_ranges
            ).execute()
            values = result.get('values', [])
        else:
            values = []

        return values

    def write(self, option, data):
        if option is None:
            self.logger.info('option is None')
            return

        if len(data) == 0 or data is None:
            self.logger.info('data is None')
            return

        sheet_id = option['id']
        self.logger.debug("Sheet ID >> %s" % sheet_id)

        if type(data[0]) == dict:  # multiple range

            for one_data in data:
                one_data['range'] = '%s!%s' % (option['sheet'], one_data['range'])
                self.logger.debug("Sheet range >> %s" % one_data['range'])

            result = self.service.spreadsheets().values().batchUpdate(
                spreadsheetId=sheet_id,
                body={
                    'valueInputOption': "USER_ENTERED",
                    'data': data
                }
            ).execute()
            self.logger.info('Result : %s' % str(result))

        elif type(data[0]) == list:  # one range

            sheet_range = '%s!%s' % (option['sheet'], option['range'])
            self.logger.debug("Sheet range >> %s" % sheet_range)

            result = self.service.spreadsheets().values().update(
                spreadsheetId=sheet_id,
                range=sheet_range,
                valueInputOption="USER_ENTERED",
                body={
                    "majorDimension": "ROWS",
                    "values": data
                }
            ).execute()
            self.logger.info('Result : %s' % str(result))

        else:
            pass

    def append(self, option, data, insert_option=None):

        if option is None:
            self.logger.info('option is None')
            return

        if len(data) == 0 or data is None:
            self.logger.info('data is None')
            return

        sheet_id = option['id']
        self.logger.debug("Sheet ID >> %s" % sheet_id)

        sheet_range = '%s!%s' % (option['sheet'], option['range'])
        self.logger.debug("Sheet range >> %s" % sheet_range)

        if insert_option is None:
            starter = self.service.spreadsheets().values().append(
                spreadsheetId=sheet_id,
                range=sheet_range,
                valueInputOption="USER_ENTERED",
                body={
                    "majorDimension": "ROWS",
                    "values": data
                }
            )

        else:
            starter = self.service.spreadsheets().values().append(
                spreadsheetId=sheet_id,
                range=sheet_range,
                valueInputOption="USER_ENTERED",
                insertDataOption=insert_option,
                body={
                    "majorDimension": "ROWS",
                    "values": data
                }
            )

        input_result = starter.execute()
        self.logger.info("Result : %s" % str(input_result))
