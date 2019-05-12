"""
Given a list of classes and a start date (if the given date isn't a Monday,
confirm that with the user before continuing), produce a tab-delimited list of
(date, title) tuples, where the date increments the available days of the week,
repeating as needed until the final title has been used.

Given a list of dates on which class will not be held, skip those days while
scheduling, and resume with the next available day of class.

The output format is tab-delimited, with two tabs between each tuple.
I.e., yyyy/mm/d1\tTitle 1\t\tyyyy/mm/d2\tTitle 2\t\tyyyy/mm/d3\tTitle 3
                ^^       ^^^^          ^^       ^^^^          ^^
The extra tab makes my copy-pasting into the destination spreadsheet easier.
I suppose the output format could/should be configurable.

NB: I'm using some Python 2 syntax because the server I currently use this on
doesn't yet have Python 3, and I don't have 'pip install' permission.
"""

import calendar
import datetime
try:
  from loguru import logger
except:
  class logger(object):
    @staticmethod
    def debug(arg): pass

VALID_SCHEDULE_TYPES = ["mon-thu", "mon,wed", "tue,thu"]


# Class titles, in order
def get_classes():
  """
  @TODO: Make classes data-driven: database, ini file, input file, spreadsheet, whatever.
  Having hard-coded classes is just wrong.
  """
  return """
  Primer 1
  Primer 2
  Primer 3
  Primer 4
  Graphics 1
  Graphics 2
  HTML 1
  HTML 2
  CSS 1
  CSS 2
  CSS 3
  CSS 4
  Bootstrap 1
  Bootstrap 2
  JavaScript 1
  JavaScript 2
  JavaScript 3
  JavaScript 4
  JavaScript 5
  JavaScript 6
  JavaScript 7
  JavaScript 8
  MySQL 1
  MySQL 2
  PHP 1
  PHP 2
  PHP 3
  PHP 4
  Capstone 1
  PHP 5
  PHP 6
  Linux/Unix 1
  Linux/Unix 2
  Capstone 2
  Capstone 3
  Graduation
  """.strip().splitlines()


def next_available_date(start_date, schedule_type=None, unavailable_dates = None):
  """This returns a generator of dates, starting with the specified date, and continuing with the next available date."""
  """@TODO: When given a list of unavailable dates, skip them, and continue with the next available date."""
  one_day = datetime.timedelta(days=1)
  year, month, day = start_date
  doy = datetime.date(year, month, day)
  schedule_type = schedule_type.lower()
  if schedule_type == 'mon-thu':
    in_class_days = [calendar.MONDAY, calendar.TUESDAY, calendar.WEDNESDAY, calendar.THURSDAY]
  elif schedule_type == 'mon,wed':
    in_class_days = [calendar.MONDAY, calendar.WEDNESDAY]
  elif schedule_type == 'tue,thu':
    in_class_days = [calendar.TUESDAY, calendar.THURSDAY]
  else:
    raise ValueError("Valid schedule types are [%s]." % (', '.join(VALID_SCHEDULE_TYPES),))
  logger.debug('Unavailable dates: %s' % (unavailable_dates,))
  logger.debug('In-class days: %s' % (in_class_days,))
  while True:
    logger.debug('Available: %s (%d)' % (doy, doy.weekday()))
    yield doy
    doy = doy + one_day
    while doy.weekday() not in in_class_days or unavailable_dates and (doy.year, doy.month, doy.day) in unavailable_dates:
      logger.debug("Unavailable: %d/%d/%d" % (doy.year, doy.month, doy.day))
      doy = doy + one_day


def flexidate(value):
  """
  This function accept a date string in any of these formats:
    yyyy/mm/dd
    mm/dd/yyyy
    mm/dd
  The separator is any non-digit; i.e., it doesn't have to be a "/".
  The 2-part date assumes the current year for the yyyy value.
  It returns a tuple of (yyyy, mm, and dd) values as numbers (not strings), regardless of the input format.
  """
  # @TODO: Change the format parsing to match the user's locale. E.g., if in England, dd/mm[/yyyy] instead of mm/dd[/yyyy].
  import re
  if len(value) < 5:
    raise ValueError("Invalid date format. Acceptable forms are yyyy/mm/dd, mm/dd/yyyy and mm/dd.")
  m = re.match(r"(\d{4})\D(\d{2})\D(\d{2})", value)
  if m and m.group(3):
    return int(m.group(1)), int(m.group(2)), int(m.group(3))
  # I append the current year, so that a two-part date is converted to a 3-part date,
  # The regex ignores the possibly redundant separator and year.
  m = re.match(r"(\d{2})\D(\d{2})\D(\d{4})", '%s/%d' % (value, datetime.date.today().year))
  if m and m.group(3):
    return int(m.group(3)), int(m.group(1)), int(m.group(2))
  raise ValueError("Invalid date format. Acceptable forms are yyyy/mm/dd, mm/dd/yyyy and mm/dd.")


def main():
  import argparse
  import sys
  classes = get_classes()
  parser = argparse.ArgumentParser(prog=sys.argv[0])
  parser.add_argument("start_date", type=flexidate, help="""
    This is the day that %s is taught, and can be in any of
    these formats: yyyy/mm/dd, mm/dd/yyyy or mm/dd.
    The separator is any non-digit; i.e., it doesn't have to be a "/".
    The 2-part date assumes the current year for the yyyy value.
    """ % classes[0])
  parser.add_argument("schedule_type", metavar="schedule_type",
    choices=VALID_SCHEDULE_TYPES, type=str.lower, help="""
    The currently-supported schedule types are 'mon-thu' (a 4-times
    per week class), 'mon,wed' (a twice weekly class on Monday and Wednesday),
    or 'tue-thu' (a twice weekly class on Tuesday and Thursday).
    """)
  parser.add_argument("unavailable_dates", metavar="unavailable_dates",
  type=flexidate, nargs='*', help="""
    Any dates that shouldn't be scheduled, such as known holidays.
    You can supply any number of unavailable dates, using the same date
    formats as the start date.
    """)
  args = vars(parser.parse_args(sys.argv[1:]))
  schedule = list(zip(classes, next_available_date(args['start_date'], args['schedule_type'], args['unavailable_dates'])))
  # I'll use the old style of string interpolation until Python 3 is installed.
  tdf = '\t\t'.join(['%s-%s-%s\t%s' % (d.year, d.month, d.day, t) for t, d in schedule])
  print(tdf)


if __name__ == "__main__":
    main()
