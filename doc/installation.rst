====================
Installation of PyFT
====================

Installing Python and other packages
------------------------------------

Installation of PyFT consists largely of installing Python and Pyglet.
Exact version numbers are provided below, and should be used when
possible. Version numbers in Python have the format M.m.R (for Major,
minor, and Release, respectively). Slight differences between the
versions listed below and your installed versions are unlikely to
prevent PyFT from working.


Prerequisite Installation in Windows
------------------------------------

Download and install the packages listed below:

    1. `Python 2.7.3
    <http://www.python.org/ftp/python/2.7.3/python-2.7.3.msi>`_
    
    2. `Pyglet 1.1.4
    <http://pyglet.googlecode.com/files/pyglet-1.1.4.msi>`_


By default, Python will be installed in ``C:\Python27``. This must be
appended to the PATH environment variable before proceeding.


Prerequeisite Installation in OS X
----------------------------------

Download and install the packages listed below. Python generally comes
bundled with OS X, and it may be sufficient to use the version already
installed. If you'd like to try that, skip 1 below and just install
Pyglet.

    1. `Python 2.7.5
    <http://www.python.org/ftp/python/2.7.5/python-2.7.5-macosx10.6.dmg>`_

    2. `Pyglet 1.1.4
    <http://pyglet.googlecode.com/files/pyglet-1.1.4.dmg>`_
    
The environment variable PATH may need to be modified accordingly.

Installing PyFT
---------------

Installation consists of unzipping PyFT.zip into any directory. Unzipping
creates a directory called PyFT, in which the following files reside:

    * ``target.py``: The main program. This will be launched whenever the
      fixation target is to be used.
      
    * ``calibrate.py``: This program is run once after installing (or whenever
      the computer's monitor is changed) in order to measure the monitor's
      pitch (DPI).
      
    * ``config.py``: This file contains all of the configurable parameters
      for the fixation target. Please see the comments in the file for details.

    * ``docs``: This folder contains documentation source in ReST / Sphinx.
      Compiled documentation can be found in the ``docs/_build`` directory.
      
    * ``logs``: If this folder does not exist, it will be created upon first
      running target.py. It logs the locations of fixation, with timestamps,
      each time the program is used.
      
    * ``dpi_calibration.txt``: This file is generated upon running ``calibrate.py``
      and contains the monitor pitch in DPI. It may be manually created and
      entered as an alternative.
      
    * ``edit_config.bat``: This is a DOS script that can be used to launch an
      editor to edit the configuration file. Notepad++ is the default command
      but this can be changed in the script if desired.
