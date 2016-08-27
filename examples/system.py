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

from fiabilipy import Component, System
from matplotlib.pylab import plot, show


def system_example():
    r""" Describe the system as a reliability block diagram

              | -- A0 -- | -- M0 -- |
              |            /        |
         E -- | -- A1 -- |          | -- S
              |            \        |
              | -- A2 -- | -- M1 -- |
    """

    alim = [Component('A_%s' % i, 2e-4) for i in xrange(3)]
    motors = [Component('M_%s' % i, 1e-4) for i in xrange(2)]
    S = System()

    S['E'] = [alim[0], alim[1], alim[2]]
    S[alim[0]] = [motors[0]]
    S[alim[1]] = [motors[0], motors[1]]
    S[alim[2]] = [motors[1]]
    S[motors[0]] = 'S'
    S[motors[1]] = 'S'

    print('The MTTF of the system is :', S.mttf)

    timerange = range(0, 2*365*24, 100) # 2 years study
    reliability = [S.reliability(t) for t in timerange]
    plot(timerange, reliability)
    show()


if __name__ == '__main__':
    system_example()
