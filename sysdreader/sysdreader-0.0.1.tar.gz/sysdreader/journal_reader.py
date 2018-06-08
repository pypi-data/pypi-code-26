from systemd import journal
from io import StringIO


class JournalReader:

    def __init__(self, logLevel=7):
        self.logLevel = logLevel
        self.reader = journal.Reader()
        self.reader.log_level(self.logLevel)

    def get_service_journal(self, service_name, output_directory, date=None,
                            boot_id=None):
        self.reader.add_match(_SYSTEMD_UNIT=service_name)
        self.reader.add_disjunction()
        self.reader.add_match(_PID=1)
        self.reader.this_boot(boot_id)
        if date is not None:
            self.reader.seek_realtime(date)
        log = StringIO()
        for entry in self.reader:
            log.write(str(entry.get('__REALTIME_TIMESTAMP')) +
                      " " + entry.get('MESSAGE') + "\n")
        with open(output_directory, 'w') as log_file:
            log_file.write(log.getvalue())
        log.close()
