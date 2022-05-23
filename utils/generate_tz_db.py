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
from shutil import rmtree
from typing import Iterable
from zoneinfo import ZoneInfo, available_timezones


PROC_LOCK = Lock()

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


def serialize_timezone(out_dir: Path, tz_name: str):
    """
    Serializes the timezone with the given tz_name to a dictionary, where keys
    represent iso timestamps and values represent a change in utc offset at the
    timestamp. If the dict is empty, the timezone is equivalent to utc all
    year round.
    """
    with PROC_LOCK:
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
            raise ValueError("UTC offset is None for given utc_now, calendar, timezone")

        new_utc_offset = new_utc_offset.total_seconds() // 3600
        if abs(new_utc_offset - utc_offset) > 0.1:
            iso_ts = instant.replace(tzinfo=None).isoformat()
            utc_offset_dict[iso_ts] = new_utc_offset
            utc_offset = new_utc_offset

    if "/" in tz_name:
        path_parts = tz_name.split("/")
        lib_dir = Path("/".join(path_parts[:-1]))
        tz_file = path_parts[-1]
        lib_dir = out_dir / lib_dir
    else:
        lib_dir = out_dir
        tz_file = tz_name

    with PROC_LOCK:
        if not lib_dir.exists():
            lib_dir.mkdir()
            (lib_dir / "__init__.py").touch()

    tz_file = lib_dir / (tz_file + ".py")
    with open(tz_file, "w", encoding="utf-8") as tz_handle:
        tz_handle.write(f"tz_data = {utc_offset_dict}\n")

    with PROC_LOCK:
        print(f"{tz_name} complete")


# Grab the list of target timezone names
tznames = []
for tzname in sorted(available_timezones()):
    for target in TARGETS:
        if tzname.startswith(target):
            tznames.append(tzname)
            break

# Write the result to file
this_file = Path(__file__)
repo_root = this_file.parent.parent
out_pkg = repo_root / "tzdb" / "_zones"

if out_pkg.exists():
    rmtree(out_pkg)

out_pkg.mkdir()
(out_pkg / "__init__.py").touch()

# Serialize the target timezones
processes = []
with ProcessPoolExecutor() as pool:
    for tzname in tznames:
        proc = pool.submit(serialize_timezone, out_pkg, tzname)
        processes.append(proc)

# Check for errors
for proc in processes:
    proc.result()
