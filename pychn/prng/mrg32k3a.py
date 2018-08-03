#!/usr/bin/env python
"""Provide a subclass of random.Random using mrg32k3a as the generator with substream support."""

import random
from math import log


## constants used in mrg32k3a and in substream generation
## all from:
 # P. L'Ecuyer, ``Good Parameter Sets for Combined Multiple Recursive Random Number Generators'',
 # Operations Research, 47, 1 (1999), 159--164.
 #
 # P. L'Ecuyer, R. Simard, E. J. Chen, and W. D. Kelton,
 # ``An Objected-Oriented Random-Number Package with Many Long Streams and Substreams'',
 # Operations Research, 50, 6 (2002), 1073--1075

a1p127 = [[2427906178.0, 3580155704.0, 949770784.0],
    [226153695.0, 1230515664.0, 3580155704.0],
    [1988835001.0,  986791581.0, 1230515664.0]
]

a2p127 = [[1464411153.0,  277697599.0, 1610723613.0],
    [32183930.0, 1464411153.0, 1022607788.0],
    [2824425944.0, 32183930.0, 2093834863.0]
]

mrgnorm = 2.328306549295727688e-10
mrgm1 = 4294967087.0
mrgm2 = 4294944443.0
mrga12 = 1403580.0
mrga13n = 810728.0
mrga21 = 527612.0
mrga23n = 1370589.0


#constants used for approximating the inverse standard normal cdf
## Beasly-Springer-Moro
bsma = [2.50662823884, -18.61500062529, 41.39119773534, -25.44106049637]
bsmb = [-8.47351093090, 23.08336743743, -21.06224101826, 3.13082909833]
bsmc = [0.3374754822726147, 0.9761690190917186, 0.1607979714918209, 0.0276438810333863, 0.0038405729373609,0.0003951896411919, 0.0000321767881768, 0.0000002888167364, 0.0000003960315187]


# this is adapted to pure Python from the P. L'Ecuyer code referenced above
def mrg32k3a(seed):
    p1 = mrga12*seed[1] - mrga13n*seed[0]
    k1 = int(p1/mrgm1)
    p1 -= k1*mrgm1
    if p1 < 0.0:
        p1 += mrgm1
    p2 = mrga21*seed[5] - mrga23n*seed[3]
    k2 = int(p2/mrgm2)
    p2 -= k2*mrgm2
    if p2 < 0.0:
        p2 += mrgm2
    if p1 <= p2:
        u = (p1 - p2 + mrgm1)*mrgnorm
    else:
        u = (p1 - p2)*mrgnorm
    newseed = (seed[1], seed[2], p1, seed[4], seed[5], p2)
    return newseed, u


# as in beasly-springer-moro
def bsm(u):
    a = (2.50662823884, -18.61500062529, 41.39119773534, -25.44106049637)
    b = (-8.47351093090, 23.08336743743, -21.06224101826, 3.13082909833)
    c = (0.3374754822726147, 0.9761690190917186, 0.1607979714918209, 0.0276438810333863, 0.0038405729373609,0.0003951896411919, 0.0000321767881768, 0.0000002888167364, 0.0000003960315187)
    y = u - 0.5
    if abs(y) < 0.42:
        r = pow(y, 2)
        r2 = pow(r, 2)
        r3 = pow(r, 3)
        r4 = pow(r, 4)
        asum = sum([a[0], a[1]*r, a[2]*r2, a[3]*r3])
        bsum = sum([1, b[0]*r, b[1]*r2, b[2]*r3, b[3]*r4])
        z = y*(asum/bsum)
    else:
        if y < 0.0:
            signum = -1
            r = u
        else:
            signum = 1
            r = 1 - u
        s = log(-log(r))
        s0 = pow(s, 2)
        s1 = pow(s, 3)
        s2 = pow(s, 4)
        s3 = pow(s, 5)
        s4 = pow(s, 6)
        s5 = pow(s, 7)
        s6 = pow(s, 8)
        clst = [c[0], c[1]*s, c[2]*s0, c[3]*s1, c[4]*s2, c[5]*s3, c[6]*s4, c[7]*s5, c[8]*s6]
        t = sum(clst)
        z = signum*t
    return z


class MRG32k3a(random.Random):
    """Subclass of the default random.Random using mrg32k3a as the generator."""

    def __init__(self, x=None):
        """Initialize the generator with an optional mrg32k3a seed (tuple of length 6)."""
        if not x:
            x = (12345, 12345, 12345, 12345, 12345, 12345)
        assert(len(x) == 6)
        self.version = 2
        super().__init__(x)

    def seed(self, a):
        """Set the seed of mrg32k3a and update the generator state."""
        assert(len(a) == 6)
        self._current_seed = a
        super().seed(a)

    def random(self):
        """Generate a random u ~ U(0, 1) and advance the generator state."""
        seed = self._current_seed
        newseed, u = mrg32k3a(seed)
        self.seed(newseed)
        return u

    def get_seed(self):
        """Return the current mrg32k3a seed."""
        return self._current_seed

    def getstate(self):
        """Return a state object describing the current generator."""
        return self.get_seed(), super().getstate()

    def setstate(self, state):
        """Set the internal state of the generator."""
        self.seed(state[0])
        super().setstate(state[1])

    def normalvariate(self, mu=0, sigma=1):
        """Generate a random z ~ N(mu, sigma)."""
        u = self.random()
        z = bsm(u)
        return sigma*z + mu


def mat333mult(a, b):
    res = [0, 0, 0]
    r3 = range(3)
    for i in r3:
        res[i] = sum([a[i][j]*b[j] for j in r3])
    return res


def mat311mod(a, b):
    res = [0, 0, 0]
    r3 = range(3)
    for i in r3:
        res[i] = a[i] - int(a[i]/b)*b
    return res


def get_next_prnstream(seed):
    """Create a generator seeded 2^127 steps from the input seed."""
    assert(len(seed) == 6)
    # split the seed into 2 components of length 3
    s1 = seed[0:3]
    s2 = seed[3:6]
    # A*s % m
    ns1m = mat333mult(a1p127, s1)
    ns2m = mat333mult(a2p127, s2)
    ns1 = mat311mod(ns1m, mrgm1)
    ns2 = mat311mod(ns2m, mrgm2)
    # random.Random objects need a hashable seed
    sseed = tuple(ns1 + ns2)
    prn = MRG32k3a(sseed)
    return prn
