Installing / Upgrading
======================
.. highlight:: bash

**fiabilipy** is in the `Python Package Index
<https://pypi.python.org/pypi/fiabilipy/>`_, so it should be quite easy to
install it. Multiple solutions are offered to you.

The main dependencies of fiabilipy are `numpy and scipy
<http://www.scipy.org/install.html>`_ and should be installed before.

Installing with pip
-------------------

To install fiabilipy::

    $ pip install fiabilipy

To get a specific version::

    $ pip install fiabilipy==2.2

To upgrade to the last version::

    $ pip install --upgrade fiabilipy


Installing on Archlinux
-----------------------

If you are using the `Archlinux <https://www.archlinux.org/>`_ GNU/Linux
distribution, an AUR package has been made. You can find it `here
<https://aur.archlinux.org/packages/fiabilipy/>`_. The major interest of using
this package, is that it gets upgraded whenever a new version is available and
you don’t have to manage dependencies.

Installing on Windows
---------------------

.. todo:: write few lines on the windows installation.


Installing from source
----------------------

If you would rather install directly from the source (to contribute, for
instance), check out for the latest source on our repository::

    $ hg clone https://chabotsi.no-ip.org/hg/utc/fiabilipy/
    $ cd fiabilipy
    $ python setup.py install

