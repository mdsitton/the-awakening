import sys

from gem import vector

# This is to make up for some missing functionality from GEM and fix some bugs
class Vector(vector.Vector):

    def clone(self):
        return Vector(self.size, data=self.vector[:]) # fix slight bug since vector contents are not copied

    def distance(self, other):
        return self.magnitude(self - other)

    def __eq__(self, vecB):
        if isinstance(vecB, Vector):
            for i in range(self.size):
                if self.vector[i] != vecB.vector[i]:
                    return False
            else:
                return True
        else:
            return NotImplemented

    def __ne__(self, vecB):
        if isinstance(vecB, Vector):
            for i in range(self.size):
                if self.vector[i] != vecB.vector[i]:
                    return True
            else:
                return False
        else:
            return NotImplemented

    def __truediv__(self, scalar):
        if isinstance(scalar, int) or isinstance(scalar, float):
            vecList = vector.vec_div(self.size, self.vector, scalar)
            return Vector(self.size, data=vecList)
        else:
            return NotImplemented


    @property
    def x(self):
        return self.vector[0]

    @x.setter
    def x(self, val):
        self.vector[0] = val

    @property
    def y(self):
        return self.vector[1]

    @y.setter
    def y(self, val):
        self.vector[1] = val

    @property
    def z(self):
        return self.vector[2]

    @z.setter
    def z(self, val):
        self.vector[2] = val

    @property
    def w(self):
        return self.vector[3]

    @w.setter
    def w(self, val):
        self.vector[3] = val

# monkey patch it
def patch():
    setattr(sys.modules['gem.vector'], 'Vector', Vector)

__all__ = [patch]
