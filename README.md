# pynterval

A small python module to handle numeric intervals

```sh
pip install pynterval
```

```python
>>> from pynterval import Interval
>>> 
>>> my_interval = Interval(0, 5)
>>> vals = (0, 4, 5, Interval(2.1, 3.4), Interval(0, 5), Interval(0, 5, 3))
>>> [val in my_interval for val in vals]
[True, True, False, True, True, False]
>>> 
>>> Interval()
Interval: {}
>>> Interval().empty
True
>>> Interval(4)
Interval: {4}
```

*** Works also with many other comparable objects ***
```python
>>> from pynterval import Interval
>>> import pint
>>> ureg = pint.UnitRegistry()
>>> 
>>> my_interval = Interval(0 * ureg.mm, 15 * ureg.cm)
>>> (1 * ureg.inch) in my_interval
True
>>> 
>>> my_rightunbounded_interval = Interval(100 * ureg.mm, float('inf'))
>>> (5 * ureg.cm) in my_rightunbounded_interval
False
>>> (5 * ureg.lightyear) in my_rightunbounded_interval
True
```
