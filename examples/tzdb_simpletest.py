#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2022 Evin Dunn
#
# SPDX-License-Identifier: Unlicense

from time import time

from adafruit_datetime import datetime
from tzdb import timezone


def main():
    # First use adafruit_ntp to fetch the current utc time & update the board's RTC

    utc_now = time()
    utc_now_dt = datetime.fromtimestamp(utc_now)

    tz_chicago = timezone("America/Chicago")
    chicago_now_dt = utc_now_dt + tz_chicago.utcoffset(utc_now_dt)

    print("UTC:     {}".format(utc_now_dt.ctime()))
    print("Chicago: {}".format(chicago_now_dt.ctime()))


if __name__ == "__main__":
    main()
