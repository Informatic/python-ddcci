python-ddcci
============

Control DDC/CI-capable display using `python-smbus`.

Small POC evolved into a full-blown interface now! Code is pretty much
self-explanatory, especially in conjunction with example included in libraries
`main`.

`qddccigui.py` is an example app, a PyQt4-based brightness/contrast controller.
Bus ID can be provider as the first (and only) commandline argument, bus 8 is
chosen otherwise. (Most probably because my primary display is accessible on
that one, but not really sure ;)) Icons used in this example are courtesy of
(Glyphish)[http://www.glyphish.com/].

You may also find `ddccontrol-db` and `ddccontrol -p` helpful when looking for
control addresses.
