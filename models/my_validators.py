import datetime as dates
import time
from sqlhtml import FormWidget

# Chooses the time zone of the user.
# We also remember if the timezone is known, so that we will try to determine it if possible.
is_timezone_unknown = False
if auth.user is None:
    is_timezone_unknown = (session.user_timezone is None)
    user_timezone = session.user_timezone or 'UTC'
else:
    is_timezone_unknown = ((auth.user.user_timezone is None) and (session.user_timezone is None))
    user_timezone = auth.user.user_timezone or session.user_timezone or 'UTC'
    # If the timezone is known in the session, but not in the user profile, updates the user profile.
    if session.user_timezone is not None and auth.user.user_timezone is None:
        logger.info("Updating timezone in profile to %r" % session.user_timezone)
        db.auth_user[auth.user.id] = dict(user_timezone = session.user_timezone)
        auth.user.user_timezone = session.auth.user.user_timezone = user_timezone

# A UTC class.
class UTC(dates.tzinfo):
    """UTC"""
    ZERO = dates.timedelta(0)
    def utcoffset(self, dt):
        return UTC.ZERO
    def tzname(self, dt):
        return "UTC"
    def dst(self, dt):
        return UTC.ZERO
utc = UTC()

class IS_LOCALIZED_DATETIME:
    """
    example::

        INPUT(_type='text', _name='name', requires=IS_DATETIME())

    datetime has to be in the ISO8960 format YYYY-MM-DD hh:mm:ss
    """

    isodatetime = '%Y-%m-%d %H:%M:%S'

    @staticmethod
    def nice(format):
        code = (('%Y', '1963'),
                ('%y', '63'),
                ('%d', '28'),
                ('%m', '08'),
                ('%b', 'Aug'),
                ('%B', 'August'),
                ('%H', '14'),
                ('%I', '02'),
                ('%p', 'PM'),
                ('%M', '30'),
                ('%S', '59'))
        for (a, b) in code:
            format = format.replace(a, b)
        return dict(format=format)

    def __init__(self, format='%Y-%m-%d %H:%M:%S',
                 error_message='enter date and time formatted like: %(format)s',
                 timezone=None):
        """
        timezome must be None or a pytz.timezone("America/Chicago") object
        """
        self.format = T(format)
        self.error_message = str(error_message)
        self.extremes = {}
        self.timezone = timezone

    def __call__(self, value):
        ovalue = value
        if isinstance(value, dates.datetime):
            return (value, None)
        try:
            (y, m, d, hh, mm, ss, t0, t1, t2) = \
                time.strptime(value, str(self.format))
            value = dates.datetime(y, m, d, hh, mm, ss)
            if self.timezone is not None:
                value = self.timezone.localize(value).astimezone(utc)
            return (value, None)
        except Exception, e:
            logger.info("Entered incorrect date: %r entered: %r" % (e, ovalue))
            self.extremes.update(IS_LOCALIZED_DATETIME.nice(self.format))
            return (ovalue, T(self.error_message) % self.extremes)

    def formatter(self, value):
        if value is None or value == '':
            return None
        format = self.format
        year = value.year
        y = '%.4i' % year
        format = format.replace('%y', y[-2:])
        format = format.replace('%Y', y)
        if year < 1900:
            year = 2000
        d = dates.datetime(year, value.month, value.day,
                              value.hour, value.minute, value.second)
        if self.timezone is not None:
            d = d.replace(tzinfo=utc).astimezone(self.timezone)
        return d.strftime(format)


# Widget that causes markitup
def markitup_widget(field, value):
    return TEXTAREA(value,
                    _name=field.name,
                    _id="%s_%s" % (field._tablename, field.name),
                    _class='markitup',
                    requires=field.requires)
