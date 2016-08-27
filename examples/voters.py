#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import (unicode_literals, absolute_import, division,
                        print_function)

from fiabilipy import Voter, Component
from sympy import Symbol, solve, exp

def voter_example(nmax=5, nmin=3):
    """
        find when a real voter M/N is equivalent to a single component.
        all real voters (i.e. 1 < M < N) having `nmin <= N < nmax` are studied.

        Parameters
        ----------
        nmax: int, optional
            the maximum value of N (excluded)

        nmin: int, optional
            the minimum value of N (included)

    """
    orders = ((M, N) for N in xrange(nmin, nmax) for M in xrange(2, N))
    l = Symbol('l', positive=True, null=False)
    t = Symbol('t', positive=True)
    x = Symbol('x')
    comp = Component('C', l)

    for order in orders:
        voter = Voter(comp, order[0], order[1])
        crossing = (voter.reliability(t) - comp.reliability(t)).nsimplify()
        roots = solve(crossing.subs(exp(-l*t), x))

        print('For M = {}, N = {}'.format(*order))
        print('− {} roots: '.format(len(roots)))
        for root in roots:
            print(' − {}'.format(root))
        print()

if __name__ == '__main__':
    voter_example(nmax=6)
