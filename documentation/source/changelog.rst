ChangeLog
=========

V2.4
----

* A better cache system.
* A documentation in English, using `Sphinx <http://sphinx.pocoo.org/>`_.
* Add some metrics computation. One can compute maintainability, and therefore
  availability, for complex systems and voters.
* An Archlinux `package <https://aur.archlinux.org/packages/fiabilipy/>`_ is
  made.
* The code has been cleaned. (thank you `pylint <http://pylint.org/>`_ ;))
* Symbolic computation can be performed, using :mod:`sympy`


.. doctest::

  >>> from sympy import symbols
  >>> from fiabilipy import Component
  >>> l, t = symbols('l t', positive=True)
  >>> a = Component('a', lambda_=l)
  >>> a.reliability(t)
  exp(-l*t)


V2.3.1
------

* Update the module name from :mod:`fiabili` to :mod:`fiabilipy`.

V2.3
----

* Create a `pypi package <https://pypi.python.org/pypi/fiabilipy/>`_.
* Update the documentation.
* A Markov graph can be drawn.


V2.2
----

* Add a :mod:`markov` module.

V0.2
----

* Some metrics are cached to faster the computation (:abbr:`MTTF
  (Mean-Time-To-Failure)`, :abbr:`MTTR (Mean-Time-To-Repair)`, etc).
* A documentation is started (in French… sorry).

V0.1
----

* *Show time*.
* System, Component and voter can be built.
* Reliability can be computed.
* :abbr:`MTTF (Mean-Time-To-Failure)` can be computed.
* Compute the minimal cuts of order 1 and 2.
