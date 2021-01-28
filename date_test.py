import datetime


def convert_time(time):
    strip = datetime.datetime.strptime(time, '%a, %d %b %Y %H:%M:%S +0900')
    converted = strip.strftime('%Y-%m-%d %H:%M:%S')
    return converted


date = date.today()
