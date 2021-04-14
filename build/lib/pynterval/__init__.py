import math

__all__ = ['Interval']

nan = float('nan')
inf = float('inf')
UNSET = object()

class Point(tuple):
    def __new__(cls, val, offset):
        
        if math.isnan(val):
            self = super().__new__(cls, (nan, ))
            self.__val = val
        
        elif math.isinf(val):
            self = super().__new__(cls, (1 + (abs(val) == val) * 4 + offset, ))
            self.__val = val
        
        else:
            self = super().__new__(cls, (3, val, offset))
        
        return self
    
    @classmethod
    def Left(cls, val, incl: bool = True):
        if math.isinf(val) and abs(val) == val and not incl:
            raise ValueError(f"impossible offset for value '{val}'")
        return cls(val, int(not incl))
    
    @classmethod
    def Right(cls, val, incl: bool = False):
        if math.isinf(val) and abs(val) != val and not incl:
            raise ValueError(f"impossible offset for value '{val}'")
        return cls(val, -int(not incl))
    
    @property
    def value(self):
        try:
            return self[1]
        except IndexError:
            return self.__val
    
    def offset(self):
        try:
            return self[2]
        except IndexError:
            return 0
    
    @property
    def nan(self):
        return math.isnan(self[0])


class Interval:
    __min    = Point(nan, 0)
    __max    = Point(nan, 0)
    __nan    = False
    __empty  = False
    __degen  = False
    __proper = False
    __bool   = True
    
    def __init__(self, v_min=UNSET, v_max=UNSET, endstate=UNSET, /):
        
        if v_min is UNSET:
            self.__empty = True
            return
        
        if v_max is UNSET:
            self.__degen = True
            self.__min = self.__max = Point(v_min, 0)
            return
        
        if endstate is UNSET:
            endstate = 2
        
        self.__min = Point.Left(v_min, bool(endstate & 2))
        self.__max = Point.Right(v_max, bool(endstate & 1))
        self.__sanitize()
    
    @classmethod
    def __pts(cls, a, b):
        self = cls()
        del(self.__empty)
        self.__min = a
        self.__max = b
        self.__sanitize()
        return self
    
    def __sanitize(self):
        if self.__min.nan or self.__max.nan:
            del(self.__min, self.__max)
            self.__nan  = True
            self.__bool = False
        
        elif self.__min > self.__max:
            del(self.__min, self.__max)
            self.__empty = True
            self.__bool  = False
        
        elif self.__min == self.__max:
            self.__degen = True
        
        else:
            self.__proper = True
    
    def __repr__(self):
        if self.nan:
            return f"{self.__class__.__name__}(nan)"
        if self.empty:
            return f"{self.__class__.__name__}: {{}}"
        if self.degenerate:
            return f"{self.__class__.__name__}: {{{self.min.value}}}"
        return (f"{self.__class__.__name__}: "
                f"{'[('[bool(self.min.offset)]}"
                f"{self.min.value}, {self.max.value}"
                f"{'])'[bool(self.max.offset)]}")
    
    def __bool__(self):
        return self.__bool
    
    def __contains__(self, other):
        if not isinstance(other, self.__class__):
            other = self.__class__(other)
        
        return (self and other and
                self.min <= other.min and
                self.max >= other.max)
    
    def __overlap(self, other):
        return (self and other and
                self.min <= other.max and
                self.max >= other.min)
    
    def __continuous(self, other):
        return (self and other and
                self.max.value == other.min.value and
                bool(self.max.offset) != bool(other.min.offset))
    
    def __and__(self, other):
        if not isinstance(other, self.__class__):
            other = self.__class__(other)
        
        if self and other:
            return self.__pts(max(self.min, other.min),
                              min(self.max, other.max))
        
        return self.__class__()
        
    def __or__(self, other):
        if not isinstance(other, self.__class__):
            other = self.__class__(other)
        
        if (self and other and
            (self.__overlap(other) or
             self.__continuous(other) or
             other.__continuous(self))):
            return self.__pts(min(self.min, other.min),
                              max(self.max, other.max))
        
        return self.__class__()
    
    def overlap(self, other):
        if not isinstance(other, self.__class__):
            other = self.__class__(other)
        return self.__overlap(other)
    
    def continuous(self, other):
        if not isinstance(other, self.__class__):
            other = self.__class__(other)
        return self.__continuous(other)
    
    @property
    def min(self):
        return self.__min
    @property
    def max(self):
        return self.__max
    
    @property
    def nan(self):
        return self.__nan
    @property
    def empty(self):
        return self.__empty
    @property
    def degenerate(self):
        return self.__degen
    @property
    def proper(self):
        return self.__proper

