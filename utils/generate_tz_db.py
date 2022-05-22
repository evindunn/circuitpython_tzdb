#!/usr/bin/env python3.9

# SPDX-FileCopyrightText: Copyright (c) 2022 Evin Dunn
# SPDX-License-Identifier: MIT

"""
This script uses python>=3.9's ZoneInfo to generate a msgpack-encoded timezone 
dict with the following format:
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

Only IANA canonical timezones are included to keep the size of the database 
small
"""

from calendar import Calendar
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, tzinfo
from multiprocessing import Lock
from pathlib import Path
from typing import Iterable, Tuple
from zoneinfo import ZoneInfo, available_timezones

from msgpack import pack as msgpack_pack

LOG_LOCK = Lock()

# Target canonical timezones only to keep the output small
TARGETS = [
    "Africa",
    "America",
    "Asia",
    "Atlantic",
    "Australia",
    "Canada",
    "Europe",
    "Indian",
    "Pacific",
    "UTC",
]


def iteryear(
    utc_now: datetime, calendar: Calendar, tz_info: tzinfo
) -> Iterable[datetime]:
    """
    Iterates over every minute of every day for the year in utc_now
    """
    epoch = datetime.min
    for month_idx in range(1, 13):
        for date in calendar.itermonthdates(utc_now.year, month_idx):
            date_time = datetime.combine(date, epoch.time(), tzinfo=tz_info)
            for hour in range(0, 24):
                for minute in range(0, 60):
                    yield date_time.replace(hour=hour, minute=minute)


def serialize_timezone(tz_name: str) -> Tuple[str, dict]:
    """
    Serializes the timezone with the given tz_name to a dictionary, where keys
    represent iso timestamps and values represent a change in utc offset at the 
    timestamp. If the dict is empty, the timezone is equivalent to utc all 
    year round.
    """
    with LOG_LOCK:
        print(f"Serializing {tz_name}...")

    utc_now = datetime.now(tz=ZoneInfo("UTC"))
    calendar = Calendar()

    timezone = ZoneInfo.no_cache(tz_name)
    jan_1 = datetime(year=utc_now.year, month=1, day=1, tzinfo=timezone)
    utc_offset = jan_1.utcoffset()

    if utc_offset is None:
        raise ValueError("UTC offset is None for given tzinfo")

    utc_offset = utc_offset.total_seconds() // 3600
    utc_offset_dict = {jan_1.replace(tzinfo=None).isoformat(): utc_offset}

    for instant in iteryear(utc_now, calendar, timezone):
        new_utc_offset = instant.utcoffset()
        if new_utc_offset is None:
            raise ValueError(
                "UTC offset is None for given utc_now, calendar, timezone"
            )

        new_utc_offset = new_utc_offset.total_seconds() // 3600
        if abs(new_utc_offset - utc_offset) > 0.1:
            iso_ts = instant.replace(tzinfo=None).isoformat()
            utc_offset_dict[iso_ts] = new_utc_offset
            utc_offset = new_utc_offset

    with LOG_LOCK:
        print(f"{tz_name} complete")

    return tz_name, utc_offset_dict


# Grab the list of target timezone names
tznames = []
for tzname in sorted(available_timezones()):
    for target in TARGETS:
        if tzname.startswith(target):
            tznames.append(tzname)
            break

# Serialize the target timezones
processes = []
with ProcessPoolExecutor() as pool:
    for tzname in tznames:
        proc = pool.submit(serialize_timezone, tzname)
        processes.append(proc)

# Combine the target timezones into a dict, where key is the timezone name
# and value is the dict returned by serialize_timezone()
timezones = {}
for proc in processes:
    tzname, offset_lst = proc.result()
    timezones[tzname] = offset_lst

# Write the result to file
this_file = Path(__file__)
repo_root = this_file.parent.parent
out_file = repo_root / "tzdb" / "_tzdb.msgpack"
with open(out_file, "wb") as msgpack_file:
    # json_dump(timezones, f, indent=2)
    msgpack_pack(timezones, msgpack_file, use_single_float=True)
