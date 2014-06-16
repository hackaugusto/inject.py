inject.py
=========

Inject is a simple function that uses values from a dictionary as arguments for a function.

```python
>>> inject(lambda argument: argument, {'argument': 1})
1

>>> def positional(one, two): return one, two
>>> inject(positional, {'one': 1, 'two': 2})
(1, 2)
```

Extra arguments are ignored (the main difference from using
`function(**context)`)

```python
>>> positional(**{'one': 1, 'two': 2, 'three': 3})
Traceback (most recent call last):
...
TypeError: positional() got an unexpected keyword argument 'three'

>>> inject(positional, {'one': 1, 'two': 2, 'three': 3})
(1, 2)
```

Inject can pass *args and **kwargs to the function:

```python
>>> def varargs(*args): return args
>>> inject(varargs, {'args': [1, 3, 5], 'extra': None})
(1, 3, 5)

>>> def kwargs(**kwargs): return kwargs
>>> result = inject(kwargs, {'args': None, 'kwargs': {'a': [1,2], 'b': [5,7]}})
>>> result['a']
[1, 2]
>>> result['b']
[5, 7]
```
