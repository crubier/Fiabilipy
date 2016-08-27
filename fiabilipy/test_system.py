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
import unittest2

from sympy import symbols, exp
from networkx import DiGraph, is_isomorphic

from fiabilipy import Component, Voter, System

class TestComponent(unittest2.TestCase):
    """ Test the Component class.
    """
    def setUp(self):
        """ Here we build the component we will use as test subjects
            We assume components have constant failure and maintainability rates
        """

        self.lambda_, self.mu = symbols('l, m',
                                        constant=True,
                                        positive=True,
                                        null=False
                                       )
        self.t = symbols('t', positive=True)
        self.component = Component('C', self.lambda_, self.mu)

    def test_reliability(self):
        """ Check the reliability is equals to the theorical one """
        self.assertEqual(exp(-self.lambda_ * self.t),
                         self.component.reliability(self.t))

    def test_maintainability(self):
        """ Check the maintainability is equals to the theorical one """
        self.assertEqual(1 - exp(-self.mu * self.t),
                         self.component.maintainability(self.t))

    def test_availability(self):
        """ Check the availability is equals to the theorical one """
        availability = self.lambda_ * \
                       exp(self.t*(-self.lambda_ - self.mu)) / \
                       (self.lambda_ + self.mu) + \
                       self.mu/(self.lambda_ + self.mu)

        self.assertEqual(availability,
                         self.component.availability(self.t))

class TestVoter(unittest2.TestCase):
    """ Test the Voter class.
    """
    pass

class TestSystem(unittest2.TestCase):
    """ Test the System class.
    """

    def setUp(self):
        """ Here we build some standard systems we will use as test subjects
        """
        systems = {'simple':System(),
                   'series-parallel':System(),
                   'parallel-series':System(),
                   'complex':System(),
                   'voter':System(),
                  }

        lambdas = {'alim': symbols('l_alim', positive=True, null=False),
                   'motor': symbols('l_motor', positive=True, null=False),
                  }
        mus = {'alim': symbols('m_alim', positive=True, null=False),
               'motor': symbols('m_motor', positive=True, null=False),
              }

        alim = [Component('Alim_A', lambda_=lambdas['alim'], mu=mus['alim']),
                Component('Alim_B', lambda_=lambdas['alim'], mu=mus['alim']),
                Component('Alim_C', lambda_=lambdas['alim'], mu=mus['alim']),
               ]
        motors = [
                Component('Motor_A', lambda_=lambdas['motor'], mu=mus['motor']),
                Component('Motor_B', lambda_=lambdas['motor'], mu=mus['motor']),
                 ]

        voter = Voter(alim[0], M=2, N=3)

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

        systems['complex']['E'] = [alim[0], alim[1], alim[2]]
        systems['complex'][alim[0]] = motors[0]
        systems['complex'][alim[1]] = [motors[0], motors[1]]
        systems['complex'][alim[2]] = motors[1]
        systems['complex'][motors[0]] = 'S'
        systems['complex'][motors[1]] = 'S'

        systems['voter']['E'] = voter
        systems['voter'][voter] = [motors[0], motors[1]]
        systems['voter'][motors[0]] = 'S'
        systems['voter'][motors[1]] = 'S'

        self.systems = systems
        self.alim = alim
        self.motors = motors
        self.voter = voter
        self.lambdas = lambdas
        self.mus = mus

    def test_successpaths(self):
        """ Check that all success paths are correctly found.
        """
        paths = {
            'simple' : set([('E', self.alim[0], self.motors[0], 'S')]),
            'series-parallel': set([('E', self.alim[0], self.motors[0], 'S'),
                                    ('E', self.alim[1], self.motors[1], 'S')]),
            'parallel-series': set([('E', self.alim[0], self.motors[0], 'S'),
                                    ('E', self.alim[0], self.motors[1], 'S'),
                                    ('E', self.alim[1], self.motors[1], 'S'),
                                    ('E', self.alim[1], self.motors[0], 'S')]),
            'complex': set([('E', self.alim[0], self.motors[0], 'S'),
                            ('E', self.alim[1], self.motors[0], 'S'),
                            ('E', self.alim[1], self.motors[1], 'S'),
                            ('E', self.alim[2], self.motors[1], 'S')]),
            'voter': set([('E', self.voter, self.motors[0], 'S'),
                          ('E', self.voter, self.motors[1], 'S')]),
        }

        for (name, S) in self.systems.items():
            for path in S.successpaths:
                paths[name].remove(tuple(path))
            self.assertEqual(paths[name], set())

    def test_minimalcuts(self):
        """ Check for minimal cut of orders 1 and 2.
        """
        cuts = {
            1: {
                 'simple': set([frozenset([self.alim[0]]),
                                frozenset([self.motors[0]])]),
                 'series-parallel': set(),
                 'parallel-series': set(),
                 'complex': set(),
                 'voter': set([frozenset([self.voter])]),
               },
            2: {
                 'simple': set([frozenset([self.alim[0]]),
                                frozenset([self.motors[0]])]),
                 'series-parallel': set([
                        frozenset([self.alim[1], self.alim[0]]),
                        frozenset([self.alim[1], self.motors[0]]),
                        frozenset([self.motors[1], self.alim[0]]),
                        frozenset([self.motors[1], self.motors[0]]),
                                        ]),
                 'parallel-series': set([
                        frozenset([self.alim[1], self.alim[0]]),
                        frozenset([self.motors[1], self.motors[0]])]),
                 'complex': set([frozenset([self.motors[0], self.motors[1]])]),
                 'voter': set([frozenset([self.voter]),
                               frozenset([self.motors[0], self.motors[1]])]),
               },
        }

        for order in [1, 2]:
            for (name, S) in self.systems.items():
                for cut in S.minimalcuts(order):
                    cuts[order][name].remove(cut)
                self.assertEqual(cuts[order][name], set([]))

    def test_mttfvalues(self):
        r""" Check if the calculated MTTF values are correct.
             Testing MTTF values is interesting because there are computed by
             integration of reliability from 0 to \inf.
             So if the values of MTTF are correct, it means :
              - MTTF values are correct
              - Reliabitily value for any t are correct too.
             The drawback is that if this test fails, we don’t known which of
             MTTF property or reliability method is failing.
        """

        la = self.lambdas['alim']
        lm = self.lambdas['motor']
        mttf = {'simple': 1.0/(la + lm),
                'series-parallel': 3.0/(2*(la + lm)),
                'parallel-series':
                    1.0/(2*la + 2*lm) - 2.0/(2*la + lm) \
                    - 2.0/(la + 2*lm) + 4.0/(la + lm),
                'complex':
                    4.0/(la + lm) - 1.0/(2*lm + la) + 1.0/(2*lm + 3*la) \
                    - 1.0/(2*lm + 2*la) - 2.0/(2*la + lm),
                'voter':
                    6.0/(2*la + lm) - 3.0/(2*la + 2*lm) - 6.0/(3*la + lm) \
                    + 3.0/(3*la + 2*lm) + 2.0/(3*la + lm) - 1.0/(3*la + 2*lm)
               }

        for (name, values) in mttf.items():
            diff = values - self.systems[name].mttf
            self.assertEqual(diff.simplify(), 0)

    def test_graphmanagement(self):
        """ Check if the constructing a system by its graph works as intended.
        """
        component = [Component('C%s' % i, 1e-3) for i in range(4)]
        system = System()

        #because 'E' must be the first inserted element
        with self.assertRaises(ValueError):
            system[component[0]] = 'S'

        #Assert the following constructions don’t fail.
        #from a list
        system['E'] = [component[0], component[1]]
        system[component[0]] = 'S'
        wanted = DiGraph({'E':[component[0].__str__(), component[1].__str__()], component[0].__str__():['S']})
        self.assertTrue(is_isomorphic(system._graph, wanted))

        del system[component[0]] #This component isn’t used anymore
        #from a single element
        system['E'] = component[1]
        system[component[1]] = 'S'
        wanted = DiGraph({'E':[component[1].__str__()], component[1].__str__():'S'})
        self.assertTrue(is_isomorphic(system._graph, wanted))

    def test_cache(self):
        """ Perfom some tests on the cache
        """
        components = [Component('C{}'.format(i), 1e-3) for i in (0, 1, 2)]
        system = System()

        #      +-- C0 --+
        #      |        |
        # E ---|        +-- C2 -- S
        #      |        |
        #      +-- C1 --+

        system['E'] = [components[0], components[1]]
        system[components[0]] = components[2]
        system[components[1]] = components[2]
        system[components[2]] = 'S'

        self.assertAlmostEqual(system.mttf, 2000/3.)
        self.assertIn('mttf', system._cache) #The mttf is cached

        components[0].lambda_ = 0.05 #Let’s change the failure rate
        self.assertEqual(system._cache, dict()) #The cache is now empty
        self.assertAlmostEqual(system.mttf, 331750/663.)
        self.assertIn('mttf', system._cache) #The mttf is cached

        #now, check if it works with a shared component
        othersystem = System()
        othersystem['E'] = components[0]
        othersystem[components[0]] = 'S'

        self.assertAlmostEqual(othersystem.mttf, 20)
        components[0].lambda_ = 2e-4
        self.assertAlmostEqual(othersystem.mttf, 5000)
        self.assertAlmostEqual(system.mttf, 29000/33.)

if __name__ == '__main__':
    unittest2.main()
