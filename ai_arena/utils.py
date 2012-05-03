import datetime


def get_current_date_time():
    now = datetime.datetime.now()
    tt = datetime.datetime.timetuple(now)
    return "%d-%d-%d %d:%d" % (tt.tm_year, tt.tm_mon, tt.tm_mday, tt.tm_hour, tt.tm_min)

def parse_logs(logs):
    """
        Helper function to prepare logs to display.

        If we would pass logs simply without parsing they would be unreadable, 
        e.g. new line chars would be ignored
    """
    return logs.split('\n')
