from dataclasses import dataclass


@dataclass(frozen=True)
class Vec2i:
    x: int
    y: int

    def __add__(self, other):
        return Vec2i(self.x + other.x, self.y + other.y)


    def __sub__(self, other):
        return Vec2i(self.x - other.x, self.y - other.y)


    def __mul__(self, scalar: int):
        return Vec2i(self.x * scalar, self.y * scalar)


    def __floordiv__(self, scalar: int):
        return Vec2i(self.x // scalar, self.y // scalar)


    def __abs__(self):
        return Vec2i(abs(self.x), abs(self.y))


@dataclass
class Transform:
    cpos: Vec2i
    prev_cpos: Vec2i
    elevation: int