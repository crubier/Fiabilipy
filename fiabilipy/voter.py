#!/usr/bin/env python
# -*- coding: utf-8 -*-

#Copyright (C) 2013 Chabot Simon, Sadaoui Akim

#This program is free software; you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation; either version 2 of the License, or
#(at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License along
#with this program; if not, write to the Free Software Foundation, Inc.,
#51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

r""" Voter design

This modude gives tools to design voters and compute some metrics, such as the
reliability, the availability, the Mean-Time-To-Failure, and so on.

"""
from builtins import range

from sympy import exp, Symbol, oo
from scipy.special import binom
from itertools import combinations, chain

from fiabilipy.component import Component

__all__ = ['Voter']

ALLSUBSETS = lambda n: (chain(*[combinations(list(range(n)), ni)
                        for ni in range(n+1)]))

class Voter(Component):
    r""" A voter with identical components having a constant failure rate

        This class is used to describe a voter. A voter M out-of N works if
        and only if *at least* M components out of the N avaible work.

        Attributes
        ----------
        component: `Component`
            the component to be replicated by the voter
        N: int
            the initial number of components
        M: int
            the minimal number of working components
        lambda_ : float
            the constant failure rate of the voter
        mu : float, optional
            the constant maintainability rate of the voter
        initialy_avaible: boolean, optional
            whether the component is avaible at t=0 or not

        Examples
        --------
        >>> motor = Component('M', 1e-4, 3e-2)
        >>> voter = Voter(motor, 2, 3)
        >>> voter.mttf
        8333.33333333333
    """

    def __init__(self, component, M, N, lambda_=0, mu=0, initialy_avaible=True):
        name = '{} out-of {} − {}'.format(M, N, component.name)
        super(Voter, self).__init__(name=name, lambda_=lambda_, mu=mu,
                                    initialy_avaible=initialy_avaible)
        self.component = component
        self.M = M
        self.N = N

    def __repr__(self):
        return u'Voter(%s out-of %s)' % (self.M, self.N)

    def _probabilitiescomputation(self, t, method):
        """ Compute the `method` (reliability, availability, maintainability) of
            a voter, given its components, and the initial number of components
            and the minimal number of components.
        """
        prob = 0
        for k in range(self.M, self.N+1):
            a = getattr(self.component, method)(t)**k
            b = (1 - getattr(self.component, method)(t))**(self.N-k)
            prob += binom(self.N, k) * a * b
        return prob

    def reliability(self, t):
        r""" Compute the reliability of the voter at `t`

            This method compute the reliability of the voter at `t`.

            Parameters
            ----------
            t : float or Symbol

            Returns
            -------
            out : float or symbolic expression
                The reliability calculated for the given `t`

            Examples
            --------
            >>> motor = Component('M', 1e-4, 3e-2)
            >>> voter = Voter(motor, 2, 3)
            >>> t = Symbol('t', positive=True)
            >>> voter.reliability(t)
            3.0*(-exp(-0.0001*t) + 1)*exp(-0.0002*t) + 1.0*exp(-0.0003*t)
            >>> voter.reliability(1000)
            0.974555817870510
        """
        ownrel = super(Voter, self).reliability(t)
        return ownrel * self._probabilitiescomputation(t, 'reliability')

    def maintainability(self, t):
        r""" Compute the maintainability of the voter at `t`

            This method compute the maintainability of the voter at `t`.

            Parameters
            ----------
            t : float or Symbol

            Returns
            -------
            out : float or symbolic expression
                The maintainability calculated for the given `t`

            Examples
            --------
            >>> motor = Component('M', 1e-4, 3e-2)
            >>> voter = Voter(motor, 2, 3, mu=1e-3)
            >>> t = Symbol('t', positive=True)
            >>> voter.maintainability(t) #doctest: +NORMALIZE_WHITESPACE
            (1.0*(-exp(-0.03*t) + 1.0)**3 + 3.0*(-exp(-0.03*t)
                + 1.0)**2*exp(-0.03*t))*(-exp(-0.001*t) + 1.0)
            >>> voter.maintainability(1000)
            0.632120558828558
        """
        ownrel = super(Voter, self).maintainability(t)
        return ownrel * self._probabilitiescomputation(t, 'maintainability')

    def availability(self, t):
        r""" Compute the availability of the voter at `t`

            This method compute the availability of the voter at `t`.

            Parameters
            ----------
            t : float or Symbol

            Returns
            -------
            out : float or symbolic expression
                The availability calculated for the given `t`

            Examples
            --------
            >>> motor = Component('M', 1e-4, 3e-2)
            >>> voter = Voter(motor, 2, 3, mu=1e-3)
            >>> t = Symbol('t', positive=True)
            >>> voter.availability(t) #doctest: +NORMALIZE_WHITESPACE
            3.0*(-0.00332225913621263*exp(-0.0301*t) +
            0.00332225913621265)*(0.00332225913621263*exp(-0.0301*t) +
            0.996677740863787)**2 + 1.0*(0.00332225913621263*exp(-0.0301*t) +
            0.996677740863787)**3
            >>> voter.availability(1000)
            0.999966961120940
        """
        ownavail = super(Voter, self).availability(t)
        return ownavail * self._probabilitiescomputation(t, 'availability')

    @property
    def mttf(self):
        r""" Compute the Mean-Time-To-Failure of the voter

            The MTTF is defined as :
                :math:`MTTF = \int_{0}^{\infty} R(t)dt`

            Returns
            -------
            out : float
                The component MTTF

            Examples
            --------
            >>> motor = Component('M', 1e-4, 3e-2)
            >>> voter = Voter(motor, 2, 3)
            >>> voter.mttf
            8333.33333333333
        """
        t = Symbol('t', positive=True)
        return self.reliability(t).integrate((t, 0, oo))

    @property
    def mttr(self):
        r""" Compute the Mean-Time-To-Repair of the voter

            The MTTR is defined as :
                :math:`MTTR = \int_{0}^{\infty} 1 - M(t)dt`

            Returns
            -------
            out : float
                The component MTTR

            Examples
            --------
            >>> motor = Component('M', 1e-4, 3e-2)
            >>> voter = Voter(motor, 2, 3, mu=1e-3)
            >>> voter.mttr
            1000.57547188695
        """
        t = Symbol('t', positive=True)
        return (1 - self.maintainability(t)).integrate((t, 0, oo))
