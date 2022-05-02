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
from gc import disable as gc_disable
from gc import enable as gc_enable
from os import sep
from time import time

from adafruit_datetime import datetime, timedelta, tzinfo
from msgpack import unpack as msgpack_unpack


class timezone(tzinfo):
    # pylint: disable=invalid-name
    """
    Subclass of tzinfo for calculating the utc offset of a given datetime
    """

    """
    The datafile that timezones will be loaded from. Timezones are stored in the dict in the
    following format:
    {
        "<name>": {
            "<iso_date>": <offset from utc>
        }
    }

    Ex:
    {
        "America/Chicago": {
            "2022-01-01T00:00:00": -6.0,
            "2022-03-13T03:00:00": -5.0,
            "2022-11-06T02:00:00": -6.0,
            "2022-10-31T00:00:00": -5.0
        }
    }

    Meaning that:
    - On January 1st, the UTC offset in Chicago is -6
    - On March 13th, the UTC offset changes to -5
    - etc.

    """
    _TZ_DB_FILE = "_tzdb.msgpack"

    """
    The loaded _TZ_DB_FILE
    """
    _TZ_DB: dict = None

    def __init__(self, tz_name: str):
        """
        Create a new timezone with tz_name. The timezone contains the offset data for tz_name
        in the _TZ_DB.
        """
        self._tz_name = tz_name

        # Lazy-load on creation of first timezone instance
        if timezone._TZ_DB is None:
            db_file = sep.join([timezone._dirname(__file__), timezone._TZ_DB_FILE])
            timezone._TZ_DB = timezone._load_db(db_file)

        try:
            sorted_kv_pairs = sorted(
                timezone._TZ_DB[tz_name].items(),
                key=lambda kv_pair: datetime.fromisoformat(kv_pair[0]),
            )
            self._tz_data = OrderedDict(sorted_kv_pairs)
        except KeyError as key_error:
            raise KeyError(f"unknown timezone {tz_name}") from key_error

    @property
    def name(self):
        """
        The name of the timezone passed to the constructor
        """
        return self._tz_name

    def utcoffset(self, dt: "datetime") -> timedelta:
        """
        The offset from UTC in the given timezone at the given dt, as a
        timedelta object that is positive east of UTC.
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
        """
        # This is how you retrieve utc time on a pi pico rtc
        now_ts = time()
        now = datetime.fromtimestamp(now_ts)
        offset = self.utcoffset(now)
        return dt + offset

    def tzname(self, dt: "datetime") -> str:
        """
        Return the time zone name corresponding to the datetime object dt, as a string
        """
        if not isinstance(dt.tzinfo, self.__class__):
            raise ValueError(
                f"datetime.tzinfo is not an instance of {self.__class__.__name__}"
            )
        return dt.tzinfo.name

    @staticmethod
    def _load_db(file_path: str) -> dict:
        """
        Load the msgpack timezone database from the given file_path
        """
        gc_disable()
        try:
            with open(file_path, "rb") as f:
                data = msgpack_unpack(f)
        finally:
            gc_enable()

        return data

    @staticmethod
    def _dirname(file_path: str) -> str:
        """
        Retrieve the dirname of the given file_path
        """
        parts = file_path.split(sep)
        return sep.join(parts[:-1])
