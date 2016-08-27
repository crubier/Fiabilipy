Tutorial
========

This tutorial is intended as an introduction to fiabilipy. You will learn to
build some components, to put them together and to compute some reliability
metrics. You will also learn how to use the markov representation.

Prerequisites
-------------

Before you start, be sure fiabilipy is well installed on your system. In the
python shell, the following import should run without raising an exception:

.. doctest::

    >>> import fiabilipy

If an exception is raised, check your :doc:`installation <../installation>`.


Topics
------

:doc:`system`
    This tutorial shows you how to build components and how to gather them to
    build a system. You also learn how to access to useful reliability metrics.

:doc:`markov`
    This tutorial shows you how to describe a system with a markov process.
    Then, it shows you how to compute the probability of being in a given state
    (such as *insufficient*, *damaged*, *nominal* and so on).

.. toctree::
    :hidden:

    system
    markov

