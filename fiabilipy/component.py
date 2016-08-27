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

r""" Component design module

This modude gives tools to design basic components and compute some metrics,
such as the reliability, the availability, the Mean-Time-To-Failure, and so on.

"""
from __future__ import division
from builtins import object
from past.utils import old_div

from sympy import exp, Symbol, oo

__all__ = ['Component']

class Component(object):
    r""" Describe a component with a constant failure rate.

        This class is used to create all the components of a system.

        Attributes
        ----------
        name : str
            the name of the component. (It has to be a unique name for the whole
            system)
        lambda_ : float
            the constant failure rate of the component
        mu : float, optional
            the constant maintainability rate of the component
        initialy_avaible : boolean, optional
            whether the component is avaible at t=0 or not

        Examples
        --------
        >>> motor = Component('M', 1e-4, 3e-2)
        >>> motor.lambda_
        0.0001
    """

    def __init__(self, name, lambda_, mu=0, initialy_avaible=True):
        self.__dict__["_systems"] = set()
        self.lambda_ = lambda_
        self.mu = mu
        self.name = name
        self.initialy_avaible = initialy_avaible

    def __lt__(self,other):
        if(isinstance(other, str)):
            return self.name < other
        else:
            return self.name < other.name

    def __setattr__(self, name, value):
        for system in self._systems:
            system._cache = {}
        self.__dict__[name] = value

    def __repr__(self):
        return u'Component(%s)' % self.name

    def __str__(self):
        return self.name

    def reliability(self, t):
        r""" Compute the reliability of the component at `t`

            This method compute the reliability of the component at `t`.

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
            >>> t = Symbol('t', positive=True)
            >>> motor.reliability(t)
            exp(-0.0001*t)
            >>> motor.reliability(1000)
            0.904837418035960
        """
        return exp(-self.lambda_ * t)

    def maintainability(self, t):
        r""" Compute the maintainability of the component at `t`

            This method compute the maintainability of the component at `t`.

            Parameters
            ----------
            t : int or Symbol

            Returns
            -------
            out : float or symbolic expression
                The maintainability calculated for the given `t`

            Examples
            --------
            >>> motor = Component('M', 1e-4, 3e-2)
            >>> t = Symbol('t', positive=True)
            >>> motor.maintainability(t)
            -exp(-0.03*t) + 1.0
            >>> motor.maintainability(1000)
            0.999999999999906
        """
        return 1.0 - exp(-self.mu * t)

    def availability(self, t):
        r""" Compute the availability of the component at `t`

            This method compute the availability of the component at `t`.

            Parameters
            ----------
            t : int or Symbol

            Returns
            -------
            out : float or symbolic expression
                The availability calculated for the given `t`

            Examples
            --------
            >>> motor = Component('M', 1e-4, 3e-2)
            >>> t = Symbol('t', positive=True)
            >>> motor.availability(t)
            0.00332225913621263*exp(-0.0301*t) + 0.996677740863787
            >>> motor.availability(1000)
            0.996677740863788
        """
        if self.mu == self.lambda_ == 0:
            return 1
        a = old_div(self.mu, (self.mu + self.lambda_))
        if self.initialy_avaible:
            b = old_div(self.lambda_, (self.mu + self.lambda_))
        else:
            b = old_div(- self.mu, (self.mu + self.lambda_))

        return a + b*exp(-(self.lambda_ + self.mu) * t)

    @property
    def mttf(self):
        r""" Compute the Mean-Time-To-Failure of the component

            The MTTF is defined as :
                :math:`MTTF = \int_{0}^{\infty} R(t)dt = \frac{1}{\lambda}`

            when the failure rate (:math:`\lambda` is constant)

            Returns
            -------
            out : float
                The component MTTF

            Examples
            --------
            >>> motor = Component('M', 1e-4, 3e-2)
            >>> motor.mttf
            10000.0
        """
        return old_div(1.0,self.lambda_)

    @property
    def mttr(self):
        r""" Compute the Mean-Time-To-Repair of the component

            The MTTR is defined as :
                :math:`MTTR = \int_{0}^{\infty} 1 - M(t)dt = \frac{1}{\mu}`

            when the failure rate (:math:`\mu` is constant)

            Returns
            -------
            out : float
                The component MTTR

            Examples
            --------
            >>> motor = Component('M', 1e-4, 3e-2)
            >>> motor.mttr
            33.333333333333336
        """
        return old_div(1.0,self.mu)
