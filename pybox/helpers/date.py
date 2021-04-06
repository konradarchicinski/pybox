#!/usr/bin/env python
from dateutil import tz
from dateutil.parser import parse
from datetime import datetime, date, timedelta


def to_date(date_input):
    """Return date object created from supplied input.

    Args:
        date_input (str, date-like): value to be transformed.
    """
    if date_input is None:
        return None
    elif isinstance(date_input, datetime):
        return date_input.date()
    else:
        return parse(date_input, default=date.min)


def to_datetime(date_input):
    """Return datetime object created from supplied input.

    Args:
        date_input (str, date-like): value to be transformed.
    """
    if date_input is None:
        return None
    elif isinstance(date_input, date):
        return to_local_time_zone(
            datetime.combine(date_input, datetime.min.time()))
    else:
        return to_local_time_zone(parse(date_input))


def to_local_time_zone(date_input):
    """Returns datetime object transformed to the local time zone.

    Args:
        date_input (datetime): value to be transformed.
    """
    if date_input.tzinfo is None:
        return date_input
    else:
        return date_input.astimezone(tz.tzlocal()).replace(tzinfo=None)


def create_dates_list(ending_date, starting_date):
    """Return list of date objects between provided dates with one day difference.

    Args:
        ending_date (date-like): last date in the list.
        starting_date (date-like): first date in the list.
    """
    # TODO create something more universal, not only for days.
    return [
        ending_date - timedelta(days=i)
        for i in range((ending_date - starting_date).days + 1)
    ]
