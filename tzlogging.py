from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler
from pytz import timezone, utc
from constants import TIMEZONE
import time

class Formatter(logging.Formatter):
    """override logging.Formatter to use an aware datetime object"""
    def converter(self, timestamp):
        dt = datetime.datetime.fromtimestamp(timestamp)
        tzinfo = timezone(TIMEZONE)
        return tzinfo.localize(dt)

    def formatTime(self, record, datefmt=None):
        dt = self.converter(record.created)
        if datefmt:
            s = dt.strftime(datefmt)
        else:
            try:
                s = dt.isoformat(timespec='milliseconds')
            except TypeError:
                s = dt.isoformat()
        return s

class TZLogger:
    def __init__(self, name, filename, level=logging.DEBUG):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        handler = RotatingFileHandler(filename,maxBytes=10000, backupCount=5)
        formatter = logging.Formatter('%(asctime)s [%(levelname)s]  %(message)s',datefmt='%d/%m/%Y %I:%M:%S %p')

        def customTime(*args):
            utc_dt = utc.localize(datetime.utcnow())
            my_tz = timezone(TIMEZONE)
            converted = utc_dt.astimezone(my_tz)
            return converted.timetuple()

        formatter.converter = customTime
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def getLogger(self):
        return self.logger

