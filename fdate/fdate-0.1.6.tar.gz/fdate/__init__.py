import datetime
import time
import doctest


__version__ = '0.1.6'
__author__ = ['Xian Qiu']


__all__ = ['Fdate', 'drange', 'today']


class Fdate(object):

    """ Formatted date string.

    >>> fd = Fdate('2018/4/7')
    >>> fd
    '2018-04-07'
    >>> fe = Fdate(fd)
    >>> fe
    '2018-04-07'
    >>> fd = Fdate().from_timestamp(1523030400)
    >>> fd
    '2018-04-07'
    >>> fd.to_timestamp()
    1523030400
    >>> fd + 8
    '2018-04-15'
    >>> fd -= 7
    >>> fd
    '2018-03-31'
    >>> fd.is_last_day(of='M')  # last day of the month
    True
    >>> fd - '2018-04-30'
    -30
    >>> fd.rank  # '2018-03-31' is the 90th day of the year
    90
    >>> Fdate('2018-04-30') >= '2018-03-31'
    True
    >>> fd[0:4]
    '2018'
    >>> [x for x in drange('2018-03-30', '2018-04-03')]
    ['2018-03-30', '2018-03-31', '2018-04-01', '2018-04-02', '2018-04-03']
    >>> [x for x in drange('2018-04-03', '2018-03-30')]
    ['2018-04-03', '2018-04-02', '2018-04-01', '2018-03-31', '2018-03-30']
    """

    def __init__(self, date_string=None):
        self._dt = None
        self._date = None
        self._init(date_string)

    def _init(self, date=None):
        # case 1: 6 digits yymmdd

        if not date:
            return
        if isinstance(date, str):
            if len(date) == 8 and date.isdigit():
                y, m, d = date[0:4], date[4:6], date[6:8]
            # case 2: yy-mm-dd
            else:
                y, m, d = date.split(date[4])
            self._dt = datetime.datetime.strptime('%s-%s-%s' % (y, m, d), '%Y-%m-%d')
            self._date = self._dt.strftime('%Y-%m-%d')
        elif isinstance(date, Fdate):
            self._date = date._date
            self._dt = date._dt

    def __str__(self):
        return self._date

    def __repr__(self):
        return repr(self._date)

    def __len__(self):
        return len(self._date) if self._date else 0

    def __getitem__(self, key):
        return self._date[key]

    def __hash__(self):
        return hash(self._date)

    def __add__(self, n):
        """
        >>> Fdate('2018-01-01') + 364
        '2018-12-31'
        """
        day = self._dt + datetime.timedelta(days=n)
        return Fdate(day.strftime('%Y-%m-%d'))

    def __sub__(self, x):
        """
        >>> Fdate('2018-12-31') - '2018/1/1'
        364
        >>> Fdate('2018-12-31') - 364
        '2018-01-01'
        """
        if isinstance(x, int):
            day = self._dt + datetime.timedelta(days=-x)
            return Fdate(day.strftime('%Y-%m-%d'))
        elif isinstance(x, str) or isinstance(x, Fdate):
            return (self._dt - Fdate(x)._dt).days

    def __iadd__(self, n):
        """
        >>> fd = Fdate('20180228')
        >>> fd += 1
        >>> fd
        '2018-03-01'
        """
        return self.__add__(n)

    def __isub__(self, n):
        """
        >>> fd = Fdate('20180301')
        >>> fd -= 1
        >>> fd
        '2018-02-28'
        """
        if isinstance(n, int):
            return self.__sub__(n)

    def __eq__(self, date):
        """
        >>> Fdate('2018-04-01') == '2018/4/1'
        True
        >>> Fdate('2018-02-01') == Fdate('20180201')
        True
        """
        return True if Fdate(date)._date == self._date else False

    def __ge__(self, date):
        """
        >>> Fdate('2018-04-01') >= '2018-03-01'
        True
        >>> Fdate('2018-04-01') >= Fdate('2018-04-01')
        True
        """
        return True if self - Fdate(date) >= 0 else False

    def __gt__(self, date):
        """
        >>> Fdate('2018-04-01') > '2018-03-31'
        True
        >>> Fdate('2018-04-01') > Fdate('2018-04-01')
        False
        """
        return True if self - Fdate(date) > 0 else False

    def __le__(self, date):
        """
        >>> Fdate('2018-04-01') <= '2018-03-31'
        False
        >>> Fdate('2018-04-01') <= Fdate('2018-04-01')
        True
        """
        return True if self - Fdate(date) <= 0 else False

    def __lt__(self, date):
        """
        >>> Fdate('2018-04-01') < '2018-03-31'
        False
        >>> Fdate('2018-04-01') < Fdate('2018-04-01')
        False
        """
        return True if self - Fdate(date) < 0 else False

    def from_timestamp(self, timestamp, unit=1):
        """ Initializes Fdate object via unix timestamp.

        :param timestamp: unix timestamp
        :param unit: magnitude of a second, e.g. minisecond: 1000
        :return: Fdate object

        >>> Fdate().from_timestamp(1523030400)
        '2018-04-07'
        >>> Fdate().from_timestamp(1523030400000, unit=1000)
        '2018-04-07'
        """
        assert isinstance(unit, int) and unit > 0, 'unit must be positive integer!'
        self._dt = datetime.datetime.fromtimestamp(timestamp // unit)
        self._date = self._dt.strftime('%Y-%m-%d')
        return self

    def to_timestamp(self, unit=1):
        """ Gets unix timestamp.

        :param unit: magnitude of a second, e.g. minisecond: 1000
        :return: unix timestamp

        >>> Fdate('2018-04-07').to_timestamp()
        1523030400
        >>> Fdate('2018-04-07').to_timestamp(unit=1000)
        1523030400000
        """
        assert isinstance(unit, int) and unit > 0, 'unit must be positive integer!'
        return int(time.mktime(self._dt.timetuple())) * unit

    @property
    def year(self):
        return self._dt.year

    @property
    def month(self):
        return self._dt.month

    @property
    def day(self):
        return self._dt.day

    @property
    def week_day(self):
        return self._dt.weekday()

    @property
    def is_work_day(self):
        return True if 0 <= self.day <= 4 else False

    @property
    def is_weekend(self):
        return not self.is_work_day

    @property
    def is_leap_year(self):
        return _is_leap(self.year)

    @property
    def rank(self):
        """ Returns date rank over the whole year.

        >>> Fdate('2018-12-31').rank
        365
        """
        num = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
        extra = 1 if self.is_leap_year else 0
        return num[self.month-1] + self.day + extra

    def is_last_day(self, of='M'):
        """ Asserts whether it is the last day of the month or year.

        :param of: 'M' -- month, 'Y' -- Year

        >>> Fdate('2018-02-28').is_last_day()
        True
        >>> Fdate('2018-02-28').is_last_day(of='Y')
        False
        >>> Fdate('2018-12-31').is_last_day(of='Y')
        True
        """
        assert of in {'M', 'Y'},  "'of' must in {'M', 'Y'}!"
        fd = self + 1
        return True if fd.is_first_day(of) else False

    def is_first_day(self, of='M'):
        """ Asserts whether it is the first day of the month or year.

        :param of: 'M' -- month, 'Y' -- Year

        >>> Fdate('2018-02-01').is_first_day()
        True
        >>> Fdate('2018-02-01').is_first_day(of='Y')
        False
        >>> Fdate('2018-01-01').is_first_day(of='Y')
        True
        """
        assert of in {'M', 'Y'}, "'of' must in {'M', 'Y'}!"
        if of == 'M':
            return True if self.day == 1 else False
        elif of == 'Y':
            return True if self.day == 1 and self.month == 1 else False

    def count_days(self, of='M'):
        assert of in {'M', 'Y'}, "'of' must in {'M', 'Y'}!"
        if of == 'M':
            if self.month in {1, 3, 5, 7, 8, 10, 12}:
                return 31
            elif self.month in {4, 6, 9, 11}:
                return 30
            elif self.month == 2 and self.is_leap_year:
                return 29
            else:
                return 28
        elif of == 'Y':
            return 366 if self.is_leap_year else 365


def drange(start, end, step=1):
    """ Iterates from start to end (both included).
    """
    d1 = Fdate(start)
    d2 = Fdate(end)
    delta = (d2 - d1) // step
    sign = 1 if delta >= 0 else - 1
    for i in range(abs(delta) + 1):
        yield Fdate(d1 + sign * i * step)


def today(shift=0):
    day = datetime.date.today() + datetime.timedelta(days=shift)
    return Fdate(day.strftime('%Y-%m-%d'))


def _is_leap(year):
    if ((year % 4 == 0) and (year % 100 != 0)) or year % 400 == 0:
        return True
    return False


if __name__ == '__main__':
    doctest.testmod()

