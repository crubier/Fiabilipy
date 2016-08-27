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

from __future__ import print_function, absolute_import
from builtins import range
import unittest2

from random import random

from fiabilipy import System, Component, Markovprocess

class TestMarkov(unittest2.TestCase):
#The reliabily and the availability of systems is already tested. Let’s
#assume they are correct for any systems.
#The idea behind those tests is very simple. We build different systems twice :
# - one with the “standard” way, by describing a system by its reliabily block
#   diagram.
# - one with a Markov process, which is going to be tested
#once that is done, the availabilities computed have just to be compared each
#others. It a different result is found, then there is a bug (or more…)

    def setUp(self):
        #Let’s build some standard systems
        systems = {'series-parallel': System(),
                   'parallel-series': System(),
                   'simple': System()
                  }

        lambdas = {'alim':1e-4, 'motor':2e-5}
        mus = {'alim':5e-4, 'motor':2e-3}

        alim = [Component('Alim_A', lambda_=lambdas['alim'], mu=mus['alim']),
                Component('Alim_B', lambda_=lambdas['alim'], mu=mus['alim']),
               ]
        motors = [Component('Motor_A', lambda_=lambdas['motor'], mu=mus['motor']),
                  Component('Motor_B', lambda_=lambdas['motor'], mu=mus['motor']),
                 ]

        systems['simple']['E'] = alim[0]
        systems['simple'][alim[0]] = motors[0]
        systems['simple'][motors[0]] = 'S'

        systems['series-parallel']['E'] = [alim[0], alim[1]]
        systems['series-parallel'][alim[0]] = motors[0]
        systems['series-parallel'][alim[1]] = motors[1]
        systems['series-parallel'][motors[0]] = 'S'
        systems['series-parallel'][motors[1]] = 'S'

        systems['parallel-series']['E'] = [alim[0], alim[1]]
        systems['parallel-series'][alim[0]] = [motors[0], motors[1]]
        systems['parallel-series'][alim[1]] = [motors[0], motors[1]]
        systems['parallel-series'][motors[0]] = 'S'
        systems['parallel-series'][motors[1]] = 'S'

        #Let’s build the markov equivalent system
        self.components = (alim[0], alim[1], motors[0], motors[1])
        self.process = Markovprocess(self.components, {0:1}) #All the components work

        self.states = {
            'series-parallel': lambda x : (x[0]*x[2]) + (x[1]*x[3]),
            'parallel-series': lambda x : (x[0]+x[1]) * (x[2]+x[3]),
            'simple': lambda x : x[0]*x[2],
        }

        self.systems = systems

    def test_availability(self):
        #Let’s do `maxiter` checks of availability values, for times randomly
        #picked between [0, `maxtime`)
        maxiter = 1000
        maxtime = 420000
        for _ in range(maxiter):
            t = random() * maxtime
            for name, states in self.states.items():
                self.assertAlmostEqual(self.process.value(t, states),
                                       self.systems[name].availability(t))

if __name__ == '__main__':
    unittest2.main()
