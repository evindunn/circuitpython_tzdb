Introduction
============


.. image:: https://readthedocs.org/projects/circuitpython-tzdb/badge/?version=latest
    :target: https://circuitpython-tzdb.readthedocs.io/
    :alt: Documentation Status



.. image:: https://img.shields.io/discord/327254708534116352.svg
    :target: https://adafru.it/discord
    :alt: Discord


.. image:: https://github.com/evindunn/CircuitPython_tzdb/workflows/Build%20CI/badge.svg
    :target: https://github.com/evindunn/CircuitPython_tzdb/actions
    :alt: Build Status


.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black
    :alt: Code Style: Black

IANA timezones for adafruit_datetime

Build
=====

To regenerate the timezone database files in `tzdb/_zones <./tzdb/_zones>`_

#. Create a python>=3.9 environment: ``python3.9 -m venv .venv``
#. Activate the environment: ``source .venv/bin/activate``
#. Install dependencies: ``pip install -r requirements.txt``
#. And run the ``utils/generate_tz_db.py`` script: ``./utils/generate_tz_db.py``

This creates a python file in `_zones <./tzdb/_zones>`_ for each timezone.
These files each contain a dictionary that maps names to utc offsets throughout
the year using python3.9's `ZoneInfo <https://docs.python.org/3/library/zoneinfo.html>`_

This file is included in this repository/package and is current as of 2022-05-22

See `tzdb/_timezone.py <./tzdb/_timezone.py>`_ for details on how it's used


Dependencies
=============
This driver depends on:

* `Adafruit CircuitPython <https://github.com/adafruit/circuitpython>`_

Please ensure all dependencies are available on the CircuitPython filesystem.
This is easily achieved by downloading
`the Adafruit library and driver bundle <https://circuitpython.org/libraries>`_
or individual libraries can be installed using
`circup <https://github.com/adafruit/circup>`_.

Installing from PyPI
=====================
On supported GNU/Linux systems like the Raspberry Pi, you can install the driver locally `from
PyPI <https://pypi.org/project/circuitpython-tzdb/>`_.
To install for current user:

.. code-block:: shell

    pip3 install circuitpython-tzdb

To install system-wide (this may be required in some cases):

.. code-block:: shell

    sudo pip3 install circuitpython-tzdb

To install in a virtual environment in your current project:

.. code-block:: shell

    mkdir project-name && cd project-name
    python3 -m venv .env
    source .env/bin/activate
    pip3 install circuitpython-tzdb



Installing to a Connected CircuitPython Device with Circup
==========================================================

Make sure that you have ``circup`` installed in your Python environment.
Install it with the following command if necessary:

.. code-block:: shell

    pip3 install circup

With ``circup`` installed and your CircuitPython device connected use the
following command to install:

.. code-block:: shell

    circup install tzdb

Or the following command to update an existing version:

.. code-block:: shell

    circup update

Usage Example
=============

.. code-block:: python3

    #!/usr/bin/env python3
    # SPDX-FileCopyrightText: Copyright (c) 2022 Evin Dunn
    # SPDX-License-Identifier: MIT

    from time import time

    from adafruit_datetime import datetime

    try:
        from tzdb import timezone
    except ImportError:
        from sys import path as sys_path
        from pathlib import Path

        sys_path.insert(0, str(Path(__file__).parent.parent))
        from tzdb import timezone


    def main():
        TARGETS = [
            "America/Chicago",
            "America/Argentina/Buenos_Aires",
            "Pacific/Guam",
            "Asia/Tokyo",
        ]

        # First use adafruit_ntp to fetch the current utc time & update the board's
        # RTC

        utc_now = time()
        utc_now_dt = datetime.fromtimestamp(utc_now)

        print("UTC: {}".format(utc_now_dt.ctime()))

        for target in TARGETS:
            localtime = utc_now_dt + timezone(target).utcoffset(utc_now_dt)
            print("{}: {}".format(target, localtime.ctime()))


    if __name__ == "__main__":
        main()


Documentation
=============
API documentation for this library can be found on `Read the Docs <https://circuitpython-tzdb.readthedocs.io/>`_.

For information on building library documentation, please check out
`this guide <https://learn.adafruit.com/creating-and-sharing-a-circuitpython-library/sharing-our-docs-on-readthedocs#sphinx-5-1>`_.

Contributing
============

Contributions are welcome! Please read our `Code of Conduct
<https://github.com/evindunn/CircuitPython_tzdb/blob/HEAD/CODE_OF_CONDUCT.md>`_
before contributing to help this project stay welcoming.
