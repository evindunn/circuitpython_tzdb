# SPDX-FileCopyrightText: Copyright (c) 2022 Evin Dunn
# SPDX-License-Identifier: MIT

"""
`tzdb.timezone`
================================================================================

IANA timezones for adafruit_datetime


* Author(s): Evin Dunn

Implementation Notes
--------------------

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://circuitpython.org/downloads

* Adafruit's Datetime library: https://github.com/adafruit/Adafruit_CircuitPython_DateTime
"""

from collections import OrderedDict
from time import time

from adafruit_datetime import datetime, timedelta, tzinfo


class timezone(tzinfo):
    # pylint: disable=invalid-name
    """
    Subclass of tzinfo for calculating the utc offset of a given datetime

    A python file is generated in _zones/ for each timezone in the following
    format::

        tz_data = {
            "2022-01-01T00:00:00": -6.0,
            "2022-03-13T03:00:00": -5.0,
            "2022-11-06T02:00:00": -6.0,
            "2022-10-31T00:00:00": -5.0
        }

    Meaning that:

    * On January 1st, the UTC offset is -6
    * On March 13th, the UTC offset changes to -5
    * etc.

    One of these files is lazily imported based on the tz_name passed to the
    constructor
    """

    def __init__(self, tz_name: str):
        """
        Create a new timezone with tz_name. The timezone contains the offset
        data for tz_name in the _TZ_DB.

        :param: tz_name The name of the IANA timezone to create
        :type tz_name: str
        """
        self._tz_name = tz_name

        # Lazy-load on creation of first timezone instance
        pkg = __import__(
            "_zones." + tz_name.replace("/", "."), globals(), locals(), ["tz_data"], 1
        )
        sorted_kv_pairs = sorted(
            pkg.tz_data.items(),
            key=lambda kv_pair: datetime.fromisoformat(kv_pair[0]),
        )
        self._tz_data = OrderedDict(sorted_kv_pairs)

    @property
    def name(self):
        """
        :return: The name of the timezone passed to the constructor
        :rtype: str
        """
        return self._tz_name

    def utcoffset(self, dt: "datetime") -> timedelta:
        """
        :param dt: The datetime to calculate the offset for
        :type dt: adafruit_datetime.datetime
        :return: The offset from UTC in the given timezone at the given dt, as a
            timedelta object that is positive east of UTC.
        :rtype: adafruit_datetime.timedelta
        """
        offset = timedelta(hours=0)
        for iso_ts, db_offset in self._tz_data.items():
            iso_dt = datetime.fromisoformat(iso_ts).replace(year=dt.year)
            if dt >= iso_dt:
                offset = timedelta(hours=db_offset)
        return offset

    def fromutc(self, dt: "datetime") -> "datetime":
        """
        datetime in UTC -> datetime in local time

        :param dt: The UTC datetime to convert to local time
        :type dt: adafruit_datetime.datetime
        :return: The UTC datetime dt in local time
        :rtype: adafruit_datetime.datetime
        """
        # This is how you retrieve utc time on a pi pico rtc
        now_ts = time()
        now = datetime.fromtimestamp(now_ts)
        offset = self.utcoffset(now)
        return dt + offset

    def tzname(self, dt: "datetime") -> str:
        """
        :param dt: The datetime to retrieve the timezone name for
        :type dt: adafruit_datetime.datetime
        :return: the time zone name corresponding to the datetime object dt, as a string
        :rtype: str
        """
        if not isinstance(dt.tzinfo, self.__class__):
            raise ValueError(
                f"datetime.tzinfo is not an instance of {self.__class__.__name__}"
            )
        return dt.tzinfo.name
