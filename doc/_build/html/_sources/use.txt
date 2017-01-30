====================
Using PyFT
====================

Running calibrate.py
--------------------

Before running target.py for the first time, run calibrate.py once.
This may be run by double-clicking on the calibrate.py icon or typing
at a prompt:

.. code-block:: bash

   python calibrate.py

The program will ask you to click two points separated by 3 inches on
your monitor. The edge of a common post-it note is 3 inches, and this
should be sufficiently precise to determine the monitor's pitch. See
the generated file ``dpi_calibration.txt`` to check if the value
is reasonable and/or equal to your expectation.

Running target.py
-----------------

As with calibrate.py, you may run target.py by double-clicking or by
running it at a command prompt.

On computers with multiple displays, check both displays to see where
the target is running. Pressing <Enter> will cycle through the displays.

Typing ? when the fullscreen target window is active (you can make it
active using any method that makes typical, non-fullscreen windows active,
such as Alt-Tab) displays a small help screen on the fixation target.
It shows how to use the keyboard to control the target. Typing ? again
makes the help screen disappear.

Please note that it is not always easy to tell whether a fullscreen OpenGL
program is active. It may be filling the screen, with no other windows visible,
and still not be the active window.

Pressing 'ESC' exits the program.
