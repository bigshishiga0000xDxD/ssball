from math import sqrt, atan2, sin, cos, pi

from config import nodesize, ballsize

eps = 1e-4
inf = 1e9

class Vector:
    def __init__(self, x = None, y = None, begin = None, end = None):
        if x is not None and y is not None:
            self.x = x
            self.y = y
        else:
            self.x = end[0] - begin[0]
            self.y = end[1] - begin[1]

    def speed(self):
        return sqrt(self.x * self.x + self.y * self.y)

    def __add__(self, v):
        return Vector(x = self.x + v.x, y = self.y + v.y)

    def __sub__(self, v):
        return Vector(x = self.x - v.x, y = self.y - v.y)

    def __mul__(self, v):
        return Vector(x = self.x * v, y = self.y * v)

    def __truediv__(self, v):
        return Vector(x = self.x / v, y = self.y / v)

    def __str__(self):
        return str([self.x, self.y])

    def normalize(self):
        v = self.speed()
        self.x /= v
        self.y /= v

def scal(a, b):
    return a.x * b.x + a.y * b.y

def cross(a, b):
    return a.x * b.y - a.y * b.x

def degree(a, b):
    return abs(atan2(cross(a, b), scal(a, b)))

def distance(a, b):
    return sqrt((a[0] - b[0]) * (a[0] - b[0]) + (a[1] - b[1]) * (a[1] - b[1]))

def sgn(x):
    if x > 0:
        return 1
    elif x == 0:
        return 0
    elif x < 0:
        return -1

def wall_collision(x, y1, y2, ball, v):
    if sgn(x - ball[0]) != sgn(v.x):
        return None
    else:
        time = abs(x - ball[0]) / abs(v.x)
        result = [x, ball[1] + v.y * time]
        if y1 <= result[1] <= y2:
            return result
        else:
            return None

def floor_collision(y, x1, x2, ball, v):
    if v.y >= 0 or ball[1] < y:
        return None
    else:
        time = (ball[1] - y) / -v.y
        result = [ball[0] + v.x * time, y]
        if x1 <= result[0] <= x2:
            return result
        else:
            return None


def node_collision(node, ball, v):
    if abs(v.x) < eps and abs(v.y) < eps:
        return None

    dist = (nodesize + ballsize) / 2

    p = [ball[0] + v.x, ball[1] + v.y]

    for i in range(2):
        p[i] -= node[i]
        ball[i] -= node[i]

    a = p[1] - ball[1]
    b = ball[0] - p[0]
    c = p[0] * ball[1] - p[1] * ball[0]

    l = [
        -(a * c) / (a * a + b * b),
        -(b * c) / (a * a + b * b)
    ]

    if abs(distance([0, 0], l) - dist) < eps:
        return [l[0] + node[0], l[1] + node[1]]
    elif distance([0, 0], l) < dist:
        d = sqrt(dist * dist - ((c * c) / (a * a + b * b)))
        m = sqrt((d * d) / (a * a + b * b))

        res = []
        res.append([
            l[0] + b * m + node[0],
            l[1] - a * m + node[1]
        ])

        res.append([
            l[0] - b * m + node[0],
            l[1] + a * m + node[1]
        ])

        ball = [ball[0] + node[0], ball[1] + node[1]]

        if distance(ball, node) < dist - eps:
            return (min(res, key = lambda x: distance(x, ball)), True)
        else:
            return (min(res, key = lambda x: distance(x, node)), False)

    return None

def calculate_vector(v1, m1, v2, m2):
    pass
