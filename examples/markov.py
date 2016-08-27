#!/usr/bin/env python2
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

import pylab as p

from fiabilipy import Component, Markovprocess


def markov_example():
    """ Describe the system as a Markov Process.
        states explanations :
            0 : A and B working
            1 : A working and B not working
            2 : A not working and B working
            3 : neither A nor B working
    """
    A = Component('A', 1e-4, 1.1e-3)
    B = Component('B', 4e-4, 1.4e-3)

    components = (A, B)

    initstates = {0: 0.8, 1: 0.1, 2: 0.1}

    process = Markovprocess(components, initstates)

    timerange = range(0, 5000, 10)
    states = {u'nominal' : lambda x: all(x),
              u'dégradé' : lambda x: not(all(x)) and any(x), #at least one but all
              u'défaillant' : lambda x: not(x[0] or x[1]),   #none
              u'disponible' : lambda x: any(x), #at least one
             }

    for name, state in states.iteritems():
        data = [process.value(t, statefunc=state) for t in timerange]
        p.plot(timerange, data, label=name)
    p.legend()
    p.show()


if __name__ == '__main__':
    markov_example()
