#!/usr/bin/env python
# -*- coding: utf-8 -*-

from utils import crt, b2i, i2b
from gmpy2 import mpz, invert


def legendre(a, p):
    '''Legendre symbol'''
    tmp = pow(a, (p-1)//2, p)
    return -1 if tmp == p-1 else tmp


def tonelli_shanks(n, p):
    '''Find r such that r^2 = n % p, r2 == p-r'''
    if legendre(n, p) == -1:
        print('Error: not square root')
        return False

    s = 0
    q = p-1
    while q&1 == 0:
        s += 1
        q >>= 1

    if s == 1:
        return pow(n, (p+1)//4, p)

    z = 1
    while legendre(z, p) != -1:
        z += 1
    c = pow(z, q, p)

    r = pow(n, (q+1)//2, p)
    t = pow(n, q, p)
    m = s
    while t != 1:
        i = 1
        while i < m:
            if pow(t, 2**i, p) == 1:
                break
            i += 1
        b = pow(c, 2**(m-i-1), p)
        r = (r*b) % p
        t = (t * (b**2)) % p
        c = pow(b, 2, p)
        m = i
    return r


class EC(object):
    def __init__(self, p, a, b):
        self.p = p
        self.a = a
        self.b = b

    def add(self, point1, point2):
        if point1 == Identity(self):
            return point2

        if point2 == Identity(self):
            return point1

        if point1 == -point2:
            return Identity(self)

        p, a, b = mpz(self.p), mpz(self.a), mpz(self.b)
        x1, y1 = mpz(point1.x), mpz(point1.y)
        x2, y2 = mpz(point2.x), mpz(point2.y)

        if point1 == point2:
            m = ((3*(x1**2) + a) * invert(2*y1, p)) % p
        else:
            m = ((y2 - y1) * invert(x2 - x1, p)) % p

        x3 = (m**2 - x1 - x2) % p
        y3 = (m*(x1 - x3) - y1) % p
        return self.point(x3, y3)

    def mul(self, point, exponent):
        result = Identity(self)
        while exponent > 0:
            if exponent & 1:  # odd
                result += point
            point += point
            exponent >>=  1
        return result

    def Identity(self):
        return Identity(self)


class EC_w(EC):
    '''Weierstrass curve'''
    def __init__(self, p, a, b):
        super(EC_w, self).__init__(p, a, b)

    def correct(self, point):
        return pow(point.y, 2, self.p) == (point.x**3 + self.a*point.x + self.b) % self.p

    def point(self, x, y):
        return Point(x, y, self)

    def __str__(self):
        return 'y^2 = x^3 + {}*x + {}'.format(self.a, self.b)


class Point(EC):
    def __init__(self, x, y, curve):
        super(Point, self).__init__(curve.p, curve.a, curve.b)
        self.x = x
        self.y = y
        self.curve = curve

    def curve(self):
        return self.curve

    def is_correct(self):
        return self.curve.correct(self)

    def get_y_square(self):
        return (self.x**3 + self.a*(self.x**2) + self.x)%self.p

    def set_y(self):
        tmp = tonelli_shanks(self.get_y_square(), self.p)
        if tmp:
            self.y = tmp
        else:
            self.y = None

    def __add__(self, other):
        return self.curve.add(self, other)

    def __sub__(self, other):
        return self.curve.add(self, -other)

    def __mul__(self, exponent):
        return self.curve.mul(self, exponent)

    __rmul__ = __mul__

    def __eq__(self, other):
        if self.y is None or other.y is None:  # for montgomery curves
            return self.x == other.x
        return (self.x, self.y) == (other.x, other.y)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return '({}, {})'.format(self.x, self.y)

    def __neg__(self):
        if self.y is None:
            return self.curve.point(self.x, None)
        return self.curve.point(self.x, -self.y%self.p)


class Identity(Point):        
    def __init__(self, curve):
        super(Identity, self).__init__(0, 1, curve)

    def __str__(self):
        return 'O'

    def __add__(self, other):
        return other


if __name__ == '__main__':
    print('test ec', end='')
    p = 233970423115425145524320034830162017933
    a = -95051
    b = 11279326
    curve = EC_w(p, a, b)
    curve.order = (2**3) * 29246302889428143187362802287225875743

    G = curve.point(182, 85518893674295321206118380980485522083)
    G.order = 29246302889428143187362802287225875743

    assert curve.correct(G)
    assert G*G.order == Identity(curve)

    n = 12354213
    m = 6452341222
    x = n + m
    assert G*x == G*n + G*m
    print(' - passed')