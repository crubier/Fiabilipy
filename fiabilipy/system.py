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

r""" Reliability system design and computation

This module gives classes and functions to design complex systems and
compute some metrics, such as the reliability, the availability, the
Mean-Time-To-Failure, and so on.

"""
from __future__ import print_function
from builtins import range
from builtins import object

from numpy import empty, ones, delete
from sympy import exp, Symbol, oo
from scipy.special import binom
from itertools import combinations, chain
from collections import Iterable
import networkx as nx

from fiabilipy import Component
from functools import reduce

__all__ = ['System']

ALLSUBSETS = lambda n: (chain(*[combinations(list(range(n)), ni)
                        for ni in range(n+1)]))


class System(object):
    r""" Describe a system with different components.

        The components are linked together thanks to a reliability diagram.
        This reliability diagram is represented by a graph. This graph
        *must* have two special nodes called `E` and `S`. `E` represents the
        start of the system and `S` its end (names stand for “Entrée”
        (start) and “Sortie” (end) in French).

        Examples
        --------

        Let’s have a look to the following system::

                 | -- C0 -- |
            E -- |          | -- C2 -- S
                 | -- C1 -- |

        Thus, to represent such a system, you must create the three
        components C0, C1 and C2 and link them.

        >>> C = [Component(i, 1e-4) for i in xrange(3)]
        >>> S = System()
        >>> S['E'] = [C[0], C[1]]
        >>> S[C[0]] = [C[2]]
        >>> S[C[1]] = [C[2]]
        >>> S[C[2]] = ['S']

        So, you can use the `System` object as a simple python dictionnary
        where each key is a component and the value associated it the list
        of the component’s successors.
    """

    def __init__(self, graph=None):
        self._graph = nx.DiGraph(graph)
        self._map = {'E':'E','S':'S'} #FIXME create map str -> component in case graph is non empty
        self._cache = {}
        self._t = Symbol('t', positive=True)

    def __getitem__(self, component):
        return self._map[self._graph[component.__str__()]]

    def __setitem__(self, component, successors):
        #Let’s do different checks before inserting the element
        if not isinstance(successors, Iterable):
            if not isinstance(successors, Component):
                msg = u'successors must be a list of components, a component '
                raise ValueError(msg)
            successors = [successors]
        if component != 'E' and 'E' not in self._graph:
            msg = u"'E' must be the first inserted component"
            raise ValueError(msg)
        for successor in successors:
            if successor != 'S':
                successor._systems.add(self)
            self._graph.add_edge(component.__str__(), successor.__str__())
            self._map[component.__str__()]=component
            self._map[successor.__str__()]=successor #FIXME this may be optional

        #reset the cache
        self._cache = {}

    def __delitem__(self, component):
        for c in self._graph:
            try:
                self._graph.remove_edge(c, component.__str__())
            except nx.NetworkXError: #i.e. edge(c, component) does not exist
                pass
            except AttributeError:
                assert self._graph[c] == 'S'
        self._graph.remove_node(component.__str__())
        if component not in self.components:
            component._systems.remove(self)
            del self._map[component.__str__()]
        #reset the cache
        self._cache = {}

    def __len__(self):
        return len(self._graph)

    def __repr__(self):
        return u'I\'m a system'

    def copy(self):
        r""" Return a copy of the system.

            Returns
            -------
            out: System
                A copy of the current system

            Notes
            -----
                The components are the same (same reference).
                Only the internal graph is new
        """
        _copy = System()
        _copy['E'] = [] #'E' must be the first inserted component
        for c in self._graph:
            _copy[c] = self[c][:]
        _copy._map = self._map.copy()
        return _copy

    @property
    def components(self):
        r""" The list of the components used by the system

            Returns
            -------
            out: list
                the list of the components used by the system, except `E` and
                `S`
        """
        #FIXME Vincent it should be the component not its str
        return [self._map[comp] for comp in self._graph if comp not in ('E', 'S')]

    def _probabilitiescomputation(self, t, method):
        """ Given a system and a `method` (either availability or
            maintainability or reliability), this method evaluates the asking
            value by exploring the graph at time `t`.
        """
        #TODO : improve complexity ?
        #   n
        # P(U a_i) = sum     (-1)^{-1+|s|} P(^a_i)
        #  i=1      s\in[1,n],              i\in s
        #           s != {}
        #
        paths = self.successpaths
        R = 0.0
        for S in ALLSUBSETS(len(paths)):
            if not S:
                continue
            comps = set([c for i in S for c in paths[i][1:-1]])
            r = reduce(lambda x, y:x*getattr(y, method)(t), comps, 1)
            R += -r if len(S) % 2 == 0 else r
        return R

    def availability(self, t):
        r""" Compute the availability of the whole system

            This method compute the availability of the system at `t`.

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
            >>> power = Component('P', 1e-6, 2e-4)
            >>> t = Symbol('t', positive=True)
            >>> S = System()
            >>> S['E'] = [power]
            >>> S[power] = [motor]
            >>> S[motor] = 'S'
            >>> S.availability(t) #doctest: +NORMALIZE_WHITESPACE
            (200/201 + exp(-201*t/1000000)/201)*(300/301 +
            exp(-301*t/10000)/301)
            >>> S.availability(1000)
            0.995774842225189
        """
        try:
            formula = self._cache['availability']
        except KeyError:
            formula = self._probabilitiescomputation(self._t, 'availability')
            self._cache['availability'] = formula

        if isinstance(t, Symbol):
            return formula.nsimplify()
        else:
            return formula.subs(self._t, t).evalf()

    def reliability(self, t):
        r""" Compute the reliability of the whole system

            This method compute the reliability of the system at `t`.

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
            >>> power = Component('P', 1e-6, 2e-4)
            >>> t = Symbol('t', positive=True)
            >>> S = System()
            >>> S['E'] = [power]
            >>> S[power] = [motor]
            >>> S[motor] = 'S'
            >>> S.reliability(t)
            exp(-101*t/1000000)
            >>> S.reliability(1000)
            0.903933032885864
        """
        try:
            formula = self._cache['reliability']
        except KeyError:
            formula = self._probabilitiescomputation(self._t, 'reliability')
            self._cache['reliability'] = formula

        if isinstance(t, Symbol):
            return formula.nsimplify()
        else:
            return formula.subs(self._t, t).evalf()

    def maintainability(self, t):
        r""" Compute the maintainability of the whole system

            This method compute the maintainability of the system at `t`.

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
            >>> power = Component('P', 1e-6, 2e-4)
            >>> t = Symbol('t', positive=True)
            >>> S = System()
            >>> S['E'] = [power]
            >>> S[power] = [motor]
            >>> S[motor] = 'S'
            >>> S.maintainability(t)
            (1 - exp(-3*t/100))*(1 - exp(-t/5000))
            >>> S.maintainability(1000)
            0.181269246922001
        """
        try:
            formula = self._cache['maintainability']
        except KeyError:
            formula = self._probabilitiescomputation(self._t, 'maintainability')
            self._cache['maintainability'] = formula

        if isinstance(t, Symbol):
            return formula.nsimplify()
        else:
            return formula.subs(self._t, t).evalf()

    @property
    def mttf(self):
        r""" Compute the Mean-Time-To-Failure of the system

            The MTTF is defined as :
                :math:`MTTF = \int_{0}^{\infty} R(t)dt`

            Returns
            -------
            out : float
                The system MTTF

            Examples
            --------
            >>> motor = Component('M', 1e-4, 3e-2)
            >>> power = Component('P', 1e-6, 2e-4)
            >>> S = System()
            >>> S['E'] = [power]
            >>> S[power] = [motor]
            >>> S[motor] = 'S'
            >>> S.mttf
            1000000/101
        """
        try:
            return self._cache['mttf']
        except KeyError:
            t = Symbol('t', positive=True)
            self._cache['mttf'] = self.reliability(t).integrate((t, 0, oo))
            return self._cache['mttf']

    @property
    def mttr(self):
        r""" Compute the Mean-Time-To-Repair of the system

            The MTTR is defined as :
                :math:`MTTF = \int_{0}^{\infty} 1 - M(t)dt`

            Returns
            -------
            out : float
                The system MTTR

            Examples
            --------
            >>> motor = Component('M', 1e-4, 3e-2)
            >>> power = Component('P', 1e-6, 2e-4)
            >>> S = System()
            >>> S['E'] = [power]
            >>> S[power] = [motor]
            >>> S[motor] = 'S'
            >>> S.mttr
            2265100/453
        """
        try:
            return self._cache['mttr']
        except KeyError:
            t = Symbol('t', positive=True)
            mttr = (1 - self.maintainability(t)).integrate((t, 0, oo))
            self._cache['mttr'] = mttr
            return self._cache['mttr']


    @property
    def successpaths(self):
        r""" Return all the success paths of the reliability diagram

            A success path is defined as a path from 'E' to 'S'.

            Returns
            -------
            out : list of paths
                the list of all the success paths. A path, is defined as a list
                of components

            Examples
            --------
            >>> motor = Component('M', 1e-4, 3e-2)
            >>> powers = [Component('P{}'.format(i), 1e-6, 2e-4) for i in (0,1)]
            >>> S = System()
            >>> S['E'] = [powers[0], powers[1]]
            >>> S[powers[0]] = S[powers[1]] = [motor]
            >>> S[motor] = 'S'
            >>> S.successpaths #doctest: +NORMALIZE_WHITESPACE
            [['E', Component(P0), Component(M), 'S'],
             ['E', Component(P1), Component(M), 'S']]
        """
        try:
            return self._cache['successpaths']
        except KeyError:
            self._cache['successpaths'] = list(self.findallpaths('E', 'S'))
            return self._cache['successpaths']

    def findallpaths(self, start='E', end='S'):
        r""" Find all paths between two components in the reliability diagram

            Parameters
            ----------
            start : Component, optional
                find paths from this component
            end : Component, optional
                find paths to this component

            Returns
            -------
            out : iterator
                an iterator on the paths from `start` to `stop`

            Examples
            --------
            >>> motor = Component('M', 1e-4, 3e-2)
            >>> powers = [Component('P{}'.format(i), 1e-6, 2e-4) for i in (0,1)]
            >>> S = System()
            >>> S['E'] = [powers[0], powers[1]]
            >>> S[powers[0]] = S[powers[1]] = [motor]
            >>> S[motor] = 'S'
            >>> list(S.findallpaths(start=powers[0])) #doctest: +NORMALIZE_WHITESPACE
            [[Component(P0), Component(M), 'S']]
        """
        return [[self._map[x] for x in l] for l in nx.all_simple_paths(self._graph, start.__str__(), end.__str__())]

    def minimalcuts(self, order=1):
        r""" List the minimal cuts of the system of order <= `order`

            A minimal cut of order :math:`n`, is a set of :math:`n` components,
            such as if there all unavailable, the whole system is unavailable.

            This function aims to find out every minimal cuts of order inferior
            to `order`.

            Parameters
            ----------
            order : int, optional
                The maximal order to look for.

            Returns
            -------
            out : list of frozensets
                each frozenset contains the components that constitute a minimal
                cut

            Examples
            --------
            >>> motor = Component('M', 1e-4, 3e-2)
            >>> powers = [Component('P{}'.format(i), 1e-6, 2e-4) for i in (0,1)]
            >>> S = System()
            >>> S['E'] = [powers[0], powers[1]]
            >>> S[powers[0]] = S[powers[1]] = [motor]
            >>> S[motor] = 'S'
            >>> S.minimalcuts(order=1) #doctest: +ELLIPSIS
            [frozenset(...)]
            >>> S.minimalcuts(order=2) #doctest: +ELLIPSIS
            [frozenset(...), frozenset(...)]
        """
        paths = self.successpaths
        incidence = empty((len(paths), len(self.components)))

        for path in range(len(paths)):
            for comp in range(len(self.components)):
                if self.components[comp] in paths[path]:
                    incidence[path, comp] = 1
                else:
                    incidence[path, comp] = 0

        pairs = list(self.components)
        minimal = []

        for k in range(1, order+1):
            if incidence.shape[1] == 0: #No more minimalcuts
                break
            #Let’s looking for column of ones
            vones = ones(len(paths))
            indicetodelete = []
            for comp in range(len(pairs)):
                if (incidence[:, comp] == vones).all():
                    if isinstance(pairs[comp], frozenset):
                        minimal.append(pairs[comp])
                    else:
                        minimal.append(frozenset([pairs[comp]]))
                    indicetodelete.append(comp)

            if k >= order:
                #so it’s useless to compute newpairs and the new incidence
                #matrix because they won’t be used anymore.
                continue

            incidence = delete(incidence, indicetodelete, axis=1)
            pairs = [p for i, p in enumerate(pairs) if i not in indicetodelete]
            newpairs = list(combinations(list(range(len(pairs))), k+1))
            incidence_ = empty((len(paths), len(newpairs)))
            for x in range(incidence_.shape[0]):
                for y in range(incidence_.shape[1]):
                    value = 0
                    for comp in newpairs[y]:
                        if incidence[x, comp]:
                            value = 1
                            break
                    incidence_[x, y] = value

            incidence = incidence_
            pairs = [frozenset([pairs[x] for x in p]) for p in newpairs]

        return minimal

    def faulttreeanalysis(self, output=None, order=2):
        r""" Build the fault tree analysis of the system

            Print (or write) the content of the dot file needed to draw the
            fault tree of the system.

            Parameters
            ----------
            output : file-like object, optional
                If `output` is given, then the content is written into this
                file. `output` *must* have a :py:meth:`write` method.

            order : int, optional
                This is the maximum order of the minimal cuts the function looks
                for.

            Notes
            -----
            Please, see the `Graphviz <http://graphviz.org/>` website for more
            information about how to transform the ouput code into a nice
            picture.

        """
        #TODO the tree needs to be simplified
        cuts = self.minimalcuts(order)
        data = ['digraph G {']
        data.append('\t"not_S" -> "or"')
        for i, cut in enumerate(cuts):
            data.append('\tor -> and_%s' % i)
            for comp in cut:
                data.append('\tand_%s -> "%s"' % (i, comp.name))
        data.append('}')

        if not output:
            print('\n'.join(data))
        else:
            try:
                output.write('\n'.join(data) + '\n')
            except AttributeError:
                with open(output, 'w') as fobj:
                    fobj.write('\n'.join(data) + '\n')


    def draw(self):
        r""" Draw the system

            Draw the system with graphviz.

            Examples
            --------
            >>> import pylab as p
            >>> motor = Component('M', 1e-4, 3e-2)
            >>> powers = [Component('P{}'.format(i), 1e-6, 2e-4) for i in (0,1)]
            >>> S = System()
            >>> S['E'] = [powers[0], powers[1]]
            >>> S[powers[0]] = S[powers[1]] = [motor]
            >>> S[motor] = 'S'
            >>> S.draw()
            >>> p.show()

        """
        nx.draw_graphviz(self._graph)
