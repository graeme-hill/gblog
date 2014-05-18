import gbgen, datetime

now = datetime.datetime.now()
d = gbgen.get_month_day_offset(now.month, now.year) + now.day
print(d)
