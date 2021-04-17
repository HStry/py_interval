import math
from typing import Any, Union
__all__ = ['Interval']

nan = float('nan')
inf = float('inf')
UNSET = object()

def isnan(val: Any) -> bool:
    "True if value is nan-like"
    try:
        return math.isnan(val)
    except TypeError:
        return (val != val)

def isinf(val: Any) -> bool:
    "True if value evaluates to infinity"
    try:
        return math.isinf(val)
    except TypeError:
        try:
            return (val * inf == val)
        except Exception:
            return False

def sign(val: Any) -> int:
    """Detects the sign of 'val'.
    Returns -1, 0, 1 for negative, zero-like, and positive values respectively.
    Will return 0 for nan.
    """
    if isnan(val):
        return 0
    if isinf(val):
        return (abs(val) == val) * 2 - 1
    
    zval = 0 * val
    return (val == zval) + 2 * (val > zval) - 1

def ispos(val: Any) -> bool:
    "True if value is positive"
    return sign(val) > 0

def isneg(val: Any) -> bool:
    "True if value is negative"
    return sign(val) < 0

def value_typetest(val: Any) -> bool:
    """Tests whether the provided value type has the required methods and
    properties for Interval"""
    # Maybe this is better done through abstract base classes, but 
    try:
        _ = isnan(val)
        _ = isinf(val)
        _ = sign(val)
        _ = val < val
        _ = val > val
        
        return True
    except Exception:
        return False

class Point(tuple):
    __nan = False
    __inf = False
    def __new__(cls, val: Any, offset: int=0) -> Point:
        
        offset = int(offset)
        if offset not in (-1, 0, 1):
            raise ValueError(f"Invalid offset '{offset}', not in (-1, 0, 1)")
        
        if isnan(val):
            self = super().__new__(cls, (nan, ))
            self.__val = val
            self.__nan = True
        
        elif isinf(val):
            if sign(val) == sign(offset):
                raise ValueError("Cannot offset beyond ±inf")
            
            self = super().__new__(cls, (3 + 2*sign(val) + offset, ))
            self.__val = val
            self.__inf = True
        
        else:
            self = super().__new__(cls, (3, val, offset))
        
        return self
    
    @classmethod
    def Left(cls, val: Any, incl: bool = True) -> Point:
        "shorthand constructor for left endpoint"
        return cls(val, int(not incl))
    
    @classmethod
    def Right(cls, val: Any, incl: bool = False) -> Point:
        "shorthand constructor for right endpoint"
        return cls(val, -int(not incl))
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self})"
    
    def __str__(self) -> str:
        return self.__format__('')
    
    def __format__(self, spec: str) -> str:
        div = ':'
        spec_options = {'sup':  ("\u207b", "\u207c", "\u207a"),
                        'base': ('-', '=', '+'),
                        'sub':  ("\u208b", "\u208c", "\u208a")}
        spec_default = 'sup'
        
        vspec, *(ospec, *_) = spec.rsplit(div, 1) + ['']
        if vspec in spec_options:
            vspec, ospec = '', vspec
        
        if not ospec:
            ospec = spec_default
        
        return f"{self.value:{vspec}}{spec_options[ospec][self.offset + 1]}"
    
    def __add__(self, other: Any) -> Point:
        return self.__class__(self.value + other, self.offset)
    
    def __sub__(self, other: Any) -> Point:
        return self.__class__(self.value - other, self.offset)
    
    def __mul__(self, other: Any) -> Point:
        return self.__class__(self.value * other, self.offset)
    
    def __truediv__(self, other: Any) -> Point:
        return self.__class__(self.value / other, self.offset)
    
    def __floordiv__(self, other: Any) -> Point:
        return self.__class__(self.value // other, self.offset)
    
    @property
    def value(self) -> Any:
        "returns the value"
        try:
            return self[1]
        except IndexError:
            return self.__val
    
    @property
    def offset(self) -> int:
        "returns the infinitessimal offset (-1, 0, 1) from the value"
        try:
            return self[2]
        except IndexError:
            if self.inf:
                return (None, 0, 1, None, -1, 0)[self[0]]
            return 0
    
    @property
    def nan(self) -> bool:
        "True if a value is a nan value"
        return self.__nan
    
    @property
    def inf(self) -> bool:
        "True if value is an infinite"
        return self.__inf


class Interval:
    __min    = Point(nan, 0)
    __max    = Point(nan, 0)
    __nan    = False
    __empty  = False
    __degen  = False
    __proper = False
    __bool   = True
    
    def __init__(self, v_min: Any=UNSET,
                       v_max: Any=UNSET,
                       endstate: int=UNSET, /) -> None:
        
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
    def __pts(cls, a: Point, b: Point) -> Interval:
        self = cls()
        del(self.__empty)
        self.__min = a
        self.__max = b
        self.__sanitize()
        return self
    
    def __sanitize(self) -> None:
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
    
    def __repr__(self) -> str:
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
    
    def __bool__(self) -> bool:
        "True if interval is degenerate or proper"
        return self.__bool
    
    def __contains__(self, other: Any) -> bool:
        "True if other value or interval is fully contained within interval"
        if not isinstance(other, self.__class__):
            other = self.__class__(other)
        
        return (self and other and
                self.min <= other.min and
                self.max >= other.max)
    
    def _overlap(self, other: Interval) -> bool:
        return (self and other and
                self.min <= other.max and
                self.max >= other.min)
    
    def _continuous(self, other: Interval) -> bool:
        return (self and other and
                self.max.value == other.min.value and
                bool(self.max.offset) != bool(other.min.offset))
    
    def __and__(self, other: Any) -> Interval:
        "Returns intersection of interval and other value or interval"
        if not isinstance(other, self.__class__):
            other = self.__class__(other)
        
        if self and other:
            return self.__pts(max(self.min, other.min),
                              min(self.max, other.max))
        
        return self.__class__()
        
    def __or__(self, other: Any) -> Interval:
        "Returns union of interval and other value or interval"
        if not isinstance(other, self.__class__):
            other = self.__class__(other)
        
        if (self and other and
            (self._overlap(other) or
             self._continuous(other) or
             other._continuous(self))):
            return self.__pts(min(self.min, other.min),
                              max(self.max, other.max))
        
        return self.__class__()
    
    def overlap(self, other: Any) -> bool:
        "True if overlap exists between interval and other value or interval"
        if not isinstance(other, self.__class__):
            other = self.__class__(other)
        return self._overlap(other)
    
    def continuous(self, other: Any) -> int:
        """Checks whether interval is exactly continuous with other interval or
        value, and in which orientation."""
        if not isinstance(other, self.__class__):
            other = self.__class__(other)
        
        return int(self._continuous(other)) or (-1 * other._continuous(self))
    
    @property
    def min(self) -> Point:
        "Returns Point instance representing the lower interval endpoint"
        return self.__min
    @property
    def max(self) -> Point:
        "Returns Point instance representing the upper interval endpoint"
        return self.__max
    
    @property
    def nan(self) -> bool:
        "True if interval constructed with a nan value"
        return self.__nan
    @property
    def empty(self) -> bool:
        "True if interval is empty"
        return self.__empty
    @property
    def degenerate(self) -> bool:
        "True if interval contains exactly one value"
        return self.__degen
    @property
    def proper(self) -> bool:
        "True if interval spans a range"
        return self.__proper

