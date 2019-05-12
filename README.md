# class-scheduler
First round of a Python program that produces a
schedule for a class that repeats on certain
days of the week. The inputs are:

1. The names of the classes,
2. The start date,
3. The available days of the week,
4. Any unavailable dates, such as holidays (optional).

In this first round, the classes are in the code (blech!),
and the available days are limited to 3 options: mon-thu; mon,wed;
and tue,thu.

Future versions will:
1. Support external class names, probably file-based.
2. Parse the available days to allow more than just 3 types.
3. Support external unavailable days, or default holidays.
