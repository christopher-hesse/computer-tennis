class Color:
    def __init__(self, r, g, b, a=1.0):
        self.r = r
        self.g = g
        self.b = b
        self.a = a


class Vec2:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __mul__(self, other):
        if isinstance(other, float):
            return Vec2(x=self.x * other, y=self.y * other)
        else:
            raise Exception("invalid operation")

    def __add__(self, other):
        if isinstance(other, Vec2):
            return Vec2(x=self.x + other.x, y=self.y + other.y)
        else:
            raise Exception("invalid operation")
