Voters intersection
###################

The older the voters are, the less reliable they are. In their youngness, voters
are more reliable than single components. The goal of this example is to find
when a voter starts to be less reliable than a single component.


Step by step
------------

Let’s start with a simple 2/3 voters. It’s really easy to get its reliability.
First, we have to import the functions and classes we will use.

.. doctest::

    >>> from fiabilipy import Voter, Component
    >>> from sympy import Symbol

Let’s build the voter, with an unknown reliability :math:`\lambda`.

.. doctest::

    >>> l = Symbol('l', positive=True, null=False) #Lambda
    >>> t = Symbol('t', positive=True) #our time variable
    >>> comp = Component('C', l)
    >>> voter = Voter(comp, 2, 3)

Here is the voter, now let’s get its reliability.

.. doctest::

    >>> voter.reliability(t)
    3.0*(1 - exp(-l*t))*exp(-2*l*t) + 1.0*exp(-3*l*t)

To have a polynomial expression, we substitute :math:`\exp(-\lambda t)` to :math:`x`.
Once more, this is easy in python…

.. doctest::

    >>> from sympy import exp
    >>> x = Symbol('x')
    >>> voter.reliability(t).subs(exp(-l*t), x).nsimplify()
    x**3 + 3*x**2*(-x +1)

Using this notation, the reliability of a single component is :math:`x`. So to
find when the given voter is equivalent to the single component, we simply have
to solve :math:`x^3 + 3x^2(-x + 1) - x = 0`.

.. doctest::

    >>> from sympy import solve
    >>> crossing = (voter.reliability(t) - comp.reliability(t)).nsimplify()
    >>> solve(crossing.subs(exp(-l*t), x))
    [0, 1/2, 1]

And, the task is done.

The complete code
-----------------

The code below gives a generic function to solve this problem.

.. code:: python


    from fiabilipy import Voter, Component
    from sympy import Symbol, solve, exp

    def voterintersection(M, N):
        assert 1 < M < N, 'the given voter is not real'

        l = Symbol('l', positive=True, null=False)
        t = Symbol('t', positive=True)
        x = Symbol('x')

        comp = Component('C', l)
        voter = Voter(comp, M, N)

        crossing = (voter.reliability(t) - comp.reliability(t)).nsimplify()
        roots = solve(crossing.subs(exp(-l*t), x))

        return roots
