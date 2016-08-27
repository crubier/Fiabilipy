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

from __future__ import print_function
from builtins import range
from builtins import object

from numpy import zeros, binary_repr, where, array
from scipy.linalg import expm

__all__ = ['Markovprocess']

class Markovprocess(object):
    """ Initialize the markov process management of the system.

        Parameters
        ----------
        components : list
            the is the list of the components to manage
        initstates : dict or list
            describes the initial state of the process, giving the initial
            probabilities of being in each situation

        Examples
        --------
        Let S be a system of two components A and B.

        >>> from fiabilipy import Component
        >>> A, B = Component('A', 1e-2), Component('B', 1e-6)
        >>> comp = (A, B)
        >>> init = [0.8, 0.1, 0.1, 0]
        >>> process = Markovprocess(comp, init)

        * `init[0]` is the probability of having A and B working
        * `init[1]` is the probability of having A working and not B
        * `init[2]` is the probability of having B working and not A
        * `init[3]` is the probability of having neither A nor B working

        In a general way `init[i]` is the probability of having::

        >>> for c, state in enumerate(binary_repr(i, len(components))):
        >>>     if state:
        >>>         print('%s working' % components[c])
        >>>     else:
        >>>         print('%s not working' % components[c])

        As `initstates` may be very sparse, it can be given through a
        dictionnary as follow::

        >>> init = {}
        >>> init[0] = 0.8
        >>> init[1] = init[2] = 0.1
    """

    def __init__(self, components, initstates):
        self.components = tuple(components) #assert order won’t change
        self.matrix = None
        if isinstance(initstates, dict):
            N = len(self.components)
            self.initstates = array([initstates.get(x, 0)
                                     for x in range(2**N)])
        else:
            self.initstates = array(initstates)
        self._initmatrix()
        self._states = {}

    def _initmatrix(self):
        r""" Given a list of components, this function initialize the markov
            matrix.
        """
        N = len(self.components)
        #2^N different states
        #Let’s build the 2^(2N) matrix…
        self.matrix = zeros((2**N, 2**N))

        for i in range(2**N):
            currentstate = array([int(x) for x in binary_repr(i, N)])
            for j in range(i+1, 2**N):
                newstate = array([int(x) for x in binary_repr(j, N)])
                tocheck = where(newstate != currentstate) #Components changed
                if len(tocheck[0]) > 1: #Impossible to reach
                    continue

                component = self.components[tocheck[0][0]]#The changed component
                self.matrix[i, j] = component.lambda_
                self.matrix[j, i] = component.mu

        rowsum = self.matrix.sum(axis=1)
        self.matrix[range(2**N), range(2**N)] = -rowsum

    def _computestates(self, func):
        r""" Compute the states described by a function

            Parameters
            ----------
            func: function
                a function defining if a state is tracked or not

            Returns
            -------
            out: list
                the list of states actually tracked by `func`

            Examples
            --------
            >>> A, B, C, D = [Component(i, 1e-3) for i in xrange(4)]
            >>> comp = (A, B, C, D)
            >>> process = Markovprocess(comp, {0:1})
            >>> availablefunc = lambda x: (x[0] or x[1]) and (x[2] or x[3])
            >>> availablestates = process.computestates(states)

            This defines, for instance, the following parallel-series system::

                     | -- A -- |    | -- C -- |
                E -- |         | -- |         | -- S
                     | -- B -- |    | -- D -- |

            * `availablefunc` is the function describing when the system is
              available.
            * `availablestates` is the actual states when the system is
              available. The result is used by the :py:meth:`value` method.
        """

        N = len(self.components)
        nsquared = 2**N
        states = []
        for x in range(nsquared):
            s = [int(i) for i in binary_repr(nsquared - 1 - x, N)]
            if func(s):
                states.append(x)
        return states

    def value(self, t, statefunc=None):
        r""" Compute the probability of being in some states.

            Parameters
            ----------
            t : float
                when the probability must be computed
            state : function
                a function defining the state you want to know the probability

            Examples
            --------
            >>> A, B, C, D = [Component(i, 1e-3) for i in xrange(4)]
            >>> comp = (A, B, C, D)
            >>> process = Markovprocess(comp, {0:1})
            >>> availablefunc = lambda x: (x[0] or x[1]) and (x[2] or x[3])
            >>> process.value(100, statefunc=availablefunc)
            0.98197017562069511

            So, at :math:`t = 100`, the probability for the system to be
            available is approximaltly 0.982.

            If you want to know, the probability, at :math:`t = 1000` that all
            the components work but the first one, you proceed like that

            >>> allbutfirstfunc = lambda x: not x[0] and x[1] and x[2] and x[3]
            >>> allbutfirststates = process.computestates(allbutfirstfunc)
            >>> process.value(1000, states=allbutfirststates)
            0.031471429479129759
        """
        v = self.initstates.dot(expm(t*self.matrix))
        if not statefunc:
            return v
        else:
            try:
                states = self._states[statefunc]
            except KeyError:
                states = self._computestates(statefunc)
                self._states[statefunc] = states

            return v[(states, )].sum()

    def draw(self, output=None):
        r""" Print the content of the dot file needed to draw the markov process

            Parameters
            ----------
            output : file-like object, optional
                If `output` is given, then the content is written into this
                file. `output` *must* have a :py:meth:`write` method.

            Notes
            -----
            Please, see the `Graphviz <http://graphviz.org/>`_ website to have
            more information about how to transform the ouput code into a nice
            picture.
        """
        def binstr(x, N):
            """ Convert `x` to its binary reprensation over N bits

                >>> bin(2, 4)
                '0010'
            """
            return ''.join([i for i in binary_repr(x, N)])

        N = len(self.components)
        nsquared = 2**N
        data = ['digraph G {', '\trankdir=LR;']
        for i in range(nsquared):
            bini = binstr(nsquared - 1 - i, N)
            for j in range(i, nsquared):
                if not self.matrix[i, j]:
                    continue

                if i == j:
                    data.append('%s -> %s [label = "%s"]'
                                % (bini, bini, 1.0 + self.matrix[i, j]))
                else:
                    binj = binstr(nsquared - 1 - j, N)
                    data.append('%s -> %s [label = "%s"]'
                                % (bini, binj, self.matrix[i, j]))
                    data.append('%s -> %s [label = "%s"]'
                                % (binj, bini, self.matrix[j, i]))
        data.append('}')
        if not output:
            print('\n'.join(data))
        else:
            try:
                output.write('\n'.join(data) + '\n')
            except AttributeError:
                with open(output, 'w') as fobj:
                    fobj.write('\n'.join(data) + '\n')
