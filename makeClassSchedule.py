"""
Given a list of classes and a start date, produce a tab-delimited list of
(date, title) tuples, where the date are among the available days of the week,
repeating as needed until the last title has been used.

Given a list of dates on which classes will not be held, skip those days while
scheduling, and resume with the next available day of class.

The output format is tab-delimited, with two tabs between each tuple.
I.e., yyyy/mm/d1\tTitle 1\t\tyyyy/mm/d2\tTitle 2\t\tyyyy/mm/d3\tTitle 3
                ^^       ^^^^          ^^       ^^^^          ^^
The extra tab makes my copy-pasting into the destination spreadsheet easier.
The output format might be configurable in the future.

NB: I'm using some Python 2 syntax because the server I currently use this on
doesn't yet have Python 3, and I don't have 'pip install' permission.
"""

import argparse
import calendar
import datetime
try:
  from loguru import logger
except:
  class logger(object):
    @staticmethod
    def debug(arg): pass

WEEKDAY_ABBREVS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]


# Used in argument parsing to confirm the class file exists.
def class_file(s):
  import os
  if not os.path.exists(s):
    raise argparse.ArgumentTypeError("File not found: %s" % s)
  return s


# The class file is expected to be class names, listed one per line.
# This function removes leading and trailing whitespace,
# and ignores lines that start with a semicolon or open bracket.
# Blank lines are also ignored.
def read_classes(s):
  with open(s) as f:
    return [
      i.strip()
      for i in f.readlines()
      if not i.strip()[:1] in [';', '[', '']
    ]


def next_available_date(start_date, class_days=None, unavailable_dates=None):
  """This returns a generator of dates, starting with the specified date, and continuing with the next available date."""
  one_day = datetime.timedelta(days=1)
  year, month, day = start_date
  doy = datetime.date(year, month, day)
  logger.debug('Class days: %s' % (class_days,))
  logger.debug('Unavailable dates: %s' % (unavailable_dates,))
  while True:
    logger.debug('Available: %s (%d)' % (doy, doy.weekday()))
    yield doy
    doy += one_day
    while doy.weekday() not in class_days or unavailable_dates and (doy.year, doy.month, doy.day) in unavailable_dates:
      logger.debug("Unavailable: %d/%d/%d" % (doy.year, doy.month, doy.day))
      doy += one_day


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
  if len(value) < 3:
    raise ValueError("Invalid date format. Acceptable forms are yyyy/mm/dd, mm/dd/yyyy and mm/dd.")
  m = re.match(r"(\d{4})\D(\d{1,2})\D(\d{1,2})", value)
  if m and m.group(3):
    return int(m.group(1)), int(m.group(2)), int(m.group(3))
  # I append the current year, so that a two-part date is converted to a 3-part date,
  # The regex ignores the possibly redundant separator and year.
  m = re.match(r"(\d{1,2})\D(\d{1,2})\D(\d{4})", '%s/%d' % (value, datetime.date.today().year))
  if m and m.group(3):
    return int(m.group(3)), int(m.group(1)), int(m.group(2))
  raise ValueError("Invalid date format. Acceptable forms are yyyy/mm/dd, mm/dd/yyyy and mm/dd.")


def weekday_abbrev(s):
  s = s.lower().split(',')
  class_days = []
  for i in set(s):
    if i == 'mon': class_days.append(calendar.MONDAY)
    elif i == 'tue': class_days.append(calendar.TUESDAY)
    elif i == 'wed': class_days.append(calendar.WEDNESDAY)
    elif i == 'thu': class_days.append(calendar.THURSDAY)
    elif i == 'fri': class_days.append(calendar.FRIDAY)
    elif i == 'sat': class_days.append(calendar.SATURDAY)
    elif i == 'sun': class_days.append(calendar.SUNDAY)
    else:
      raise argparse.ArgumentTypeError("Valid days are [%s]." % (', '.join(WEEKDAY_ABBREVS),))
  return class_days


def main():
  import sys
  parser = argparse.ArgumentParser(prog=sys.argv[0])
  parser.add_argument("class_file", type=class_file, help="""
    Specify a file that includes the class names, listed one per line.
    """)
  parser.add_argument("start_date", type=flexidate, help="""
    This is the day that %s is taught, and can be in any of
    these formats: yyyy/mm/dd, mm/dd/yyyy or mm/dd.
    The separator is any non-digit; i.e., it doesn't have to be a "/".
    The 2-part date assumes the current year for the yyyy value.
    """ % ("the first class",))
  parser.add_argument("class_days", metavar="class_days",
    type=weekday_abbrev, action="append", help="""
    Valid weekday names are %s. Separate names by commas (no spaces or dashes).
    Duplicates are ignored. Order doesn't matter. E.g., mon,tue,wed
    """ % str(WEEKDAY_ABBREVS))
  parser.add_argument("unavailable_dates", metavar="unavailable_dates",
  type=flexidate, nargs='*', help="""
    Any dates that shouldn't be scheduled, such as known holidays.
    You can supply any number of unavailable dates, using the same date
    formats as the start date.
    """)
  args = vars(parser.parse_args(sys.argv[1:]))
  classes = read_classes(args['class_file'])
  schedule = list(zip(classes, next_available_date(args['start_date'], args['class_days'][0], args['unavailable_dates'])))
  # I'll use the old % style of string interpolation until Python 3 is installed.
  tdf = '\t\t'.join(['%04d/%02d/%02d\t%s' % (d.year, d.month, d.day, t) for t, d in schedule])
  print(tdf)


if __name__ == "__main__":
    main()
