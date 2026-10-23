# -*- coding: utf-8 -*-
"""使用 python -m unittest -v test_iteration 執行。"""
import math
import unittest
import numpy as np
from iterative import calculate
from iter_framework import (generic_iterator,demo_fixed_point,demo_newton,
    demo_gauss_seidel,demo_power_iteration,demo_qr_algorithm,demo_rk4,
    demo_pagerank,demo_kmeans,demo_em_two_coin)

class TestIteration(unittest.TestCase):
    def test_three_methods(self):
        rows=calculate(1,20)
        self.assertEqual(rows[0][1],3.0)
        self.assertEqual(rows[1][1],1.0)
        self.assertAlmostEqual(rows[-1][2],math.sqrt(3),places=6)
        self.assertAlmostEqual(rows[-1][3],math.sqrt(3),places=10)

    def test_generic(self):
        v,n,ok=generic_iterator(lambda x:x/2,lambda a,b,i:abs(b)<1e-8,1.0)
        self.assertTrue(ok)
        self.assertLess(abs(v),1e-8)

    def test_algorithms(self):
        self.assertTrue(np.all(np.isfinite(demo_fixed_point())))
        self.assertAlmostEqual(demo_newton(),2.,places=8)
        self.assertTrue(np.allclose(demo_gauss_seidel(),[2.25,2.,3.75],atol=1e-5))
        self.assertGreater(demo_power_iteration(),4.)
        self.assertTrue(np.allclose(demo_qr_algorithm(),[1.,2.2679491924,5.7320508076],atol=1e-5))
        t,y=demo_rk4();self.assertAlmostEqual(t,2.,places=8)
        self.assertAlmostEqual(y,math.exp(2)+2,delta=.003)
        pagerank=demo_pagerank();self.assertAlmostEqual(sum(pagerank),1.,places=6)
        self.assertTrue(np.all(np.isfinite(demo_kmeans())))
        self.assertTrue(all(math.isfinite(x) for x in demo_em_two_coin()))

if __name__=='__main__':
    unittest.main(verbosity=2)
